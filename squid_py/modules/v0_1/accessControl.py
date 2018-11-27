from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.utils import get_contract_abi_and_address, hexstr_to_bytes, get_fingerprint_by_name
from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled,
    get_eth_contracts)
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.utils import build_condition_key


def grantAccess(web3, contract_path, account, service_agreement_id, service_definition,
                *args, **kwargs):
    """ Checks if grantAccess condition has been fulfilled and if not calls
        AccessConditions.grantAccess smart contract function.
    """
    access_conditions, contract, abi, access_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        'grantAccess',
    )
    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement_address = get_contract_abi_and_address(web3, contract_path, contract_name)[1]
    if is_condition_fulfilled(web3, contract_path, service_definition['slaTemplateId'],
                              service_agreement_id, service_agreement_address,
                              access_conditions.address, abi, 'grantAccess'):
        return

    name_to_parameter = {param['name']: param for param in access_condition_definition['parameters']}
    asset_id = name_to_parameter['assetId']['value']
    document_key_id = name_to_parameter['documentKeyId']['value']
    transact = {'from': account.address, 'gas': DEFAULT_GAS_LIMIT}

    #######################
    sa_contracts = get_eth_contracts(web3, contract_path, service_agreement_address)
    fingerprint = hexstr_to_bytes(web3, get_fingerprint_by_name(abi, 'grantAccess'))
    value_hash = web3.soliditySha3(['bytes32', 'bytes32'], [asset_id, asset_id])
    cond_key = access_condition_definition['conditionKey']
    k = build_condition_key(web3, access_conditions.address, fingerprint, service_definition['slaTemplateId'])
    assert k == cond_key
    cond_inst_1 = web3.soliditySha3(['bytes32', 'bytes32'], [cond_key, value_hash])
    cond_inst = sa_contracts[0].getConditionInstance(service_agreement_id, access_conditions.address, fingerprint)
    assert cond_inst == cond_inst_1
    valid_access_controller = sa_contracts[0].isValidControllerHandlerFunc(service_agreement_id, fingerprint, value_hash, access_conditions.address)
    print('valid controller: ', valid_access_controller)
    assert valid_access_controller, 'something not right.'
    ##########################

    try:
        if account.password:
            web3.personal.unlockAccount(account.address, account.password)

        tx_hash = access_conditions.grantAccess(service_agreement_id, asset_id, asset_id, transact=transact)
    except Exception as e:
        print('error: ', e)
        raise

    web3.eth.waitForTransactionReceipt(tx_hash)
    receipt = web3.eth.getTransactionReceipt(tx_hash)
    event = contract.events.AccessGranted().processReceipt(receipt)
    print('AccessGranted event: ', event)


def consumeAsset(web3, contract_path, account, service_agreement_id, service_definition,
                 consume_callback, *args, **kwargs):

    if consume_callback:
        result = consume_callback(
            service_agreement_id, service_definition['id'],
            service_definition[ServiceAgreement.SERVICE_DEFINITION_ID_KEY], account
        )
        print('done consuming asset, result: ', result)

    else:
        raise ValueError('Consume asset triggered but the consume callback is not set.')
