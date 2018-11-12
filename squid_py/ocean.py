import json
import logging

import requests
from web3 import Web3, HTTPProvider
from secret_store_client.client import Client

from squid_py.account import Account
from squid_py.aquariuswrapper import AquariusWrapper
from squid_py.asset import Asset
from squid_py.config import Config
from squid_py.ddo import DDO, PUBLIC_KEY_STORE_TYPE_HEX
from squid_py.ddo.authentication import Authentication
from squid_py.ddo.public_key_base import PublicKeyBase
from squid_py.ddo.public_key_rsa import PUBLIC_KEY_TYPE_RSA
from squid_py.didresolver import VALUE_TYPE_URL, VALUE_TYPE_DID
from squid_py.keeper import Keeper
from squid_py.log import setup_logging
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.services import ServiceTypes, ServiceFactory
from squid_py.utils import to_32byte_hex
from squid_py.utils.utilities import get_publickey_from_address, generate_new_id, get_id_from_did

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
        self.keeper = Keeper(self._web3, self.config.keeper_path)

        # Add the Metadata store to the interface
        if self.config.aquarius_url:
            self.metadata_store = AquariusWrapper(self.config.aquarius_url)
        else:
            self.metadata_store = None

        # Collect the accounts
        self.accounts = self.get_accounts()

        assert self.accounts

    def print_config(self):
        # TODO: Cleanup
        print("Ocean object configuration:".format())
        print("Ocean.config.keeper_path: {}".format(self.config.keeper_path))
        print("Ocean.config.keeper_url: {}".format(self.config.keeper_url))
        print("Ocean.config.gas_limit: {}".format(self.config.gas_limit))
        print("Ocean.config.aquarius_url: {}".format(self.config.aquarius_url))

    def _update_accounts(self):
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
        self._update_accounts()
        return self.accounts

    def get_asset(self, asset_did):
        """
        Given an assetID, return the Asset
        :return: Asset object
        """
        # TODO: implement this
        asset = None
        return asset

    def get_order(self, order_id):
        # TODO: implement this
        order = None
        return order

    def search_assets(self, search_query):
        """

        :return:
        """
        # TODO: implement this
        assets = []
        return assets

    def search_assets_by_text(self, search_text):
        # TODO: implement this
        assets = []
        return assets

    def register_asset(self, metadata, publisher_account, service_descriptors):
        # Create a DDO object
        asset_id = generate_new_id(metadata)
        did = 'did:op:%s' % asset_id
        ddo = DDO(did)
        # set public key
        public_key_value = get_publickey_from_address(self._web3, publisher_account)
        pub_key = PublicKeyBase('keys-1', **{'value': public_key_value, 'owner': publisher_account, 'type': PUBLIC_KEY_STORE_TYPE_HEX})
        pub_key.assign_did(did)
        ddo.add_public_key(pub_key)
        # set authentication
        auth = Authentication(pub_key, PUBLIC_KEY_TYPE_RSA)
        ddo.add_authentication(auth, PUBLIC_KEY_TYPE_RSA)

        # TODO: setup secret store encryption session and encrypt contents
        # contents_url = metadata['base']['contentUrls']
        # publisher = Client(secret_store_url, parity_client_publish_url,
        #                    publisher_address, publisher_password)

        # DDO url and `Metadata` service
        ddo_service_endpoint = self.metadata_store.get_service_endpoint(did)
        metadata_service = ServiceFactory.build_metadata_service(did, metadata, ddo_service_endpoint)
        ddo.add_service(metadata_service)
        # Other services for consuming the asset
        sa_def_key = ServiceAgreement.SERVICE_DEFINITION_ID_KEY
        for i, service_desc in enumerate(service_descriptors):
            service = ServiceFactory.build_service(service_desc, did)
            # set serviceDefinitionId for each service
            service.update_value(sa_def_key, 'services-{}'.format(i+1))
            ddo.add_service(service)

        # publish the new ddo in ocean-db/Aquarius
        self.metadata_store.publish_asset_metadata(Asset(ddo))

        # register on-chain
        self.keeper.didregistry.register_attribute(Web3.toBytes(hexstr=asset_id), VALUE_TYPE_DID, Web3.sha3(text='Metadata'), ddo_service_endpoint, publisher_account)

        return ddo

    def sign_service_agreement(self, did, consumer, service_definition_id):
        service_id = ''
        # Extract all of the params necessary for execute agreement from the ddo
        service = None
        sa_def_key = ServiceAgreement.SERVICE_DEFINITION_ID_KEY
        ddo = DDO(json_text=json.dumps(self.metadata_store.get_asset_metadata(did)))
        for s in ddo.services:
            if sa_def_key in s.get_values() and s.get_values()[sa_def_key] == service_definition_id:
                service = s
                break

        if not service:
            raise ValueError('Service with definition id "%s" is not found in this DDO.' % service_definition_id)

        service = service.as_dictionary()
        purchase_endpoint = service['purchaseEndpoint']
        # Prepare a payload to send to `Brizo`
        # payload = json.puts()
        # requests.post(purchase_endpoint, '', payload)

        return service_id

    def execute_service_agreement(self, sa_id, signature, sa_message_hash, consumer_address, ddo, price, timeout):
        # Extract all of the params necessary for execute agreement from the ddo
        # Validate the signature before submitting service agreement on-chain

        return

    def resolve_did(self, did):
        ddo_object = None
        _id = Web3.toHex(get_id_from_did(did))
        event_filter = self.keeper.didregistry.events.SetupAgreementTemplate.createFilter(
            fromBlock='latest', argument_filters={'did': _id, 'type': VALUE_TYPE_DID, 'key': Web3.sha3('Metadata')})
        logs = event_filter.get_all_entries()
        if logs:
            ddo_endpoint = logs[-1]
            if ddo_endpoint:
                response = requests.get(ddo_endpoint)
                ddo_object = DDO(json_text=response)

        return ddo_object