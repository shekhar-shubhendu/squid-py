from squid_py.keeper.utils import get_contract_by_name
from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled,
)
from squid_py.utils import network_name


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
    contract_json = get_contract_by_name(contract_path, network_name(web3), contract_name)
    service_agreement_address = contract_json['address']
    if is_condition_fulfilled(web3, contract_path, service_definition['templateId'],
                              service_agreement_id, service_agreement_address,
                              access_conditions.address, abi, 'grantAccess'):
        return

    parameters = access_condition_definition['parameters']
    name_to_parameter = {param['name']: param for param in parameters}
    access_conditions.grantAccess(
        service_agreement_id.encode(),
        name_to_parameter['did']['value'].encode(),
        name_to_parameter['did']['value'].encode(),
        transact={'from': account},
    )
