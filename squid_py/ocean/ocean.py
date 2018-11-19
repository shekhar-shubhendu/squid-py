import json

import requests
from web3 import Web3, HTTPProvider
from secret_store_client.client import Client

from squid_py.ddo.metadata import Metadata
from squid_py.ocean.account import Account
from squid_py.ocean.asset import Asset
from squid_py.aquariuswrapper import AquariusWrapper
from squid_py.config import Config
from squid_py.ddo import DDO
from squid_py.ddo.public_key_rsa import PUBLIC_KEY_TYPE_RSA
from squid_py.keeper import Keeper
from squid_py.log import setup_logging
from squid_py.didresolver import DIDResolver
from squid_py.exceptions import OceanDIDAlreadyExist, OceanInvalidMetadata
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.service_factory import ServiceFactory, ServiceDescriptor
from squid_py.service_agreement.utils import make_public_key_and_authentication, register_service_agreement_template
from squid_py.utils.utilities import generate_new_id
from squid_py.did import did_to_id, did_generate

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
        self.keeper = Keeper(self._web3, self.config.keeper_path)

        # Add the Metadata store to the interface
        if self.config.aquarius_url:
            self.metadata_store = AquariusWrapper(self.config.aquarius_url)
        else:
            self.metadata_store = None

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

        return Asset.from_ddo_dict(self.metadata_store.get_asset_metadata(asset_did))

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
            return [Asset.from_ddo_dict(i) for i in self.metadata_store.text_search(text, sort, offset, page)]

    def search_assets_by_text(self, search_text):
        # TODO: implement this
        assets = []
        return assets

    def register_asset(self, metadata, publisher_address, service_descriptors, threshold=None):
        """
        Register an asset in both the keeper's DIDRegistry (on-chain) and in the Meta Data store (Aquarius)

        :param metadata: dict conforming to the Metadata accepted by Ocean Protocol.
        :param publisher_address: Account of the publisher registering this asset
        :param service_descriptors: list of ServiceDescriptor tuples of length 2. The first item must be one of ServiceTypes and the second
            item is a dict of parameters and values required by the service.
        :return:
        """
        assert publisher_address in self.accounts, 'Unrecognized publisher address %s' % publisher_address
        assert isinstance(metadata, dict), 'Expected metadata of type dict, got "%s"' % type(metadata)
        if not metadata or not Metadata.validate(metadata):
            raise OceanInvalidMetadata('Metadata seems invalid. Please make sure the required metadata values are filled in.')

        asset_id = generate_new_id()
        # Check if it's already registered first!
        if asset_id in self.metadata_store.list_assets():
            raise OceanDIDAlreadyExist('Asset id "%s" is already registered to another asset.' % asset_id)

        # copy metadata so we don't change the original
        metadata_copy = metadata.copy()

        # Create a DDO object
        did = did_generate(asset_id)
        ddo = DDO(did)

        # Add public key and authentication
        pub_key, auth = make_public_key_and_authentication(did, publisher_address, self._web3)
        ddo.add_public_key(pub_key)
        ddo.add_authentication(auth, PUBLIC_KEY_TYPE_RSA)

        # Setup metadata service
        # First replace `contentUrls` with encrypted `contentUrls`
        assert metadata_copy['base']['contentUrls'], 'contentUrls is required in the metadata base attributes.'
        content_urls_encrypted = self._encrypt_metadata_content_urls(did, json.dumps(metadata_copy['base']['contentUrls']))
        # only assign if the encryption worked
        if content_urls_encrypted:
            metadata_copy['base']['contentUrls'] = content_urls_encrypted

        # DDO url and `Metadata` service
        ddo_service_endpoint = self.metadata_store.get_service_endpoint(did)
        metadata_service_desc = ServiceDescriptor.metadata_service_descriptor(metadata_copy, ddo_service_endpoint)

        # Add all services to ddo
        _service_descriptors = service_descriptors + [metadata_service_desc]
        for service in ServiceFactory.build_services(did, _service_descriptors):
            ddo.add_service(service)

        # publish the new ddo in ocean-db/Aquarius
        self.metadata_store.publish_asset_metadata(ddo)

        # register on-chain
        self.keeper.didregistry.register(
            Web3.toBytes(hexstr=asset_id),
            key=Web3.sha3(text='Metadata'),
            url=ddo_service_endpoint,
            account=publisher_address
        )

        return ddo

    def sign_service_agreement(self, did, service_definition_id, consumer):
        service_agreement_id = '0x%s' % generate_new_id()
        # Extract all of the params necessary for execute agreement from the ddo
        ddo = DDO(json_text=json.dumps(self.metadata_store.get_asset_metadata(did)))
        service = ddo.find_service_by_key_value(ServiceAgreement.SERVICE_DEFINITION_ID_KEY, service_definition_id)
        if not service:
            raise ValueError('Service with definition id "%s" is not found in this DDO.' % service_definition_id)

        service = service.as_dictionary()
        sa = ServiceAgreement.from_service_dict(service)
        purchase_endpoint = sa.purchase_endpoint

        signature, sa_hash = sa.get_signed_agreement_hash(self._web3, did_to_id(did), service_agreement_id, consumer)
        # Prepare a payload to send to `Brizo`
        payload = json.dumps({
            'did': did,
            'serviceAgreementId': service_agreement_id,
            'serviceDefinitionId': service_definition_id,
            'signature': signature,
            'consumerPublicKey': consumer
        })
        requests.post(purchase_endpoint, data=payload, headers={'content-type': 'application/json'})

        # :TODO: enable event handling
        # # subscribe to events related to this service_agreement_id
        # register_service_agreement(self._web3, self.keeper.contract_path, self.config.storage_path, consumer,
        #                            service_agreement_id, did, service, 'consumer', 3)

        return service_agreement_id

    def execute_service_agreement(self, did, service_definition_id, service_agreement_id,
                                  service_agreement_signature, consumer_address, publisher_address):
        """
        Execute the service agreement on-chain using keeper's ServiceAgreement contract.
        The on-chain executeAgreement method requires the following arguments:
        templateId, signature, consumer, hashes, timeouts, serviceAgreementId, did

        `agreement_message_hash` is necessary to verify the signature.
        The consumer `signature` includes the conditions timeouts and parameters value which is used on-chain to verify the values actually
        match the signed hashes.

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param service_definition_id: str identifies the specific service in the ddo to use in this agreement.
        :param service_agreement_id: 32 bytes identifier created by the consumer and will be used on-chain for the executed agreement.
        :param service_agreement_signature: str the signed agreement message hash which includes conditions and their parameters
            values and other details of the agreement.
        :param consumer_address: ethereum account address of consumer
        :param publisher_address: ethereum account address of publisher
        :return:
        """
        # Extract all of the params necessary for execute agreement from the ddo
        ddo = DDO(json_text=json.dumps(self.metadata_store.get_asset_metadata(did)))
        service = ddo.find_service_by_key_value(ServiceAgreement.SERVICE_DEFINITION_ID_KEY, service_definition_id)
        if not service:
            raise ValueError('Service with definition id "%s" is not found in this DDO.' % service_definition_id)

        asset_id = did_to_id(did)
        service = service.as_dictionary()
        sa = ServiceAgreement.from_service_dict(service)
        self.verify_service_agreement_signature(did, service_agreement_id, service_definition_id, consumer_address, service_agreement_signature, ddo=ddo)

        receipt = self.keeper.service_agreement.execute_service_agreement(
            sa.sla_template_id,
            service_agreement_signature,
            consumer_address,
            sa.conditions_params_value_hashes,
            sa.conditions_timeouts,
            service_agreement_id,
            asset_id,
            publisher_address
        )

        # :TODO: enable event handling
        # # subscribe to events related to this service_agreement_id
        # register_service_agreement(self._web3, self.keeper.contract_path, self.config.storage_path, publisher_address,
        #                            service_agreement_id, did, service, 'publisher', 3)

        return receipt

    def check_permissions(self, service_agreement_id, did, consumer_address):
        """
        Verify on-chain that the `consumer_address` has permission to access the given `asset_did` according to the `service_agreement_id`.

        :param service_agreement_id:
        :param asset_did:
        :param consumer_address:
        :return: bool True if user has permission
        """
        # :TODO:
        #   1. ensure service_agreement_id is actually executed on-chain and is associated to both asset_id and consumer_address

        return True

    def verify_service_agreement_signature(self, did, service_agreement_id, service_definition_id, consumer_address, signature, ddo=None):
        if not ddo:
            ddo = DDO(json_text=json.dumps(self.metadata_store.get_asset_metadata(did)))

        service = ddo.find_service_by_key_value(ServiceAgreement.SERVICE_DEFINITION_ID_KEY, service_definition_id)
        if not service:
            raise ValueError('Service with definition id "%s" is not found in this DDO.' % service_definition_id)

        service = service.as_dictionary()
        sa = ServiceAgreement.from_service_dict(service)
        agreement_hash = ServiceAgreement.generate_service_agreement_hash(
            self._web3, sa.sla_template_id, sa.conditions_keys, sa.conditions_params_value_hashes,
            sa.conditions_timeouts, service_agreement_id
        )
        # :TODO: complete the signature verification below. This is disabled because the KeyAPI recovery does not match the original
        # consumer address/public key.
        return True
        # pub_key = KeyAPI.PublicKey.recover_from_msg_hash(agreement_hash, KeyAPI.Signature(self._web3.toBytes(hexstr=signature)))
        # address = pub_key.to_address()
        # return address == consumer_address

    def _register_service_agreement_template(self, template_dict, owner_address):
        sla_template = ServiceAgreementTemplate(template_json=template_dict)
        return register_service_agreement_template(self.keeper, owner_address, sla_template)

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

    def _encrypt_metadata_content_urls(self, did, data):
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
            # document_id = secrets.token_hex(32)
            result = publisher.publish_document(document_id, data)
        return result
