from squid_py.keeper.utils import get_contract_abi_and_address
from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled,
)
from squid_py.service_agreement.service_agreement import ServiceAgreement


def grantAccess(web3, contract_path, account, service_agreement_id, service_definition,
                *args, **kwargs):
    """ Checks if grantAccess condition has been fulfilled and if not calls
        AccessConditions.grantAccess smart contract function.
    """
    access_conditions, abi, access_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        'grantAccess',
    )
    contract_name = service_definition['serviceAgreementContract']['contractName']
    service_agreement_address = get_contract_abi_and_address(web3, contract_path, contract_name)[1]
    if is_condition_fulfilled(web3, contract_path, service_definition['templateId'],
                              service_agreement_id, service_agreement_address,
                              access_conditions.address, abi, 'grantAccess'):
        return

    parameters = access_condition_definition['parameters']
    name_to_parameter = {param['name']: param for param in parameters}
    access_conditions.grantAccess(
        service_agreement_id,
        name_to_parameter['assetId']['value'],
        name_to_parameter['assetId']['value'],
        transact={'from': account},
    )


def consumeAsset(web3, contract_path, account, service_agreement_id, service_definition,
                 consume_callback, *args, **kwargs):

    if consume_callback:
        consume_callback(
            service_agreement_id, service_definition['id'],
            service_definition[ServiceAgreement.SERVICE_DEFINITION_ID_KEY], account
        )
        return
