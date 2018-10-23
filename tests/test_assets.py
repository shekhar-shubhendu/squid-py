"""
    Test ocean class
"""

import logging
import os
from squid_py.ocean import Ocean

class LoggerCritical:
    def __enter__(self):
        my_logger = logging.getLogger()
        my_logger.setLevel("CRITICAL")
    def __exit__(self, type, value, traceback):
        my_logger = logging.getLogger()
        my_logger.setLevel("DEBUG")

import json
import pathlib

SAMPLE_METADATA_PATH = pathlib.Path.cwd() / 'tests' / 'sample_metadata.json'
assert SAMPLE_METADATA_PATH.exists(), "{} does not exist!".format(SAMPLE_METADATA_PATH)
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA = json.load(f)

# Disable low level loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)


def test_sample_data():
    ocean = Ocean('config_local.ini')
    assert SAMPLE_METADATA
    logging.debug("Loaded metadata file {} for price: {}".format(SAMPLE_METADATA['base']['name'], SAMPLE_METADATA['base']['price']))

def test_register_data():
    ocean = Ocean('config_local.ini')
    asset_price = 100

    ##########################################################
    # Setup 2 accounts
    ##########################################################
    provider_address = list(ocean.accounts)[0]
    consumer_address = list(ocean.accounts)[1]
    provider_acct = ocean.accounts[provider_address]
    consumer_acct = ocean.accounts[consumer_address]

    # ensure Ocean token balance
    if provider_acct.ocean == 0:
        rcpt = provider_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)
    if consumer_acct.ocean == 0:
        rcpt = consumer_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert provider_acct.ocean > 0
    assert consumer_acct.ocean > 0
    ##########################################################
    # Register
    ##########################################################
    # with LoggerCritical():
    asset_id = ocean.keeper.market.register_asset(SAMPLE_METADATA['base']['name'], SAMPLE_METADATA['base']['description'], asset_price, provider_acct.address)

    assert ocean.keeper.market.check_asset(asset_id)
    assert asset_price == ocean.keeper.market.get_asset_price(asset_id)
    print(logging.Logger.manager.loggerDict)

def test_check_data():

    pass