"""

    Keeper Contract Base

    All keeper contract inherit from this base class

"""

class KeeperContract(object):
    def __init__(self, web3_helper, contract_name, name, contract_path, address):
        self._web3_helper = web3_helper
        contract = web3_helper.load(contract_name, name, contract_path, address)
        self._helper = web3_helper
        self._contract_concise = contract[0]
        self._contract = contract[1]
        self._address = web3_helper.to_checksum_address(contract[2])
        self._name = name

    @property
    def address(self):
        return self._address

    @property
    def name(self):
        return self._name

    # TODO: remove contract_concise and handle all contract interfaces within the contract class
    @property
    def contract_concise(self):
        return self._contract_concise

    # TODO: remove contract and handle all contract interfaces within the contract class
    @property
    def contract(self):
        return self._contract
