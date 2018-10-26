import json

from squid_py.ocean import Ocean


def test_aquarius():
    ocean_provider = Ocean(config_file='config_local.ini')
    asset = ocean_provider.metadata.publish_asset_metadata(json.load(open('tests/resources/ddo/ddo_sample1.json','r')))
    assert len(ocean_provider.metadata.search(search_query={"text": "Office"})) == 1
    ocean_provider.metadata.update_asset_metadata(json.load(open('tests/resources/ddo/ddo_sample2.json', 'r')))
    assert ocean_provider.metadata.get_asset_metadata(asset['id'])['authentication'] == asset['authentication']
    ocean_provider.metadata.retire_asset_metadata(asset['id'])