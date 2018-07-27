import os
import json
import time, site
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract
from threading import Thread
from web3py_wrapper.config_parser import load_config_section, KEEPER_CONTRACTS, get_contracts_path


config_file = 'config.ini'
conf = load_config_section(config_file, KEEPER_CONTRACTS)


def convert_to_bytes(data):
    return Web3.toBytes(text=data)


def convert_to_string(data):
    return Web3.toHex(data)


class OceanContracts(object):

    def __init__(self, host=conf['keeper.host'], port=conf['keeper.port'], account=None):
        self.host = host
        self.port = port
        self.web3 = OceanContracts.connect_web3(self.host, self.port)
        self.account = self.web3.eth.accounts[0] if account is None else account
        self.contracts_abis_path = get_contracts_path(conf)
        self.concise_contracts = {}
        self.contracts = {}

    def init_contracts(self, market_address=conf['market.address'], auth_address=conf['auth.address'],
                       token_address=conf['token.address']):
        # TODO Improve load of contracts
        for contract_name in os.listdir(self.contracts_abis_path):
            if contract_name == 'Market.json':
                self.concise_contracts[contract_name] = self.get_contract_instance(
                    os.path.join(self.contracts_abis_path, contract_name), market_address, True)
                self.contracts[contract_name] = self.get_contract_instance(
                    os.path.join(self.contracts_abis_path, contract_name), market_address, False)
            elif contract_name == 'OceanToken.json':
                self.concise_contracts[contract_name] = self.get_contract_instance(
                    os.path.join(self.contracts_abis_path, contract_name), token_address, True)
                self.contracts[contract_name] = self.get_contract_instance(
                    os.path.join(self.contracts_abis_path, contract_name), token_address, False)
            else:
                self.concise_contracts[contract_name] = self.get_contract_instance(
                    os.path.join(self.contracts_abis_path, contract_name), auth_address, True)
                self.contracts[contract_name] = self.get_contract_instance(
                    os.path.join(self.contracts_abis_path, contract_name), auth_address, False)

    @staticmethod
    def connect_web3(host, port='8545'):
        return Web3(HTTPProvider("http://%s:%s" % (host, port)))

    def get_contract_instance(self, contract_file, contract_address, concise=False):
        with open(contract_file, 'r') as abi_definition:
            abi = json.load(abi_definition)
            if concise:
                return self.web3.eth.contract(
                    address=self.web3.toChecksumAddress(contract_address),
                    abi=abi['abi'],
                    ContractFactoryClass=ConciseContract)
            else:
                return self.web3.eth.contract(
                    address=self.web3.toChecksumAddress(contract_address),
                    abi=abi['abi'])

    def get_tx_receipt(self, tx_hash):
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        return self.web3.eth.getTransactionReceipt(tx_hash)

    def watch_event(self, contract_name, event_name, callback, interval, fromBlock=0, toBlock='latest', filters=None, ):
        event_filter = self.install_filter(
            contract_name, event_name, fromBlock, toBlock, filters
        )
        event_filter.poll_interval = 500
        Thread(
            target=self.watcher,
            args=(event_filter, callback, interval),
            daemon=True,
        ).start()
        return event_filter

    def watcher(self, event_filter, callback, interval):
        while True:
            for event in event_filter.get_all_entries():
                callback(event)
                time.sleep(interval)

    def install_filter(self, contract_name, event_name, fromBlock=0, toBlock='latest', filters=None):
        contract_instance = self.contracts[contract_name + ".json"]
        event = getattr(contract_instance.events, event_name)
        eventFilter = event.createFilter(
            fromBlock=fromBlock, toBlock=toBlock, argument_filters=filters
        )
        return eventFilter
