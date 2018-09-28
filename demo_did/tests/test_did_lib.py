"""
    Test did_lib
"""
import logging
import os
import secrets

from did_lib import (
    generate_did,
    OceanDDO,
    PUBLIC_KEY_TYPE_PEM,
    PUBLIC_KEY_TYPE_JWK,
    PUBLIC_KEY_TYPE_HEX,
    PUBLIC_KEY_TYPE_BASE64,

)

public_key_types = [
    PUBLIC_KEY_TYPE_PEM,
    PUBLIC_KEY_TYPE_HEX,
    PUBLIC_KEY_TYPE_BASE64,
]

def test_creating_ddo():
    id = secrets.token_hex(32)
    did = generate_did(id)
    assert did
    ddo = OceanDDO(did)
    assert ddo
    private_keys = []
    for public_key_type in public_key_types:
        private_keys.append(ddo.add_signature(public_key_type))

    assert len(private_keys) == len(public_key_types)
    ddo.add_service('ocean-meta-storage', 'http://localhost:8005')

    assert len(ddo.public_keys) == len(public_key_types)
    assert len(ddo.authentications) == len(public_key_types)
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
