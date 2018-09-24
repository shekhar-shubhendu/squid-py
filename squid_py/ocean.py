import logging
import os

from web3 import Web3, HTTPProvider

from squid_py.config_parser import load_config_section, get_value
from squid_py.constants import KEEPER_CONTRACTS
from squid_py.utils.web3_helper import Web3Helper
from squid_py.keeper.market import Market
from squid_py.keeper.auth import Auth
from squid_py.keeper.token import Token
from squid_py.metadata import Metadata


class Ocean(object):
    def __init__(self, host=None, port=None, config_path=None):
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

        # self.web3provider =
        # self.node_uri =
        self.default_gas = get_value(self.config, 'gas.limit', 'GAS_LIMIT', 300000)
        self.helper = Web3Helper(self.web3, self.config)
        self.provider_uri = get_value(self.config, 'provider.uri', 'PROVIDER_URI', 'http://localhost:5000')
        self.metadata = Metadata(self.provider_uri)
        self.market = Market(self.helper)
        self.auth = Auth(self.helper)
        self.token = Token(self.helper)
        self.network = self.helper.get_network_name()

    @staticmethod
    def connect_web3(host, port='8545'):
        """Establish a connexion using Web3 with the client."""
        return Web3(HTTPProvider("%s:%s" % (host, port)))
