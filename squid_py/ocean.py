import logging
import os

from web3 import Web3, HTTPProvider

from squid_py.config import Config
from squid_py.keeper import Keeper
from squid_py.log import setup_logging
from squid_py.metadata import Metadata
from squid_py.account import Account

from squid_py.utils import Web3Helper

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
        if self.config.provider_url:
            self.metadata = Metadata(self.config.provider_url)
        else: self.metadata = None


        # Collect the accounts
        self.accounts = self.get_accounts()

        assert self.accounts

    def print_config(self):
        #TODO: Cleanup
        print("Ocean object configuration:".format())
        print("Ocean.config.keeper_path: {}".format(self.config.keeper_path))
        print("Ocean.config.keeper_url: {}".format(self.config.keeper_url))
        print("Ocean.config.gas_limit: {}".format(self.config.gas_limit))
        print("Ocean.config.provider_url: {}".format(self.config.provider_url))
        print("Ocean.config.address_list.market: {}".format(self.config.address_list['market']))
        print("Ocean.config.address_list.token: {}".format(self.config.address_list['token']))
        print("Ocean.config.address_list.auth: {}".format(self.config.address_list['auth']))

    def update_accounts(self):
        """
        Using the Web3 driver, get all account addresses
        This is used for development to get an overview of all accounts
        For each address, instantiate a new Account object
        :return: List of Account instances
        """
        logging.debug("Updating accounts")
        accounts_dict = dict()
        for account_address in self._web3.eth.accounts:
            accounts_dict[account_address] = Account(self.keeper, account_address)

        self.accounts = accounts_dict

    def get_accounts(self):
        self.update_accounts()
        return self.accounts

    def get_asset(self):
        """
        Given an assetID, return the Asset
        :return: Asset object
        """
        pass
        return this_asset

    def get_asset_ids(self):
        """

        :return:
        """
        pass

    def search_assets(self):
        """

        :return:
        """
        pass

    def register(self,asset):
        """
        Register an asset in both the Market (on-chain) and in the Meta Data store

        Wrapper on keeper.market.register and metadata.publish_asset

        :param Asset: Asset object
        :return:
        """
        # First, publish this asset to the MetaData store
        meta_data_assets = self.metadata.list_assets()

        # If this asset is already registered, remove it from the metadatastore
        #TODO: Handle this differently!
        if asset['assetId'] in meta_data_assets['assetsIds']:
            print("Removing asset {}".format(SAMPLE_METADATA1['assetId']))
            ocean.metadata.get_asset_metadata(SAMPLE_METADATA1['assetId'])
            ocean.metadata.retire_asset_metadata(SAMPLE_METADATA1['assetId'])
        pass

class Order:
    def __init__(self):
        pass

