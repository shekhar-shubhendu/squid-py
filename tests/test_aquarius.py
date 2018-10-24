from squid_py.ocean import Ocean
from squid_py.asset import Asset

import logging
import json
import pathlib

# Load samples
SAMPLE_METADATA_PATH = pathlib.Path.cwd() / 'tests/resources/metadata' / 'sample_metadata1.json'
assert SAMPLE_METADATA_PATH.exists(), "{} does not exist!".format(SAMPLE_METADATA_PATH)
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA1 = json.load(f)

SAMPLE_METADATA_PATH = pathlib.Path.cwd() / 'tests/resources/metadata' / 'sample_metadata2.json'
assert SAMPLE_METADATA_PATH.exists(), "{} does not exist!".format(SAMPLE_METADATA_PATH)
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA2 = json.load(f)

# Disable low level loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

def test_asset_class():
    asset = Asset(asset_id='TestID', publisher_id='TestPID', price = 0)
    print(asset)

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
        print("Removing asset {}".format(SAMPLE_METADATA1['assetId'] ))
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
