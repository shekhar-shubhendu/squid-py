import logging
import os

from web3 import Web3, HTTPProvider

from squid_py.config_parser import load_config_section, get_value
from squid_py.constants import KEEPER_CONTRACTS
from squid_py.keeper.auth import Auth
from squid_py.keeper.market import Market
from squid_py.keeper.token import Token
from squid_py.log import setup_logging
from squid_py.metadata import Metadata
from squid_py.utils.web3_helper import Web3Helper

from squid_py.config import (
    Config,
)

CONFIG_FILE_ENVIRONMENT_NAME = 'CONFIG_FILE'

setup_logging()


class Ocean(object):

    """Create a new Ocean object for access to the Ocean Protocol Network

    :param keeper_url: URL of the Keeper network to connect too.
    :param address_list: Dictinorary of contract addresses.
        [
            'market': '0x00..00',
            'auth' : '0x00..00',
            'token' : '0x00..00',
        ]
    :param web3: Web3 object to use as the Ethereum node.
    :param keeper_path: Path to the Ocean Protocol Keeper contracts, to load contracts and addresses via the artifacts folder.
    :param logger: Optional logger to use instead of creating our own loggger
    :param provider_url: url of the provider
    :param gas_limit: Optional gas limit, defaults to 300000
    :param config_file: Optional config file to load in the above config
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

        self._keeper_url = kwargs.get('keeper_url', config.get_keeper_url())
        self._keeper_path = kwargs.get('keeper_path', config.get_keeper_path())
        self._gas_limit = kwargs.get('gas_limit', config.get_gas_limit())
        self._provider_url = kwargs.get('provider_url', config.get_provider_url())

        # put a priority on getting the contracts directly instead of via the 'ocean node'

        # load in the contract addresses
        self._address_list = config.get_address_list()
        if 'address_list' in kwargs:
            address_list = kwargs['address_list']
            for name, value in self._address_list.items():
                if name in address_list and address_list[name]:
                    self._address_list[name] = address_list[name]


        if  self._keeper_url == None:
            raise TypeError('You must provide a Keeper url')

        if 'web3' in kwargs:
            self._web3 = kwargs['web3']
        else:
            if self._keeper_url:
                self._web3 = Web3(HTTPProvider(self._keeper_url))
        if self._web3 == None:
            raise ValueError('You need to provide a valid Keeper host and port connection values')
        """
        try:
            config_path = os.getenv('CONFIG_FILE') if not config_path else config_path
            self.config = load_config_section(config_path, KEEPER_CONTRACTS)
            self.host = get_value(self.config, 'keeper.host', 'KEEPER_HOST', host)
            self.port = get_value(self.config, 'keeper.port', 'KEEPER_PORT', port)
            self.web3 = self.connect_web3(self.host, self.port)
            logging.info("web3 connection: {}".format(self.web3))
        except:
            logging.error('OceanContracts could not initiate. You can specify the path in $CONFIG_FILE environment '
                          'variable.')
            raise Exception('You should provide a valid config file.')


        self.default_gas = get_value(self.config, 'gas.limit', 'GAS_LIMIT', 300000)
        self.provider_uri = get_value(self.config, 'provider.uri', 'PROVIDER_URI', 'http://localhost:5000')
        """
#        self.node_uri = "%s:%s" % (self.host, self.port)
        self.helper = Web3Helper(self._web3, self._keeper_path, self._address_list)
        self.metadata = Metadata(self._provider_url)
        self.market = Market(self.helper)
        self.auth = Auth(self.helper)
        self.token = Token(self.helper)
        self._network_name = self.helper.get_network_name()

    def get_web3(self):
        return self._web3

    @staticmethod
    def connect_web3(host, port='8545'):
        """Establish a connexion using Web3 with the client."""
        return Web3(HTTPProvider("%s:%s" % (host, port)))

    def get_message_hash(self, message):
        return self.web3.sha3(message)

    def generate_did(self, content):
        return 'did:ocn:' + self.market.contract_concise.generateId(content)

    def resolve_did(self, did):
        pass
