"""
    Test ocean class

"""

import logging
import os
import pathlib
import json

import pytest
from ocean.ocean import Ocean
from ocean.metadata_agent import METADATA_AGENT_ENDPOINT_NAME

CONTRACTS_PATH = './artifacts'
OCEAN_URL = 'http://localhost:8545'

METADATA_STORAGE_URL = 'http://13.67.33.157:8080'
# METADATA_STORAGE_URL = 'http://localhost:8080'
METADATA_STORAGE_AUTH = 'QWxhZGRpbjpPcGVuU2VzYW1l'
METADATA_SAMPLE_PATH = pathlib.Path.cwd() / 'tests' / 'resources' / 'metadata' / 'sample_metadata1.json'


def test_ocean_instance():
    # create an ocean object
    ocean = Ocean(OCEAN_URL, CONTRACTS_PATH, metadata_agent_auth=METADATA_STORAGE_AUTH)
    assert ocean.client
    assert ocean.client.keeper
    assert ocean.client.web3
    assert ocean.client.accounts
    agent_account = ocean.client.accounts[0]

    # test register a new metadata storage agent
    agent, password = ocean.register_agent_metadata(METADATA_STORAGE_URL, agent_account)
    assert agent
    assert password
    assert agent.did
    assert agent.ddo

    # test getting the agent from a DID
    agent = ocean.get_agent(agent.did)
    assert agent
    assert not agent.is_empty

    # load in the sample metadata
    assert METADATA_SAMPLE_PATH.exists(), "{} does not exist!".format(METADATA_SAMPLE_PATH)
    metadata = None
    with open(METADATA_SAMPLE_PATH, 'r') as file_handle:
        metadata = json.load(file_handle)
    assert metadata

    # test registering an asset
    asset = ocean.register_asset(metadata['base'], agent.did)
    assert asset

    # start to test getting the asset from storage
    asset_did = "{0}/{1}".format(agent.did, asset.asset_id)
    found_asset = ocean.get_asset(asset_did)
