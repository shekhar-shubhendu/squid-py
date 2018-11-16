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

METADATA_STORAGE_URL = 'http://localhost:8080'
METADATA_SAMPLE_PATH = pathlib.Path.cwd() / 'tests' / 'resources' / 'metadata' / 'sample_metadata1.json'


def test_ocean_instance():
    # create an ocean object
    ocean = Ocean(OCEAN_URL, CONTRACTS_PATH)
    assert ocean.client
    assert ocean.client.keeper
    assert ocean.client.web3
    assert ocean.client.accounts
    agent_account = ocean.client.accounts[0]

    # test register a new agent
    agent = ocean.register_agent(METADATA_AGENT_ENDPOINT_NAME, METADATA_STORAGE_URL, agent_account)
    assert agent
    assert agent.did
    assert agent.ddo
    assert agent.ddo_password

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
    asset = ocean.register_asset(metadata, agent.did)
    assert asset

