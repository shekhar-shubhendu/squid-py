import logging
import json
import hashlib
import pytest
import secrets
import os

from secret_store_client.client import Client

secret_store_url = 'http://localhost:8010'

parity_client_publish_url = 'http://localhost:8545'
publisher_address = "0x594d9f933f4f2df6bb66bb34e7ff9d27acc1c019"
publisher_password = 'password'

parity_client_consume_url = 'http://localhost:8545'
consumer_address= "0xd7fac5a254c27eb7bf387b596dd700b9531c9568"
publisher_password = 'password'


def test_secret_store():

    test_document = os.path.join('tests', 'resources', 'metadata', 'sample_metadata1.json')
    with open(test_document, 'r') as file_handle:
        metadata = json.load(file_handle)

    publisher = Client(secret_store_url, parity_client_publish_url,
                   publisher_address, publisher_password)

    metadata_json = json.dumps(metadata)
    document_id = hashlib.sha256((metadata_json + secrets.token_hex(32)).encode()).hexdigest()
    print(document_id)
    result = publisher.publish_document(document_id, metadata_json)
    print(result)
