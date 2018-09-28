"""
    Test did_lib
"""
import logging
import os
import secrets

from did_lib import (
    generate_did,
    OceanDDO,
)


def test_creating_ddo():
    id = secrets.token_hex(32)
    did = generate_did(id)
    assert did
    ddo = OceanDDO(did)
    assert ddo
    private_key = ddo.add_signature()
    assert private_key
    ddo.add_service('ocean-meta-storage', 'http://localhost:8005')

    assert len(ddo.public_keys) == 1
    assert len(ddo.authentications) == 1
    assert len(ddo.services) == 1

    ddo_text_no_proof = ddo.as_text()
    assert ddo_text_no_proof
    ddo.add_proof(0, private_key)
    ddo_text_proof = ddo.as_text()

    assert ddo.validate_proof()
    print(ddo_text_proof)

    ddo = OceanDDO(ddo_text = ddo_text_proof)
    assert ddo.validate()
    assert ddo.is_proof_defined()
    assert ddo.validate_proof()

    ddo = OceanDDO(ddo_text = ddo_text_no_proof)
    assert ddo.validate()
    # valid proof should be false since no static proof profided
    assert not ddo.is_proof_defined()
    assert not ddo.validate_proof()
