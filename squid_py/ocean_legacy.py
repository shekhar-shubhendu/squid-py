
class Ocean_Legacy:
    """Create a new Ocean object for access to the Ocean Protocol Network

    :param keeper_url: URL of the Keeper network to connect too.
    :param address_list: Dictinorary of contract addresses.
        [
            'market': '0x00..00',
            'auth' : '0x00..00',
            'token' : '0x00..00',
        ]
    :param web3: Web3 object to use to connect too the keeper node.
    :param keeper_path: Path to the Ocean Protocol Keeper contracts, to load contracts and addresses via the artifacts folder.
    :param logger: Optional logger to use instead of creating our own loggger
    :param aquarius_url: Optional url of the ocean network aquarius, can be None
    :param gas_limit: Optional gas limit, defaults to 300000
    :param config_file: Optional config file to load in the above config details
    :returns: Ocean object

    An example in creating an Ocean object::

        address = [
            'market': '0x00..00',
            'auth' : '0x00..00',
            'token' : '0x00..00',
        ]
        ocean = Ocean(url='http://localhost:8545', aquarius_url = 'http://localhost:5000', address_list = address)
        print(ocean.accounts[0])

    """

    def __init__(self, **kwargs):
        self._w3 = None
        self._logger = kwargs.get('logger') or logging.getLogger(__name__)

        config_file = kwargs.get('config_file', os.getenv(CONFIG_FILE_ENVIRONMENT_NAME) or None)

        config = Config(config_file)

        self._keeper_url = kwargs.get('keeper_url', config.keeper_url)
        self._keeper_path = kwargs.get('keeper_path', config.keeper_path)
        self._gas_limit = kwargs.get('gas_limit', config.gas_limit)
        self._aquarius_url = kwargs.get('aquarius_url', config.aquarius_url)

        # put a priority on getting the contracts directly instead of via the 'ocean node'

        # load in the contract addresses
        self._address_list = config.address_list
        if 'address_list' in kwargs:
            address_list = kwargs['address_list']
            for name in self._address_list:
                if name in address_list and address_list[name]:
                    self._address_list[name] = address_list[name]

        if self._keeper_url is None:
            raise TypeError('You must provide a Keeper URL')

        if 'web3' in kwargs:
            self._web3 = kwargs['web3']
        else:
            self._web3 = Web3(HTTPProvider(self._keeper_url))
        if self._web3 is None:
            raise ValueError('You need to provide a valid Keeper URL or Web3 object')

        self._helper = Web3Helper(self._web3)

        # optional _aquarius_url
        if self._aquarius_url:
            self._metadata = Metadata(self._aquarius_url)
        self._network_name = self._helper.network_name
        self._contracts = Keeper(self._helper, self._keeper_path, self._address_list)

    def calculate_hash(self, message):
        return self._web3.sha3(message)

    def generate_did(self, content):
        return 'did:ocn:' + self._contracts.market.contract_concise.generateId(content)

    def resolve_did(self, did):
        pass

    def get_ether_balance(self, account_address):
        return self._contracts.token.get_ether_balance(account_address)

    def get_token_balance(self, account_address):
        return self._contracts.token.get_token_balance(account_address)

    # Properties
    @property
    def web3(self):
        return self._web3

    @property
    def address_list(self):
        return self._address_list

    @property
    def gas_limit(self):
        return self._gas_limit

    @property
    def keeper_path(self):
        return self._keeper_path

    @property
    def keeper_url(self):
        return self._keeper_url

    @property
    def aquarius_url(self):
        return self._aquarius_url

    @property
    def network_name(self):
        return self._network_name

    @property
    def accounts(self):
        accounts = []
        if self._helper and self._helper.accounts:
            for account_address in self._helper.accounts:
                accounts.append({
                    'address': account_address,
                    'ether': self.get_ether_balance(account_address),
                    'token': self.get_token_balance(account_address)
                })
        return accounts

    def get_accounts(self):
        # Wrapper for API unification
        return self.accounts

    @property
    def helper(self):
        return self._helper

    # TODO: remove later from user space
    @property
    def metadata(self):
        return self._metadata

    @property
    def contracts(self):
        return self._contracts

    # Static methods
    @staticmethod
    def connect_web3(host, port='8545'):
        """Establish a connexion using Web3 with the client."""
        return Web3(HTTPProvider("{0}:{1}".format(host, port)))
