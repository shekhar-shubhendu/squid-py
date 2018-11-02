import os.path
import time
import json
import pathlib

from web3 import Web3

import squid_py.acl as acl
from squid_py.ddo import DDO
from squid_py.ocean import Ocean
from squid_py.utils import convert_to_string

SAMPLE_METADATA_PATH = os.path.join(pathlib.Path.cwd(), 'tests', 'sample_metadata1.json')
assert SAMPLE_METADATA_PATH.exists()
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA = json.load(f)


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
    ocean = Ocean('config_local.ini')
    market = ocean.keeper.market
    token = ocean.keeper.token
    auth = ocean.keeper.auth
    service_agreement = ocean.keeper.service_agreement

    accounts = ocean.get_accounts().keys()
    publisher_account = accounts[0]
    consumer_account = accounts[1]
    assert market.request_tokens(2000, publisher_account)
    assert market.request_tokens(2000, consumer_account)

    # 1. Aquarius register an asset
    asset_id = market.register_asset(SAMPLE_METADATA['base']['name'], SAMPLE_METADATA['base']['description'], asset_price, publisher_account)
    assert market.check_asset(asset_id)
    assert asset_price == market.get_asset_price(asset_id)

    SAMPLE_METADATA['assetId'] = Web3.toHex(asset_id)
    # ocean.metadata.register_asset(json_dict)
    expiry = int(time.time() + expire_seconds)

    # token.token_approve(Web3.toChecksumAddress(market.address), asset_price, consumer_account)

    # buyer_balance_start = token.get_token_balance(consumer_account)
    # seller_balance_start = token.get_token_balance(publisher_account)
    # print('starting buyer balance = ', buyer_balance_start)
    # print('starting seller balance = ', seller_balance_start)
    #
    # print('buyer balance = ', token.get_token_balance(consumer_account))
    # print('seller balance = ', token.get_token_balance(publisher_account))
    # ocean.metadata.retire_asset_metadata(convert_to_string(asset_id))


    #####################################
    # Service Agreement Template
    #
    # Setup a service agreement template

    # prepare ddo to use in service agreement
    service_agreement_id = 1000
    ddo = DDO.from_json_file(os.path.join(pathlib.Path.cwd(), 'tests', 'resources', 'ddo', 'ddo_sa_sample.json'))

    #####################################
    # Service Agreement
    service_definition_id = ''
    timeout = 0
    # execute service agreement
    values_per_condition = []
    for condition in ddo.conditions:
        values = []
        values_per_condition.append(values)
    service_agreement.execute_service_agreement(ddo, consumer_account, service_definition_id, timeout, values_per_condition)

    # process ExecuteAgreement event
    # verify consumer balance
    # lockPayment
    # process PaymentLocked event
    # verify consumer balance
    # verify PaymentConditions contract balance

    # grantAccess
    # process AccessGranted event

    # releasePayment
    # process PaymentReleased event
    # verify publisher balance

    # verify consumer balance
    # Repeate execute agreement, lock payment
    # process events
    # verify consumer balance
    # try refundPayment before timeout, should fail
    # wait until timeout occurs
    # refundPayment, should get refund processed
    # process PaymentRefund event
    # verify consumer funds has the original funds returned.

