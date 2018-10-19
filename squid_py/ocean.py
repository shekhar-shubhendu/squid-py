import logging
import os

from web3 import Web3, HTTPProvider

from squid_py.config import (
    Config,
)
from squid_py.keeper import Keeper
from squid_py.log import setup_logging
from squid_py.metadata import Metadata
from squid_py.utils import Web3Helper

CONFIG_FILE_ENVIRONMENT_NAME = 'CONFIG_FILE'

setup_logging()


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
    :param provider_url: Optional url of the ocean network provider, can be None
    :param gas_limit: Optional gas limit, defaults to 300000
    :param config_file: Optional config file to load in the above config details
    :returns: Ocean object

    An example in creating an Ocean object::

        address = [
            'market': '0x00..00',
            'auth' : '0x00..00',
            'token' : '0x00..00',
        ]
        ocean = Ocean(url='http://localhost:8545', provider_url = 'http://localhost:5000', address_list = address)
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
        self._provider_url = kwargs.get('provider_url', config.provider_url)

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

        # optional _provider_url
        if self._provider_url:
            self._metadata = Metadata(self._provider_url)
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
    def provider_url(self):
        return self._provider_url

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

class Ocean:
    def __init__(self, config_file):
        """
        The Ocean class is the entry point into Ocean Protocol.
        This class is an aggregation of
         * the smart contracts via the Keeper class
         * the metadata store
         * and utilities
        Ocean is also a wrapper for the web3.py interface (https://github.com/ethereum/web3.py)
        An instance of Ocean is parameterized by a configuration file.

        :param config_file:
        """

        # Configuration information for the market is stored in the Config class
        self.config = Config(config_file)

        # For development, we use the HTTPProvider Web3 interface
        self._web3 = Web3(HTTPProvider(self.config.keeper_url))

        # With the interface loaded, the Keeper node is connected with all contracts
        self.keeper = Keeper(self._web3, self.config.keeper_path, self.config.address_list)

        # Collect the accounts
        self.accounts = self.get_accounts()
        assert self.accounts

    def print_config(self):
        print("Ocean object configuration:".format())
        print("Ocean.keeper_path: {}".format(self.config.keeper_path))
        print("Ocean.keeper_url: {}".format(self.config.keeper_url))
        print("Ocean.gas_limit: {}".format(self.config.gas_limit))
        print("Ocean.provider_url: {}".format(self.config.provider_url))
        print("Ocean.address_list.market: {}".format(self.config.address_list['market']))
        print("Ocean.address_list.token: {}".format(self.config.address_list['token']))
        print("Ocean.address_list.auth: {}".format(self.config.address_list['auth']))

    def update_accounts(self):
        """
        Using the Web3 driver, get all account addresses
        This is used for development to get an overview of all accounts
        For each address, instantiate a new Account object
        :return: List of Account instances
        """
        accounts_dict = dict()
        for account_address in self._web3.eth.accounts:
            accounts_dict[account_address] = Account(self.keeper, account_address)

        self.accounts = accounts_dict

    def get_accounts(self):
        self.update_accounts()
        return self.accounts


class Account:
    def __init__(self, keeper, address):
        """
        Hold account address, and update balances of Ether and Ocean token

        :param keeper: The instantiated Keeper
        :param address: The address of this account
        """
        self.keeper = keeper
        self.address = address

        # Inititalize the balances with the current values from the Blockchain
        self.ether = self.get_ether_balance()
        self.ocean = self.get_ocean_balance()

    def get_ether_balance(self):
        """
        Call the Token contract method .web3.eth.getBalance()
        :return: Ether balance, int
        """
        self.ether = self.keeper.token.get_ether_balance(self.address)
        return self.ether

    def get_ocean_balance(self):
        """
        Call the Token contract method .balanceOf(account_address)
        :return: Ocean token balance, int
        """
        self.ocean = self.keeper.token.get_token_balance(self.address)
        return self.ocean

    def request_tokens(self,amount):
        return self.keeper.market.request_tokens(amount,self.address)

    def get_balance(self):
        pass

    def __str__(self):
        return "Account {} with {} Eth, {} Ocean".format(self.address, self.ether, self.ocean)

class Asset:
    def __init__(self, asset_id, publisher_id, price):
        """
        Represent an asset in the MetaData store

        :param asset_id:
        :param publisher_id:
        :param price:
        """

        self.asset_id = asset_id
        self.publisher_id = publisher_id
        self.price = price


    def purchase(self, consumer, timeout):
        """
        Generate an order for purchase of this Asset

        :param timeout:
        :param consumer: Account object of the requester
        :return: Order object
        """
        # Check if asset exists

        # Approve the token transfer

        # Submit access request

        return

    def consume(self, order, consumer):
        """

        :param order: Order object
        :param consumer: Consumer Account
        :return: access_url
        :rtype: string
        :raises :
        """

        # Get access token (jwt)

        # Download the asset from the provider using the URL in access token
        # Decode the the access token, get service_endpoint and request_id

        return

    def get_DDO(self):
        """

        :return:
        """

    def get_DID(self):
        pass

    def publish_metadata(self):
        pass

    def get_metadata(self):
        pass

    def update_metadata(self):
        pass

    def retire_metadata(self):
        pass

    def get_service_agreements(self):
        pass

class Order:
    def __init__(self):
        pass

