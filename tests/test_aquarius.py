from squid_py.ocean import Ocean
from squid_py.asset import Asset

import json
import pathlib

SAMPLE_METADATA_PATH = pathlib.Path.cwd() / 'tests' / 'sample_metadata.json'
assert SAMPLE_METADATA_PATH.exists(), "{} does not exist!".format(SAMPLE_METADATA_PATH)
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA = json.load(f)


def test_asset_class():
    asset = Asset(asset_id='TestID', publisher_id='TestPID', price = 0)
    print(asset)

def test_ocean_metadata():
    ocean = Ocean('config_local.ini')
    # Instantiate a new Asset

    # Publish the metadata
    #TODO: Handle duplicate!
    try:
        asset = ocean.metadata.publish_asset_metadata(SAMPLE_METADATA)
    except:
        pass

    assert len(ocean.metadata.search(search_query={"text": "Office"})) == 1
    assert ocean.metadata.get_asset_metadata(asset['assetId'])['base']['name'] == asset['base']['name']
    aquarius_assets = ocean.metadata.list_assets()
    for ass in aquarius_assets:
        print(ass)
        # print("ASSET:",ass['assetsIds'])
    print(aquarius_assets)
    # Retire the metadata
    ocean.metadata.retire_asset_metadata(asset['assetId'])

    assert len(ocean.metadata.search(search_query={"text": "Office"})) == 0

def _test_ocean_provider():
    ocean_provider = Ocean_Legacy(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    asset = ocean_provider.metadata.publish_asset_metadata(json_dict)
    assert len(ocean_provider.metadata.search(search_query={"text": "Office"})) == 1
    assert ocean_provider.metadata.get_asset_metadata(asset['assetId'])['base']['name'] == asset['base']['name']
    ocean_provider.metadata.retire_asset_metadata(asset['assetId'])