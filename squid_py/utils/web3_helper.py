import logging
from squid_py.config_parser import get_contracts_path, get_value
import json
from web3 import Web3
from web3.contract import ConciseContract
from collections import namedtuple
from threading import Thread
import time

Signature = namedtuple('Signature', ('v', 'r', 's'))


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
            return concise_cont, contract, contract_address

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
        """Validate the address provided."""
        return self.web3.toChecksumAddress(address)

    def get_tx_receipt(self, tx_hash):
        """Get the receipt of the tx."""
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        return self.web3.eth.getTransactionReceipt(tx_hash)

    def watch_event(self, contract_name, event_name, callback, interval, fromBlock=0, toBlock='latest', filters=None, ):
        event_filter = self.install_filter(
            contract_name, event_name, fromBlock, toBlock, filters
        )
        event_filter.poll_interval = interval
        Thread(
            target=self.watcher,
            args=(event_filter, callback),
            daemon=True,
        ).start()
        return event_filter

    @staticmethod
    def watcher(event_filter, callback):
        while True:
            try:
                events = event_filter.get_all_entries()
            except ValueError as err:
                # ignore error, but log it
                print('Got error grabbing keeper events: ', str(err))
                events = []

            for event in events:
                callback(event)
                # time.sleep(0.1)

            # always take a rest
            time.sleep(0.1)

    def install_filter(self, contract, event_name, fromBlock=0, toBlock='latest', filters=None):
        # contract_instance = self.contracts[contract_name][1]
        event = getattr(contract.events, event_name)
        event_filter = event.createFilter(
            fromBlock=fromBlock, toBlock=toBlock, argument_filters=filters
        )
        return event_filter

    def to_32byte_hex(self, val):
        return self.web3.toBytes(val).rjust(32, b'\0')

    def split_signature(self, signature):
        v = self.web3.toInt(signature[-1])
        r = self.to_32byte_hex(int.from_bytes(signature[:32], 'big'))
        s = self.to_32byte_hex(int.from_bytes(signature[32:64], 'big'))
        if v != 27 and v != 28:
            v = 27 + v % 2
        return Signature(v, r, s)


def convert_to_bytes(data):
    return Web3.toBytes(text=data)


def convert_to_string(data):
    return Web3.toHex(data)


def convert_to_text(data):
    return Web3.toText(data)
