from squid_py.ocean import Ocean_Legacy
import json

SAMPLE_METADATA_PATH = pathlib.Path.cwd() / 'tests' / 'sample_metadata.json'
assert SAMPLE_METADATA_PATH.exists()
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA = json.load(f)

def test_ocean_provider():
    ocean_provider = Ocean_Legacy(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    asset = ocean_provider.metadata.publish_asset_metadata(json_dict)
    assert len(ocean_provider.metadata.search(search_query={"text": "Office"})) == 1
    assert ocean_provider.metadata.get_asset_metadata(asset['assetId'])['base']['name'] == asset['base']['name']
    ocean_provider.metadata.retire_asset_metadata(asset['assetId'])
