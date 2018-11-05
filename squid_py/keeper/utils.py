import json
import os


def get_contract_abi_by_address(config, address):
    contract_tree = os.walk(config.keeper_path)

    while True:
        dirname, _, files = next(contract_tree)
        for entry in files:
            with open(os.path.join(dirname, entry)) as f:
                try:
                    definition = json.loads(f.read())
                except Exception:
                    continue

                if address != definition['address']:
                    continue

                return definition['abi']


def get_contract_by_name(config, network_name, contract_name):
    file_name = '{}.{}.json'.format(contract_name, network_name)
    with open(os.path.join(config.keeper_path, file_name)) as f:
        contract = json.loads(f.read())
        return contract


def get_fingerprint_by_name(abi, name):
    for item in abi:
        if 'name' in item and item['name'] == name:
            return item['signature']

    raise ValueError('{} not found in the given ABI'.format(name))


def hexstr_to_bytes(web3, hexstr):
    return web3.toBytes(int(hexstr, 16))
