import time

from web3 import (
    Web3,
)

import squid_py.acl as acl

from squid_py import (
    Ocean,
)

from squid_py.utils import (
    convert_to_string,
)

json_dict = {"publisherId": "0x1",
             "base": {
                 "name": "UK Weather information 20111",
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


def get_events(event_filter, max_iterations=100, pause_duration=0.1):
    events = event_filter.get_new_entries()
    i = 0
    while not events and i < max_iterations:
        i += 1
        time.sleep(pause_duration)
        events = event_filter.get_new_entries()

    if not events:
        print('no events found in %s events filter.' % str(event_filter))
    return events


def process_enc_token(event):
    # should get accessId and encryptedAccessToken in the event
    print("token published event: %s" % event)


def test_keeper():
    expire_seconds = 9999999999
    asset_price = 100
    ocean = Ocean(keeper_url='http://localhost:8545', config_file='config_local.ini')
    market = ocean.contracts.market
    token = ocean.contracts.token
    auth = ocean.contracts.auth
    provider_account = ocean.helper.accounts[0]
    consumer_account = ocean.helper.accounts[1]
    assert market.request_tokens(2000, provider_account)
    assert market.request_tokens(2000, consumer_account)

    # 1. Provider register an asset
    asset_id = market.register_asset(json_dict['base']['name'],json_dict['base']['description'], asset_price, provider_account)
    assert market.check_asset(asset_id)
    assert asset_price == market.get_asset_price(asset_id)

    json_dict['assetId'] = Web3.toHex(asset_id)
    # ocean.metadata.register_asset(json_dict)
    expiry = int(time.time() + expire_seconds)

    pubprivkey = acl.generate_encryption_keys()
    pubkey = pubprivkey.public_key
    req = auth.contract_concise.initiateAccessRequest(asset_id,
                                                      provider_account,
                                                      pubkey,
                                                      expiry,
                                                      transact={'from': consumer_account})
    receipt = ocean.helper.get_tx_receipt(req)

    send_event = auth.contract.events.AccessConsentRequested().processReceipt(receipt)
    request_id = send_event[0]['args']['_id']

    assert auth.get_order_status(request_id) == 0 or auth.get_order_status(
        request_id) == 1

    # filter_token_published = ocean.helper.watch_event(auth.contract, 'EncryptedTokenPublished', process_enc_token, 0.5,
    #                                                   fromBlock='latest')

    i = 0
    while (auth.get_order_status(request_id) == 1) is False and i < 100:
        i += 1
        time.sleep(0.1)

    assert auth.get_order_status(request_id) == 1

    token.token_approve(Web3.toChecksumAddress(market.address),
                        asset_price,
                        consumer_account)

    buyer_balance_start = token.get_token_balance(consumer_account)
    seller_balance_start = token.get_token_balance(provider_account)
    print('starting buyer balance = ', buyer_balance_start)
    print('starting seller balance = ', seller_balance_start)

    send_payment = market.contract_concise.sendPayment(request_id,
                                                       provider_account,
                                                       asset_price,
                                                       expiry,
                                                       transact={'from': consumer_account, 'gas': 400000})
    receipt = ocean.helper.get_tx_receipt(send_payment)
    print('Receipt: %s' % receipt)

    print('buyer balance = ', token.get_token_balance(consumer_account))
    print('seller balance = ', token.get_token_balance(provider_account))
    ocean.metadata.retire_asset_metadata(convert_to_string(asset_id))


    # events = get_events(filter_token_published)
    # assert events
    # assert events[0].args['_id'] == request_id
    # on_chain_enc_token = events[0].args["_encryptedAccessToken"]
