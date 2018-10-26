"""
    Collection of Keeper contracts

"""

from squid_py.keeper.auth import Auth
from squid_py.keeper.market import Market
from squid_py.keeper.token import Token
import logging


class Keeper(object):
    def __init__(self, web3, contract_path, address_list):
        """
        The Keeper class aggregates all contracts in the Ocean Protocol node

        :param web3: The common web3 object
        :param contract_path: Path for
        :param address_list:
        """

        self.web3 = web3
        self.contract_path = contract_path
        self.address_list = address_list

        logging.debug("Keeper contract artifacts (JSON) at: {}".format(self.contract_path))

        # The contract objects
        self.market = Market(web3, contract_path, address_list['market'])
        self.auth = Auth(web3, contract_path, address_list['auth'])
        self.token = Token(web3, contract_path, address_list['token'])

        logging.debug("Keeper instantiated with {} contracts".format(len(self.address_list)))
