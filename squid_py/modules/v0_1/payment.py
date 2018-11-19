from squid_py.keeper.utils import get_contract_by_name
from squid_py.modules.v0_1.utils import (
    get_condition_contract_data,
    is_condition_fulfilled,
)
from squid_py.utils import network_name


def lockPayment(web3, contract_path, account, service_agreement_id, service_definition,
                *args, **kwargs):
    """ Checks if the lockPayment condition has been fulfilled and if not calls
        PaymentConditions.lockPayment smart contract function.

        The account is supposed to have sufficient amount of approved Ocean tokens.
    """
    payment_conditions, abi, payment_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        'lockPayment',
    )

    contract_name = service_definition['serviceAgreementContract']['contractName']
    contract_json = get_contract_by_name(contract_path, network_name(web3), contract_name)
    service_agreement_address = contract_json['address']
    if is_condition_fulfilled(web3, contract_path, service_definition['templateId'],
                              service_agreement_id, service_agreement_address,
                              payment_conditions.address, abi, 'lockPayment'):
        return

    parameters = payment_condition_definition['parameters']
    name_to_parameter = {param['name']: param for param in parameters}
    payment_conditions.lockPayment(
        service_agreement_id.encode(),
        name_to_parameter['did']['value'].encode(),
        name_to_parameter['price']['value'],
        transact={'from': account},
    )


def releasePayment(web3, contract_path, account, service_agreement_id, service_definition,
                   *args, **kwargs):
    """ Checks if the releasePayment condition has been fulfilled and if not calls
        PaymentConditions.releasePayment smart contract function.
    """
    payment_conditions, abi, payment_condition_definition = get_condition_contract_data(
        web3,
        contract_path,
        service_definition,
        'releasePayment',
    )

    contract_name = service_definition['serviceAgreementContract']['contractName']
    contract_json = get_contract_by_name(contract_path, network_name(web3), contract_name)
    service_agreement_address = contract_json['address']
    if is_condition_fulfilled(web3, contract_path, service_definition['templateId'],
                              service_agreement_id, service_agreement_address,
                              payment_conditions.address, abi, 'releasePayment'):
        return

    parameters = payment_condition_definition['parameters']
    name_to_parameter = {param['name']: param for param in parameters}
    payment_conditions.releasePayment(
        service_agreement_id.encode(),
        name_to_parameter['did']['value'].encode(),
        name_to_parameter['price']['value'],
        transact={'from': account},
    )
