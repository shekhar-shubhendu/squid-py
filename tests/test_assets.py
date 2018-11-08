"""
"""

import logging
import pathlib

import pytest

from squid_py.ocean.asset import Asset
from squid_py.ddo import DDO
from squid_py.ocean.ocean import Ocean
import secrets
import json

# Disable low level loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)


def test_create_asset_from_metadata():
    sample_metadata_path = pathlib.Path.cwd() / 'tests' / 'resources' / 'metadata' / 'sample_metadata1.json'
    assert sample_metadata_path.exists(), "{} does not exist!".format(sample_metadata_path)

    # An asset can be be created directly from a metadata file/string
    asset1 = Asset.create_from_metadata_file(sample_metadata_path, 'http://localhost:5000')
    assert asset1.is_valid

    with open(sample_metadata_path) as file_handle:
        metadata = json.load(file_handle)

    # An asset can be be created directly from a metadata file/string
    asset1 = Asset.create_from_metadata(metadata, 'http://localhost:5000')
    assert asset1.is_valid


def test_create_asset_ddo_file():
    # An asset can be created directly from a DDO .json file
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    asset1 = Asset.from_ddo_json_file(sample_ddo_path)

    assert isinstance(asset1.ddo, DDO)
    assert asset1.is_valid

    assert asset1.has_metadata
    print(asset1.metadata)


def test_register_data_asset_market():
    """
    Setup accounts and asset, register this asset in Keeper node (On-chain only)
    """
    logging.debug("".format())
    ocean = Ocean('config_local.ini')
    asset_price = 100
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup 2 accounts
    ##########################################################
    aquarius_address = list(ocean.accounts)[0]
    consumer_address = list(ocean.accounts)[1]
    aquarius_acct = ocean.accounts[aquarius_address]
    consumer_acct = ocean.accounts[consumer_address]

    # ensure Ocean token balance
    if aquarius_acct.ocean == 0:
        rcpt = aquarius_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)
    if consumer_acct.ocean == 0:
        rcpt = consumer_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert aquarius_acct.ocean > 0
    assert consumer_acct.ocean > 0

    ##########################################################
    # Create an Asset with valid metadata
    ##########################################################

    asset = Asset.from_ddo_json_file(sample_ddo_path)

    ##########################################################
    # Register
    ##########################################################
    # The asset requires an ID before registration!

    # Call the Register function
    result = ocean.keeper.market.register_asset(asset, asset_price, aquarius_acct.address)

    # Check exists
    chain_asset_exists = ocean.keeper.market.check_asset(asset.asset_id)
    logging.info("check_asset = {}".format(chain_asset_exists))
    assert chain_asset_exists

    # Check price
    chain_asset_price = ocean.keeper.market.get_asset_price(asset.asset_id)
    assert asset_price == chain_asset_price
    logging.info("chain_asset_price = {}".format(chain_asset_price))


def test_publish_data_asset_aquarius():
    """
    Setup accounts and asset, register this asset on Aquarius (MetaData store)
    """
    logging.debug("".format())
    ocean = Ocean('config_local.ini')
    asset_price = 100
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup 2 accounts
    ##########################################################
    aquarius_address = list(ocean.accounts)[0]
    consumer_address = list(ocean.accounts)[1]
    aquarius_acct = ocean.accounts[aquarius_address]
    consumer_acct = ocean.accounts[consumer_address]

    # ensure Ocean token balance
    if aquarius_acct.ocean == 0:
        rcpt = aquarius_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)
    if consumer_acct.ocean == 0:
        rcpt = consumer_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert aquarius_acct.ocean > 0
    assert consumer_acct.ocean > 0

    ##########################################################
    # Create an Asset with valid metadata
    ##########################################################
    asset = Asset.from_ddo_json_file(sample_ddo_path)

    ##########################################################
    # List currently published assets
    ##########################################################
    meta_data_assets = ocean.metadata.list_assets()
    if meta_data_assets:
        print("Currently registered assets:")
        print(meta_data_assets)

    if asset.did in meta_data_assets:
        ocean.metadata.get_asset_metadata(asset.did)
        ocean.metadata.retire_asset_metadata(asset.did)
    # Publish the metadata
    this_metadata = ocean.metadata.publish_asset_metadata(asset.did, asset.ddo)
    assert(this_metadata)

    print("Publishing again should raise error")
    with pytest.raises(ValueError):
        this_metadata = ocean.metadata.publish_asset_metadata(asset.did, asset.ddo)

    # TODO: Ensure returned metadata equals sent!
    # get_asset_metadata only returns 'base' key, is this correct?
    published_metadata = ocean.metadata.get_asset_metadata(asset.did)

    assert published_metadata
    # only compare top level keys
    # assert sorted(list(asset.metadata['base'].keys())) == sorted(list(published_metadata['base'].keys()))
    # asset.metadata == published_metadata


def test_ocean_publish():
    """
    Setup accounts and asset, register this asset on Aquarius (MetaData store)
    """
    logging.debug("".format())
    ocean = Ocean('config_local.ini')
    asset_price = 100
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample2.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup account
    ##########################################################
    publisher_address = list(ocean.accounts)[0]
    publisher_acct = ocean.accounts[publisher_address]

    # ensure Ocean token balance
    if publisher_acct.ocean == 0:
        rcpt = publisher_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert publisher_acct.ocean > 0

    ##########################################################
    # Create an Asset with valid metadata
    ##########################################################
    asset = Asset.from_ddo_json_file(sample_ddo_path)

    ######################

    # For this test, ensure the asset does not exist in Aquarius
    meta_data_assets = ocean.metadata.list_assets()
    if asset.did in meta_data_assets:
        ocean.metadata.get_asset_metadata(asset.did)
        ocean.metadata.retire_asset_metadata(asset.did)

    ##########################################################
    # Register using high-level interface
    ##########################################################
    ocean.register(asset, 100, publisher_acct)
    assert asset.from_ddo_dict(ocean.resolve_did(asset.did))
