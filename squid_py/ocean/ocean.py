import logging
import json
import secrets

from web3 import Web3, HTTPProvider
from secret_store_client.client import Client

from squid_py.ocean.account import Account
from squid_py.ocean.asset import Asset
from squid_py.aquariuswrapper import AquariusWrapper
from squid_py.config import Config
from squid_py.keeper import Keeper
from squid_py.log import setup_logging
from squid_py.didresolver import DIDResolver
from squid_py.exceptions import OceanDIDAlreadyExist

from squid_py.did import did_to_id

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
        """
        Returns all available accounts loaded via a wallet, or by Web3.
        :return:
        """
        accounts_dict = dict()
        for account_address in self._web3.eth.accounts:
            accounts_dict[account_address] = Account(self.keeper, account_address)
        return accounts_dict

    def get_asset(self, asset_did):
        """
        Given an asset_did, return the Asset
        :return: Asset object
        """

        return Asset.from_ddo_dict(self.metadata.get_asset_metadata(asset_did))

    def search_assets(self, text, sort=None, offset=100, page=0, aquarius_url=None):
        """
        Search an asset in oceanDB using aquarius.
        :param text String with the value that you are searching.
        :param sort Dictionary to choose order base in some value.
        :param offset Number of elements shows by page.
        :param page Page number.
        :param aquarius_url Url of the aquarius where you want to search. If there is not provided take the default.
        :return: List of assets that match with the query.
        """
        if aquarius_url is not None:
            aquarius = AquariusWrapper(aquarius_url)
            return [Asset.from_ddo_dict(i) for i in aquarius.text_search(text, sort, offset, page)]
        else:
            return [Asset.from_ddo_dict(i) for i in self.metadata.text_search(text, sort, offset, page)]

    def register(self, asset, asset_price, publisher_acct):
        """
        Register an asset in both the Market (on-chain) and in the Meta Data store

        Wrapper on both
            - keeper.market.register
            - metadata.publish_asset
            - keeper.did_registry

        :param asset: Asset object.
        :param asset_price: Price of the asset.
        :param publisher_acct: Account of the publisher.
        :return:
        """

        # 1) Check that the asset is valid
        assert asset.has_metadata
        assert asset.is_valid

        # 2) Check that the publisher is valid and has funds
        assert publisher_acct.address in self.accounts

        # 3) Publish to metadata store
        # Check if it's already registered first!
        if asset.asset_id in self.metadata.list_assets():
            raise OceanDIDAlreadyExist

        # encrypt the contentUrls using the secret store
        metadata = None
        metadata_service = asset.ddo.get_service('Metadata')
        if 'metadata' in metadata_service.get_values():
            metadata = metadata_service.get_values()['metadata']
        if metadata and metadata['base']['contentUrls']:
            content_urls_encrypted = self.encrypt_content_urls(asset.did, json.dumps(metadata['base']['contentUrls']))
            # only assign if the encryption worked
            if content_urls_encrypted:
                metadata['base']['contentUrls'] = content_urls_encrypted
            
        logging.info("Publishing {} in aquarius".format(asset.did))
        self.metadata.publish_asset_metadata(asset.did, asset.ddo)

        # 4) Register the asset onto blockchain
        logging.info("Registering asset with did {} on chain.".format(asset.did))
        self.keeper.market.register_asset(asset, asset_price, publisher_acct.address)
        logging.info("Registering did {} in the registry.".format(asset.did))
        self.keeper.didregistry.register(asset.did,
                                         key=Web3.sha3(text='Metadata'),
                                         url=self.config.aquarius_url,
                                         account=publisher_acct.address)

    def resolve_did(self, did):
        """
        When you pass a did retrieve the ddo associated.
        :param did:
        :return:
        """
        resolver = self.did_resolver.resolve(did)
        if resolver.is_ddo:
            return self.did_resolver.resolve(did).ddo
        elif resolver.is_url:
            aquarius = AquariusWrapper(resolver.url)
            return aquarius.get_asset_metadata(did)
        else:
            return None

    def get_order(self):
        pass

    def get_orders_by_account(self):
        pass

    def search_orders(self):
        pass

    def get_service_agreement(self):
        pass

    def encrypt_content_urls(self, did, data):
        """
        encrypt string data using the DID as an secret store id, 
        if secret store is enabled then return the result from secret store encryption

        return None for no encryption performed
        """
        result = None
        if self.config.secret_store_url and self.config.parity_url and self.config.parity_address:
            publisher = Client(self.config.secret_store_url, self.config.parity_url,
                               self.config.parity_address, self.config.parity_password)

            document_id = did_to_id(did)
            # TODO: need to remove below to stop multiple session testing so that we can encrypt using the id from the DID.
            document_id = secrets.token_hex(32)
            result = publisher.publish_document(document_id, data)
        return result
