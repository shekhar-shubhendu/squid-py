"""
    Test did_lib
"""
import logging
import os
import secrets

from did_ddo_lib import (
    did_generate,
    did_parse,
    OceanDDO,
    PUBLIC_KEY_STORE_TYPE_PEM,
    PUBLIC_KEY_STORE_TYPE_JWK,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_BASE64,
)

public_key_store_types = [
    PUBLIC_KEY_STORE_TYPE_PEM,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_BASE64,
]

def test_did():

    test_id = secrets.token_hex(32)
    test_path = 'test_path'
    test_fragment = 'test_fragment'
    test_method = 'abcdefghijklmnopqrstuvwxyz0123456789'
    all_id = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-.'
    valid_did = 'did:ocean:{0}'.format(test_id)

    assert did_generate(test_id) == valid_did
    assert did_parse(valid_did)['id'] == test_id

    # all valid method values are supported
    valid_method_did = 'did:{0}:{1}'.format(test_method, test_id)
    assert did_generate(test_id, method=test_method) == valid_method_did

    # split method
    assert did_parse(valid_method_did)['method'] == test_method

    # invalid method chars are removed
    assert did_generate(test_id, method=test_method + '!@#$%^&') == valid_method_did

    # all valid method and id's are accepted
    valid_id_method_did = 'did:{0}:{1}'.format(test_method, all_id)
    assert did_generate(all_id, method=test_method) == valid_id_method_did

    # split id and method
    assert did_parse(valid_id_method_did)['method'] == test_method
    assert did_parse(valid_id_method_did)['id'] == all_id

    # invalid id values are masked out
    assert did_generate(all_id + '%^&*()_+=', method=test_method) == valid_id_method_did

    # path can be appended
    valid_path_did = 'did:ocean:{0}/{1}'.format(test_id, test_path)
    assert did_generate(test_id, test_path) == valid_path_did

    assert did_parse(valid_path_did)['path'] == test_path

    # append path and fragment
    valid_path_fragment_did = 'did:ocean:{0}/{1}#{2}'.format(test_id, test_path, test_fragment)
    assert did_generate(test_id, test_path, test_fragment) == valid_path_fragment_did

    # assert split of path and fragment
    assert did_parse(valid_path_fragment_did)['path'] == test_path
    assert did_parse(valid_path_fragment_did)['fragment'] == test_fragment

    # append fragment
    valid_fragment_did = 'did:ocean:{0}#{1}'.format(test_id, test_fragment)
    assert did_generate(test_id, fragment=test_fragment) == valid_fragment_did

    # assert split offragment
    assert did_parse(valid_fragment_did)['fragment'] == test_fragment


def test_creating_ddo():
    id = secrets.token_hex(32)
    did = did_generate(id)
    assert did
    ddo = OceanDDO(did)
    assert ddo
    private_keys = []
    for public_key_store_type in public_key_store_types:
        private_keys.append(ddo.add_signature(public_key_store_type))

    assert len(private_keys) == len(public_key_store_types)
    ddo.add_service('ocean-meta-storage', 'http://localhost:8005')

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


    ddo = OceanDDO(ddo_text = ddo_text_proof)
    assert ddo.validate()
    assert ddo.is_proof_defined()
    assert ddo.validate_proof()
    assert ddo.calculate_hash() == ddo_text_proof_hash

    ddo = OceanDDO(ddo_text = ddo_text_no_proof)
    assert ddo.validate()
    # valid proof should be false since no static proof provided
    assert not ddo.is_proof_defined()
    assert not ddo.validate_proof()
    assert ddo.calculate_hash() == ddo_text_no_proof_hash
