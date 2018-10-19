from squid_py.ocean import Ocean

import json
import pathlib

SAMPLE_METADATA_PATH = pathlib.Path.cwd() / 'tests' / 'sample_metadata.json'
assert SAMPLE_METADATA_PATH.exists(), "{} does not exist!".format(SAMPLE_METADATA_PATH)
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA = json.load(f)

def test_ocean_metadata():
    ocean = Ocean('config_local.ini')

    # Publish the metadata
    asset = ocean.metadata.publish_asset_metadata(SAMPLE_METADATA)
    assert len(ocean.metadata.search(search_query={"text": "Office"})) == 1
    assert ocean.metadata.get_asset_metadata(asset['assetId'])['base']['name'] == asset['base']['name']

    # Retire the metadata
    ocean.metadata.retire_asset_metadata(asset['assetId'])

    assert len(ocean.metadata.search(search_query={"text": "Office"})) == 0

def _test_ocean_provider():
    ocean_provider = Ocean_Legacy(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    asset = ocean_provider.metadata.publish_asset_metadata(json_dict)
    assert len(ocean_provider.metadata.search(search_query={"text": "Office"})) == 1
    assert ocean_provider.metadata.get_asset_metadata(asset['assetId'])['base']['name'] == asset['base']['name']
    ocean_provider.metadata.retire_asset_metadata(asset['assetId'])