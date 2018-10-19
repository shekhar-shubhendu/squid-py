"""
    Keeper Contract Base

    All keeper contract inherit from this base class
"""
import os
import logging
import json
from web3 import Web3
from web3.contract import ConciseContract
# from ..utils.web3_helper_module import convert_to_bytes, convert_to_string, convert_to_text

class ContractBase(object):
    """
    Base class for all contract objects.
    """
    def __init__(self, web3, contract_name, name, contract_path, address):
        self.web3 = web3

        # Load the contract objects
        contract = self.load(contract_name, name, contract_path, address)
        self.contract_concise = contract[0]
        self.contract = contract[1]

        self.address = self.to_checksum_address(contract[2])
        self.name = name

        logging.debug("Loaded {}".format(self))

    def load(self, contract_file, name, contract_path, contract_address):
        """Retrieve a tuple with the concise contract and the contract definition."""
        contract_filename = os.path.join(contract_path, "{}.json".format(contract_file))
        try:
            valid_address = self.web3.toChecksumAddress(contract_address)
        except ValueError as e:
            raise OceanInvalidContractAddress("Invalid contract address for keeper contract '{}'".format(name))
        except Exception as e:
            raise e

        with open(contract_filename, 'r') as abi_definition:
            abi = json.load(abi_definition)
            concise_cont = self.web3.eth.contract(
                address=valid_address,
                abi=abi['abi'],
                ContractFactoryClass=ConciseContract)
            contract = self.web3.eth.contract(
                address=valid_address,
                abi=abi['abi'])

        return concise_cont, contract, contract_address

    def to_checksum_address(self, address):
        """Validate the address provided."""
        return self.web3.toChecksumAddress(address)

    def get_tx_receipt(self, tx_hash):
        """Get the receipt of a tx."""
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        return self.web3.eth.getTransactionReceipt(tx_hash)

    def to_32byte_hex(self, val):
        return self.web3.toBytes(val).rjust(32, b'\0')

    def __str__(self):
        return "{} at {}".format(self.name, self.address)

    def convert_to_bytes(self, data):
        return Web3.toBytes(text=data)

    def convert_to_string(self,data):
        return Web3.toHex(data)

    def convert_to_text(self, data):
        return Web3.toText(data)