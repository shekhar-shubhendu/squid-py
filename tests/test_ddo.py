"""
    Test did_lib
"""
import json
import pathlib
import pytest
import secrets
from web3 import Web3

from did_ddo_lib.main import (
    did_generate,
    did_generate_from_ddo,
    did_validate,
)

from squid_py.ddo import (
    DDO,
    PUBLIC_KEY_STORE_TYPE_PEM,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_BASE64,
    PUBLIC_KEY_STORE_TYPE_BASE85,
)

public_key_store_types = [
    PUBLIC_KEY_STORE_TYPE_PEM,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_BASE64,
    PUBLIC_KEY_STORE_TYPE_BASE85,
]

TEST_SERVICE_TYPE = 'ocean-meta-storage'
TEST_SERVICE_URL = 'http://localhost:8005'


def test_creating_ddo():
    did_id = secrets.token_hex(32)
    did = did_generate(did_id)
    assert did
    ddo = DDO(did)
    assert ddo
    private_keys = []
    for public_key_store_type in public_key_store_types:
        private_keys.append(ddo.add_signature(public_key_store_type))

    assert len(private_keys) == len(public_key_store_types)
    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)

    assert len(ddo.public_keys) == len(public_key_store_types)
    assert len(ddo.authentications) == len(public_key_store_types)
    assert len(ddo.services) == 1

    ddo_text_no_proof = ddo.as_text()
    assert ddo_text_no_proof
    ddo_text_no_proof_hash = ddo.calculate_hash()

    # test getting public keys in the DDO record
    for index, private_key in enumerate(private_keys):
        assert ddo.get_public_key(index)
        signature_key_id = '{0}#keys={1}'.format(did, index + 1)
        assert ddo.get_public_key(signature_key_id)

    # test validating static proofs
    for index, private_key in enumerate(private_keys):
        ddo.add_proof(index, private_key)
        ddo_text_proof = ddo.as_text()
        assert ddo.validate_proof()
        ddo_text_proof_hash = ddo.calculate_hash()

    ddo = DDO(json_text=ddo_text_proof)
    assert ddo.validate()
    assert ddo.is_proof_defined()
    assert ddo.validate_proof()
    assert ddo.calculate_hash() == ddo_text_proof_hash

    ddo = DDO(json_text=ddo_text_no_proof)
    assert ddo.validate()
    # valid proof should be false since no static proof provided
    assert not ddo.is_proof_defined()
    assert not ddo.validate_proof()
    assert ddo.calculate_hash() == ddo_text_no_proof_hash


def test_creating_ddo_embedded_public_key():
    test_id = secrets.token_hex(32)
    did = did_generate(test_id)
    assert did
    ddo = DDO(did)
    assert ddo
    private_keys = []
    for public_key_store_type in public_key_store_types:
        private_keys.append(ddo.add_signature(public_key_store_type, is_embedded=True))

    assert len(private_keys) == len(public_key_store_types)
    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)
    # test validating static proofs
    for index, private_key in enumerate(private_keys):
        ddo.add_proof(index, private_key)
        ddo_text_proof = ddo.as_text()
        assert ddo_text_proof
        assert ddo.validate_proof()
        ddo_text_proof_hash = ddo.calculate_hash()
        assert ddo_text_proof_hash


def test_creating_did_using_ddo():
    # create an empty ddo
    test_id = secrets.token_hex(32)
    ddo = DDO()
    assert ddo
    private_keys = []
    for public_key_store_type in public_key_store_types:
        private_keys.append(ddo.add_signature(public_key_store_type, is_embedded=True))
    assert len(private_keys) == len(public_key_store_types)
    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)
    # add a proof to the first public_key/authentication
    ddo.add_proof(0, private_keys[0])
    ddo_text_proof = ddo.as_text()
    assert ddo_text_proof
    assert ddo.validate_proof()

    ddo_text_proof_hash = ddo.calculate_hash()
    assert ddo_text_proof_hash
    did, assigned_ddo = did_generate_from_ddo(test_id, ddo)

    assert (ddo.calculate_hash() == assigned_ddo.calculate_hash())
    assert assigned_ddo.validate_proof()

    # check to see if did is valid against the new ddo
    assert did_validate(did, test_id, assigned_ddo)

    # check to see if did is valid against the old ddo
    assert did_validate(did, test_id, ddo)


def test_load_ddo_json():
    # TODO: Fix
    SAMPLE_DDO_PATH = pathlib.Path.cwd() / 'tests' / 'resources' / 'ddo' / 'ddo_sample1.json'
    assert SAMPLE_DDO_PATH.exists(), "{} does not exist!".format(SAMPLE_METADATA_PATH)
    with open(SAMPLE_DDO_PATH) as f:
        SAMPLE_DDO_JSON_DICT = json.load(f)

    SAMPLE_DDO_JSON_STRING = json.dumps(SAMPLE_DDO_JSON_DICT)

    this_ddo = DDO(json_text = SAMPLE_DDO_JSON_STRING)
    service = this_ddo.get_service('Metadata')
    assert service
    assert service.get_type() == 'Metadata'
    values = service.get_values()
    assert values['metadata']


def test_ddo_dict():
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ddo1 = DDO(json_filename=sample_ddo_path)
    assert ddo1.is_valid
    assert len(ddo1.public_keys) == 3
    assert ddo1.did == 'did:op:3597a39818d598e5d60b83eabe29e337d37d9ed5af218b4af5e94df9f7d9783a'
