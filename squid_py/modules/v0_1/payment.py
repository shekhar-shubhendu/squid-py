from web3.contract import ConciseContract

from squid_py.keeper.utils import get_contract_abi_by_address, get_fingerprint_by_name
from squid_py.modules.v0_1.exceptions import InvalidModule


def lockPayment(web3, contract_path, account, service_agreement_id, service_definition,
                *args, **kwargs):
    """ Calls PaymentConditions.lockPayment smart contract function. The account is supposed
        to have sufficient amount of approved Ocean tokens.
    """
    payment_condition = None
    for condition in service_definition['conditions']:
        if condition['conditionKey'].get('functionName') == 'lockPayment':
            payment_condition = condition
            break

    if payment_condition is None:
        raise InvalidModule('Failed to find the lockPayment condition in the function definition')

    address = payment_condition['conditionKey']['contractAddress']
    fingerprint = payment_condition['conditionKey']['fingerprint']

    abi = get_contract_abi_by_address(contract_path, address)
    if get_fingerprint_by_name(abi, 'lockPayment') != fingerprint:
        raise InvalidModule('The lockPayment fingerprint specified in the service definition ' +
                            'does not match the known fingerprint')

    payment_conditions = web3.eth.contract(
        address=address,
        abi=abi,
        ContractFactoryClass=ConciseContract,
    )

    parameters = payment_condition['parameters']
    payment_conditions.lockPayment(
        service_agreement_id.encode(),
        parameters['did'].encode(),
        parameters['price'],
        transact={'from': account},
    )
