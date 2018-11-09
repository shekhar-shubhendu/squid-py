from web3.contract import ConciseContract

from squid_py.keeper.utils import (
    get_contract_abi_by_address,
    get_fingerprint_by_name,
    hexstr_to_bytes,
)
from squid_py.modules.v0_1.exceptions import InvalidModule


def lockPayment(web3, contract_path, account, service_agreement_id, service_definition,
                *args, **kwargs):
    """ Calls PaymentConditions.lockPayment smart contract function. The account is supposed
        to have sufficient amount of approved Ocean tokens.
    """
    payment_conditions, abi, payment_condition_definition = _get_payment_conditions_data(
        web3,
        contract_path,
        service_definition,
    )

    service_agreement = _get_service_agreement_contract(web3, contract_path, service_definition)
    status = service_agreement.getConditionStatus(
        service_agreement_id.encode(),
        _get_lock_payment_condition_key(web3, service_definition, payment_conditions.address, abi),
    )
    if status:
        # condition has been fulfilled already
        return

    parameters = payment_condition_definition['parameters']
    payment_conditions.lockPayment(
        service_agreement_id.encode(),
        parameters['did'].encode(),
        parameters['price'],
        transact={'from': account},
    )


def _get_payment_conditions_data(web3, contract_path, service_definition):
    payment_condition = None
    for condition in service_definition['conditions']:
        if condition['conditionKey'].get('functionName') == 'lockPayment':
            payment_condition = condition
            break

    if payment_condition is None:
        raise InvalidModule('Failed to find the lockPayment condition in the service definition')

    address = payment_condition['conditionKey']['contractAddress']
    fingerprint = payment_condition['conditionKey']['fingerprint']

    abi = get_contract_abi_by_address(contract_path, address)
    if get_fingerprint_by_name(abi, 'lockPayment') != fingerprint:
        raise InvalidModule('The lockPayment fingerprint specified in the service definition ' +
                            'does not match the known fingerprint')

    return web3.eth.contract(
        address=address,
        abi=abi,
        ContractFactoryClass=ConciseContract,
    ), abi, payment_condition


def _get_service_agreement_contract(web3, contract_path, service_definition):
    address = service_definition['serviceAgreementContract']['address']
    abi = get_contract_abi_by_address(contract_path, address)

    return web3.eth.contract(
        address=address,
        abi=abi,
        ContractFactoryClass=ConciseContract,
    )


def _get_lock_payment_condition_key(web3, service_definition, address, abi):
    return web3.soliditySha3(
        ['bytes32', 'address', 'bytes4'],
        [
            service_definition['templateId'].encode(),
            address,
            hexstr_to_bytes(web3, get_fingerprint_by_name(abi, 'lockPayment')),
        ]
    ).hex()
