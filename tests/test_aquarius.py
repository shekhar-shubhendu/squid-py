import json
from squid_py.asset import Asset
from squid_py.ocean import Ocean
import pathlib

def test_aquarius():
    ocean_provider = Ocean(config_file='config_local.ini')
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    asset1 = Asset.from_ddo_json_file(sample_ddo_path)
    asset1.assign_did_from_ddo()

    # Ensure the asset it not already in database
    ocean_provider.metadata.retire_asset_metadata(asset1.asset_id)

    this_metadata = ocean_provider.metadata.publish_asset_metadata(asset1)
    assert len(ocean_provider.metadata.search(search_query={"text": "Office"})) == 1


    sample_ddo_path2 = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample2.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)
    asset2 = Asset.from_ddo_json_file(sample_ddo_path2)
    asset2.assign_did_from_ddo()

    ocean_provider.metadata.update_asset_metadata(json.load(open('tests/resources/ddo/ddo_sample2.json', 'r')))
    this_metadata = ocean_provider.metadata.get_asset_metadata(asset2.asset_id)

    assert this_metadata['authentication'] == asset2.ddo['authentication']
    ocean_provider.metadata.retire_asset_metadata(asset2.asset_id)