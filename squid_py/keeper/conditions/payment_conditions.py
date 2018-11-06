from web3.contract import ConciseContract

from squid_py.keeper.utils import get_contract_by_name
from squid_py.utils import network_name


class PaymentConditions:

    def __init__(self, web3, contract_path):
        self.web3 = web3
        self.contract_path = contract_path

        contract_definition = get_contract_by_name(
            self.contract_path,
            network_name(self.web3),
            'PaymentConditions',
        )

        self.address = contract_definition['address']
        self.abi = contract_definition['abi']

        self.contract_concise = self.web3.eth.contract(
            address=self.address,
            abi=self.abi,
            ContractFactoryClass=ConciseContract,
        )
        self.contract = self.web3.eth.contract(
            address=self.address,
            abi=self.abi,
        )
