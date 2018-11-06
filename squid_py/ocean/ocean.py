import logging

from web3 import Web3, HTTPProvider

from squid_py.ocean.account import Account
from squid_py.aquariuswrapper import AquariusWrapper
from squid_py.config import Config
from squid_py.keeper import Keeper
from squid_py.log import setup_logging
from squid_py.didresolver import DIDResolver

CONFIG_FILE_ENVIRONMENT_NAME = 'CONFIG_FILE'

setup_logging()


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

        # Add the Metadata store to the interface
        if self.config.aquarius_url:
            self.metadata = AquariusWrapper(self.config.aquarius_url)
        else:
            self.metadata = None

        # Collect the accounts
        self.accounts = self.get_accounts()

        assert self.accounts

        self.did_resolver = DIDResolver(self._web3, self.keeper.didregistry)

    def print_config(self):
        # TODO: Cleanup
        print("Ocean object configuration:".format())
        print("Ocean.config.keeper_path: {}".format(self.config.keeper_path))
        print("Ocean.config.keeper_url: {}".format(self.config.keeper_url))
        print("Ocean.config.gas_limit: {}".format(self.config.gas_limit))
        print("Ocean.config.aquarius_url: {}".format(self.config.aquarius_url))
        print("Ocean.config.address_list.market: {}".format(self.config.address_list['market']))
        print("Ocean.config.address_list.token: {}".format(self.config.address_list['token']))
        print("Ocean.config.address_list.auth: {}".format(self.config.address_list['auth']))
        print("Ocean.config.address_list.didregistry: {}".format(self.config.address_list['didregistry']))

    def get_accounts(self):
        accounts_dict = dict()
        for account_address in self._web3.eth.accounts:
            accounts_dict[account_address] = Account('name', self.keeper, account_address)
        return accounts_dict

    def get_asset(self, asset_did):
        """
        Given an asset_did, return the Asset
        :return: Asset object
        """
        return self.metadata.get_asset_metadata(asset_did)


    def search_assets(self, text, sort=None, offset=100, page=0):
        """
        Search an asset in oceanDB using aquarius.
        :param text
        :param sort
        :param offset
        :param page
        :return: List of assets that match with the query.
        """
        return self.metadata.text_search(text=text, sort=sort, offset=offset, page=page)

    def register(self, asset, asset_price, publisher_acct):
        """
        Register an asset in both the Market (on-chain) and in the Meta Data store

        Wrapper on both
            - keeper.market.register
            - metadata.publish_asset

        :param asset:
        :param asset_price:
        :param publisher_acct:
        :return:
        """

        # 1) Check that the asset is valid
        assert asset.has_metadata
        assert asset.is_valid_did
        assert asset.ddo.is_valid

        # 2) Check that the publisher is valid and has funds
        assert publisher_acct.address in self.accounts

        # 3) Publish to metadata store
        # Check if it's already registered first!
        if asset.asset_id in self.metadata.list_assets()['ids']:
            # TODO: raise proper error
            pass
        self.metadata.publish_asset_metadata(asset)

        # 4) Register the asset onto blockchain
        result = self.keeper.market.register_asset(asset, asset_price, publisher_acct.address)

    def resolve_did(self, did):
        self.did_resolver.resolve(did)
