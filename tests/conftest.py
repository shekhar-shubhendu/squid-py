import os
from secret_store_client.client import Client
import json

import pytest
from web3 import Web3, HTTPProvider

from squid_py.config import Config
from squid_py.ddo.metadata import Metadata
from squid_py.ocean import ocean
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.service_factory import ServiceDescriptor
from squid_py.service_agreement.utils import get_sla_template_path, register_service_agreement_template


class SecretStoreClientMock(Client):
    def __init__(self, *args, **kwargs):
        pass

    def publish_document(self, document_id, document, threshold=0):
        return '!!%s!!' % document

    def decrypt_document(self, document_id, encrypted_document):
        return encrypted_document[2: -2]


class BrizoMock(object):
    def __init__(self, ocean_instance, publisher_address):
        self.ocean_instance = ocean_instance
        self.publisher_address = publisher_address

    def post(self, url, data=None, **kwargs):
        if url.endswith('initialize'):
            payload = json.loads(data)
            did = payload['did']
            sa_id = payload['serviceAgreementId']
            sa_def_id = payload['serviceDefinitionId']
            signature = payload['signature']
            consumer = payload['consumerPublicKey']
            valid_signature = self.ocean_instance.verify_service_agreement_signature(did, sa_id, sa_def_id, consumer, signature)
            assert valid_signature, 'Service agreement signature seems invalid.'
            if valid_signature:
                self.ocean_instance.execute_service_agreement(did, sa_def_id, sa_id, signature, consumer, self.publisher_address)

        return


def make_ocean_instance():
    path_config = 'config_local.ini'
    os.environ['CONFIG_FILE'] = path_config
    return ocean.Ocean(os.environ['CONFIG_FILE'])


@pytest.fixture
def secret_store():
    return SecretStoreClientMock

@pytest.fixture
def ocean_instance():
    ocean.Client = SecretStoreClientMock
    ocn = make_ocean_instance()
    ocean.requests = BrizoMock(ocn, list(ocn.accounts)[0])

    return ocn


@pytest.fixture
def registered_ddo():
    ocean_instance = make_ocean_instance()
    publisher = list(ocean_instance.accounts)[0]
    # register an AssetAccess service agreement template
    register_service_agreement_template(
        ocean_instance.keeper, publisher, ServiceAgreementTemplate.from_json_file(get_sla_template_path())
    )

    metadata = Metadata.get_example()

    ddo = ocean_instance.register_asset(
        metadata, publisher,
        [ServiceDescriptor.access_service_descriptor(7, '/brizo/initialize', '/service/endpoint', 3)]
    )
    return ddo


@pytest.fixture
def web3_instance():
    path_config = 'config_local.ini'
    os.environ['CONFIG_FILE'] = path_config
    config = Config(path_config)
    return Web3(HTTPProvider(config.keeper_url))
