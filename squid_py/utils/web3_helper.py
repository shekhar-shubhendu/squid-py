import json
import logging
import os.path
import time
from collections import namedtuple
from threading import Thread

from web3.contract import ConciseContract

from squid_py.exceptions import (
    OceanInvalidContractAddress,
)

Signature = namedtuple('Signature', ('v', 'r', 's'))


class Web3Helper(object):
    def __init__(self, web3):
        self._web3 = web3

    # def load(self, contract_file, name, contract_path, contract_address):
    #     """Retrieve a tuple with the concise contract and the contract definition."""
    #     contract_filename = os.path.join(contract_path, "{}.json".format(contract_file))
    #     try:
    #         valid_address = self._web3.toChecksumAddress(contract_address)
    #     except ValueError as e:
    #         raise OceanInvalidContractAddress("Invalid contract address for keeper contract '{}'".format(name))
    #     except Exception as e:
    #         raise e
    #
    #     with open(contract_filename, 'r') as abi_definition:
    #         abi = json.load(abi_definition)
    #         concise_cont = self._web3.eth.contract(
    #             address=valid_address,
    #             abi=abi['abi'],
    #             ContractFactoryClass=ConciseContract)
    #         contract = self._web3.eth.contract(
    #             address=valid_address,
    #             abi=abi['abi'])
    #         return concise_cont, contract, contract_address

    def sign(self, account_address, message):
        return self._web3.eth.sign(account_address, message)

    # def to_checksum_address(self, address):
    #     """Validate the address provided."""
    #     return self._web3.toChecksumAddress(address)

    def get_balance(self, account_address, block_identifier):
        return self._web3.eth.getBalance(account_address, block_identifier)



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

    def install_filter(self, contract, event_name, fromBlock=0, toBlock='latest', filters=None):
        # contract_instance = self.contracts[contract_name][1]
        event = getattr(contract.events, event_name)
        event_filter = event.createFilter(
            fromBlock=fromBlock, toBlock=toBlock, argument_filters=filters
        )
        return event_filter


    def split_signature(self, signature):
        v = self._web3.toInt(signature[-1])
        r = self.to_32byte_hex(int.from_bytes(signature[:32], 'big'))
        s = self.to_32byte_hex(int.from_bytes(signature[32:64], 'big'))
        if v != 27 and v != 28:
            v = 27 + v % 2
        return Signature(v, r, s)

    # properties

    @property
    def accounts(self):
        """Return the accounts in the current network."""
        try:
            return self._web3.eth.accounts
        except Exception as e:
            logging.error("Error obtaining accounts")
            raise Exception(e)

    @property
    def web3(self):
        return self._web3

    @property
    def network_name(self):
        """Give the network name."""
        network_id = self._web3.version.network
        switcher = {
            1: 'Main',
            2: 'orden',
            3: 'Ropsten',
            4: 'Rinkeby',
            42: 'Kovan',
        }
        return switcher.get(network_id, 'development')

    # static methods
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
