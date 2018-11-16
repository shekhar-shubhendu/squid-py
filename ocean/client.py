"""
    Client class, to handle connections to the Ocean network
"""
from web3 import (
    Web3,
    HTTPProvider
)

from squid_py.keeper import Keeper

class Client():

    def __init__(self, ocean_url, contracts_path, metadata_agent_auth=None):
        """
        init the connection with URL for the ethereum node and the path
        to the contracts ABI files
        """
        self._ocean_url = ocean_url
        self._contracts_path = contracts_path
        self._metadata_agent_auth = metadata_agent_auth

        # For development, we use the HTTPProvider Web3 interface
        self._web3 = Web3(HTTPProvider(self._ocean_url))

        # With the interface loaded, the Keeper node is connected with all contracts
        self._keeper = Keeper(self._web3, self._contracts_path)


    @property
    def accounts(self):
        """return the ethereum accounts"""
        return self._web3.eth.accounts

    @property
    def web3(self):
        """return the web3 instance"""
        return self._web3

    @property
    def keeper(self):
        """return the keeper contracts"""
        return self._keeper

    @property
    def metadata_agent_auth(self):
        """return extra authenticaiton information needed to acess the metadata agent"""
        return self._metadata_agent_auth
