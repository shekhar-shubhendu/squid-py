"""
"""

import logging
import os
from squid_py.ocean import Ocean
from squid_py.asset import Asset
from squid_py.ddo import DDO
import json
import pathlib
import pytest


# Disable low level loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

def test_create_asset_simple():
    # An asset can be be created directly
    asset1 = Asset(asset_id='TestID', publisher_id='TestPID', price = 0, ddo=None)
    assert not asset1.is_valid_did()

    # Can gen the DID locally BUT it requires a DDO!
    with pytest.raises(AttributeError):
        asset1.generate_did()


def test_create_asset_ddo_file():
    # An asset can be created directly from a DDO .json file
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    asset = Asset.from_ddo_json_file(sample_ddo_path)

    assert isinstance(asset.ddo, DDO)

    print(asset.metadata)

def test_register_data_market():
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
    asset.generate_did()

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

def test_register_asset_aquarius():
    """
    Setup accounts and asset, register this asset on Aquarius (MetaData)
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
    asset.generate_did()

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
def test_check_data():

    pass


def test_ocean_metadata():
    """
    Low level test directly on the metadata store object
    :return:
    """
    ocean = Ocean('config_local.ini')
    # Instantiate a new Asset

    # First, get all currently registered asset ID's
    meta_data_assets = ocean.metadata.list_assets()
    print("Currently registered assets:")
    print(meta_data_assets['assetsIds'])

    # If this asset is already registered, remove it from the metadatastore
    if SAMPLE_METADATA1['assetId'] in meta_data_assets['assetsIds']:
        print("Removing asset {}".format(SAMPLE_METADATA1['assetId']))
        ocean.metadata.get_asset_metadata(SAMPLE_METADATA1['assetId'])
        ocean.metadata.retire_asset_metadata(SAMPLE_METADATA1['assetId'])

    # Publish the metadata
    print("Publishing")
    asset = ocean.metadata.publish_asset_metadata(SAMPLE_METADATA1)

    assert len(ocean.metadata.search(search_query={"text": "Office"})) == 1
    assert ocean.metadata.get_asset_metadata(asset['assetId'])['base']['name'] == asset['base']['name']
    aquarius_assets = ocean.metadata.list_assets()

    print("Currently registered assets:")
    print(aquarius_assets)
    # for ass in aquarius_assets:
    #     print(ass)
        # print("ASSET:",ass['assetsIds'])
    # print(aquarius_assets)
    # Retire the metadata
    ocean.metadata.retire_asset_metadata(asset['assetId'])

    assert len(ocean.metadata.search(search_query={"text": "Office"})) == 0

def test_ocean_register():
    # Create 2 asset objects
    this_asset = Asset()

def _test_ocean_provider():
    ocean_provider = Ocean_Legacy(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    asset = ocean_provider.metadata.publish_asset_metadata(json_dict)
    assert len(ocean_provider.metadata.search(search_query={"text": "Office"})) == 1
    assert ocean_provider.metadata.get_asset_metadata(asset['assetId'])['base']['name'] == asset['base']['name']
    ocean_provider.metadata.retire_asset_metadata(asset['assetId'])

def _test_ocean_aquarius():
    ocean_aquarius = Ocean_Legacy(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    asset = ocean_aquarius.metadata.publish_asset_metadata(json_dict)
    assert len(ocean_aquarius.metadata.search(search_query={"text": "Office"})) == 1
    assert ocean_aquarius.metadata.get_asset_metadata(asset['assetId'])['base']['name'] == asset['base']['name']
    ocean_aquarius.metadata.retire_asset_metadata(asset['assetId'])
