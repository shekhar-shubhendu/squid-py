import os, json, time
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract
from threading import Thread
from collections import namedtuple
from ocean_web3.config_parser import load_config_section, get_contracts_path
from ocean_web3.constants import OceanContracts

Signature = namedtuple('Signature', ('v', 'r', 's'))


def convert_to_bytes(data):
    return Web3.toBytes(text=data)

def convert_to_string(data):
    return Web3.toHex(data)

def convert_to_text(data):
    return Web3.toText(data)


class OceanContractsWrapper(object):

    def __init__(self, host=None, port=None, config_path=None):

        try:
            config_path = os.getenv('CONFIG_FILE') if not config_path else config_path
            self.config = load_config_section(config_path, OceanContracts.KEEPER_CONTRACTS)
        except Exception:
            self.config = None
        self.host = self.get_value('keeper.host', 'KEEPER_HOST', host)
        self.port = self.get_value('keeper.port', 'KEEPER_PORT', port)
        self.web3 = OceanContractsWrapper.connect_web3(self.host, self.port)
        self.account = self.get_value('provider.account', 'PROVIDER_ACCOUNT', self.web3.eth.accounts[0])
        self.contracts_abis_path = get_contracts_path(self.config)
        self.contracts = {}
        self.default_contract_address_map = {
            OceanContracts.OMKT: self.get_value('market.address', 'MARKET_ADDRESS', None),
            OceanContracts.OACL: self.get_value('auth.address', 'AUTH_ADDRESS', None),
            OceanContracts.OTKN: self.get_value('token.address', 'TOKEN_ADDRESS', None)
        }
        self.network = self.get_value('keeper.network', 'KEEPER_NETWORK', 'development')

    def get_value(self, value, env_var, default):
        if os.getenv(env_var) is not None:
            return os.getenv(env_var)
        elif self.config is not None and value in self.config:
            return self.config[value]
        else:
            return default

    def init_contracts(self, contracts_folder=None, contracts_addresses=None):
        contracts_abis_path = contracts_folder if contracts_folder else self.contracts_abis_path
        contract_address_map = contracts_addresses if contracts_addresses else self.default_contract_address_map
        for contract_name, address in contract_address_map.items():
            contract_abi_file = os.path.join(contracts_abis_path, contract_name + '.' + self.network + '.json')
            self.contracts[contract_name] = self.get_contract_instances(contract_abi_file, address)

    @staticmethod
    def connect_web3(host, port='8545'):
        return Web3(HTTPProvider("%s:%s" % (host, port)))

    def get_contract_instances(self, contract_file, contract_address):
        with open(contract_file, 'r') as abi_definition:
            abi = json.load(abi_definition)
            if not contract_address and 'address' in abi:
                contract_address = abi['address']
                print('Extracted %s contract address ' % contract_file, contract_address)
            concise_cont = self.web3.eth.contract(
                address=self.web3.toChecksumAddress(contract_address),
                abi=abi['abi'],
                ContractFactoryClass=ConciseContract)
            contract = self.web3.eth.contract(
                address=self.web3.toChecksumAddress(contract_address),
                abi=abi['abi'])
            return concise_cont, contract

    def get_tx_receipt(self, tx_hash):
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

    def install_filter(self, contract_name, event_name, fromBlock=0, toBlock='latest', filters=None):
        contract_instance = self.contracts[contract_name][1]
        event = getattr(contract_instance.events, event_name)
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
