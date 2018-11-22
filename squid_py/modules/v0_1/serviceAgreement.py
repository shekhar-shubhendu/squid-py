from web3.contract import ConciseContract

from squid_py.keeper.utils import get_contract_abi_and_address


def fulfillAgreement(web3, contract_path, account, service_agreement_id,
                     service_definition, *args, **kwargs):
    """ Checks if serviceAgreement has been fulfilled and if not calls
        ServiceAgreement.fulfillAgreement smart contract function.
    """
    contract_name = service_definition['serviceAgreementContract']['contractName']
    abi, service_agreement_address = get_contract_abi_and_address(web3, contract_path, contract_name)
    service_agreement = web3.eth.contract(address=service_agreement_address, abi=abi, ContractFactoryClass=ConciseContract)
    service_agreement.fulfillAgreement(
        service_agreement_id,
        transact={'from': account},
    )


def terminateAgreement(web3, contract_path, account, service_agreement_id,
                       service_definition, *args, **kwargs):
    fulfillAgreement(web3, contract_path, account, service_agreement_id, service_definition, *args, **kwargs)
