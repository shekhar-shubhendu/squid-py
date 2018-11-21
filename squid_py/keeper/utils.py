import json
import os

from squid_py.utils import get_network_name


def get_contract_abi_by_address(contract_path, address):
    contract_tree = os.walk(contract_path)
    address = address.lower()
    while True:
        dirname, _, files = next(contract_tree)
        for entry in files:
            with open(os.path.join(dirname, entry)) as f:
                try:
                    definition = json.loads(f.read())
                except Exception:
                    continue

                if address != definition['address'].lower():
                    continue

                return definition['abi']


def get_contract_by_name(contract_path, network_name, contract_name):
    file_name = '{}.{}.json'.format(contract_name, network_name)
    with open(os.path.join(contract_path, file_name)) as f:
        contract = json.loads(f.read())
        return contract


def get_contract_abi_and_address(web3, contract_path, contract_name, network_name=None):
    if not network_name:
        network_name = get_network_name(web3)
    contract_json = get_contract_by_name(contract_path, network_name, contract_name)
    return contract_json['abi'], web3.toChecksumAddress(contract_json['address'])


def get_contract_instance(web3, contract_path, contract_name, network_name=None):
    abi, address = get_contract_abi_and_address(web3, contract_path, contract_name, network_name)
    return web3.eth.contract(address=address, abi=abi)


def get_fingerprint_by_name(abi, name):
    for item in abi:
        if 'name' in item and item['name'] == name:
            return item['signature']

    raise ValueError('{} not found in the given ABI'.format(name))


def get_fingerprint_bytes_by_name(web3, abi, name):
    return hexstr_to_bytes(web3, get_fingerprint_by_name(abi, name))


def hexstr_to_bytes(web3, hexstr):
    return web3.toBytes(int(hexstr, 16))
