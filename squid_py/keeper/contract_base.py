"""

    Keeper Contract Base

    All keeper contract inherit from this base class

"""

class ContractWrapperBase(object):

    """
    Base class for all contract objects.
    """
    def __init__(self, web3, contract_name, name, contract_path, address):
        """
        :param contract_name:
        :param name:
        :param contract_path:
        :param address:
        """
        # self._web3_helper = web3_helper
        contract = self.load(contract_name, name, contract_path, address)
        # self._helper = web3_helper
        self._contract_concise = contract[0]
        self._contract = contract[1]
        self._address = web3_helper.to_checksum_address(contract[2])
        self._name = name

    def load(self, contract_file, name, contract_path, contract_address):
        """Retrieve a tuple with the concise contract and the contract definition."""
        contract_filename = os.path.join(contract_path, "{}.json".format(contract_file))
        try:
            valid_address = self._web3.toChecksumAddress(contract_address)
        except ValueError as e:
            raise OceanInvalidContractAddress("Invalid contract address for keeper contract '{}'".format(name))
        except Exception as e:
            raise e

        with open(contract_filename, 'r') as abi_definition:
            abi = json.load(abi_definition)
            concise_cont = self._web3.eth.contract(
                address=valid_address,
                abi=abi['abi'],
                ContractFactoryClass=ConciseContract)
            contract = self._web3.eth.contract(
                address=valid_address,
                abi=abi['abi'])
            return concise_cont, contract, contract_address

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
