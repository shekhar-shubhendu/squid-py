"""
    Collection of Keeper contracts

"""

from squid_py.keeper.auth import Auth
from squid_py.keeper.market import Market
from squid_py.keeper.token import Token


class Keeper(object):
    def __init__(self, web3, contract_path, address_list):
        # self._helper = web3_helper
        self._market = Market(web3, contract_path, address_list['market'])
        self._auth = Auth(web3, contract_path, address_list['auth'])
        self._token = Token(web3, contract_path, address_list['token'])

    @property
    def market(self):
        return self._market

    @property
    def token(self):
        return self._token

    @property
    def auth(self):
        return self._auth
