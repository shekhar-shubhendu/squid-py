import logging
from squid_py.config_parser import get_contracts_path, get_value
import json, os
from web3.contract import ConciseContract


class Web3Helper(object):
    def __init__(self, web3, config=None):
        self.web3 = web3
        self.config = config

    def load(self, contract_file, name):
        """Retrieve a tuple with the concise contract and the contract definition."""
        contract_address = get_value(self.config, name + '.address', name.upper() + '_ADDRESS', None)
        with open(get_contracts_path(self.config) + '/' + contract_file + '.json', 'r') as abi_definition:
            abi = json.load(abi_definition)
            concise_cont = self.web3.eth.contract(
                address=self.web3.toChecksumAddress(contract_address),
                abi=abi['abi'],
                ContractFactoryClass=ConciseContract)
            contract = self.web3.eth.contract(
                address=self.web3.toChecksumAddress(contract_address),
                abi=abi['abi'])
            return concise_cont, contract

    def get_accounts(self):
        """Return the accounts in the current network."""
        try:
            return self.web3.eth.accounts
        except Exception as e:
            logging.error("Error obtaining accounts")
            raise Exception(e)

    def get_network_name(self):
        """Give the network name."""
        network_id = self.web3.version.network
        switcher = {
            1: 'Main',
            2: 'orden',
            3: 'Ropsten',
            4: 'Rinkeby',
            42: 'Kovan',
        }
        return switcher.get(network_id, 'development')

    def sign(self, account_address, message):
        return self.web3.eth.sign(account_address, message)

    def to_checksum_address(self, address):
        return self.web3.toChecksumAddress(address)

    def get_tx_receipt(self, tx_hash):
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        return self.web3.eth.getTransactionReceipt(tx_hash)

