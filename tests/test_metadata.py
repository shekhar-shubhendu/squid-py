from squid_py.ocean import Ocean

json_dict = {"publisherId": "0x1",
             "base": {
                 "name": "UK Weather information 2011",
                 "description": "Weather information of UK including temperature and humidity",
                 "size": "3.1gb",
                 "author": "Met Office",
                 "license": "CC-BY",
                 "copyrightHolder": "Met Office",
                 "encoding": "UTF-8",
                 "compression": "zip",
                 "contentType": "text/csv",
                 "workExample": "stationId,latitude,longitude,datetime,temperature,humidity\n"
                                "423432fsd,51.509865,-0.118092,2011-01-01T10:55:11+00:00,7.2,68",
                 "contentUrls": ["https://testocnfiles.blob.core.windows.net/testfiles/testzkp.pdf"],
                 "links": [
                     {"sample1": "http://data.ceda.ac.uk/badc/ukcp09/data/gridded-land-obs/gridded-land-obs-daily/"},
                     {
                         "sample2": "http://data.ceda.ac.uk/badc/ukcp09/data/gridded-land-obs/gridded-land-obs-averages-25km/"},
                     {"fieldsDescription": "http://data.ceda.ac.uk/badc/ukcp09/"}
                 ],
                 "inLanguage": "en",
                 "tags": "weather, uk, 2011, temperature, humidity",
                 "price": 10,
                 "type": "dataset"
             },
             "curation": {
                 "rating": 0,
                 "numVotes": 0,
                 "schema": "Binary Votting"
             },
             "additionalInformation": {
                 "updateFrecuency": "yearly"
             },
             "assetId": "001"
             }


def test_ocean_provider():
    ocean_provider = Ocean(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    asset = ocean_provider.metadata.publish_asset_metadata(json_dict)
    assert len(ocean_provider.metadata.search(search_query={"text": "Office"})) == 1
    assert ocean_provider.metadata.get_asset_metadata(asset['assetId'])['base']['name'] == asset['base']['name']
    ocean_provider.metadata.retire_asset_metadata(asset['assetId'])
