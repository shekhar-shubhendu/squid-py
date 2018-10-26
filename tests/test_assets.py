"""
"""

import logging
import pathlib

import pytest

from squid_py.asset import Asset
from squid_py.ddo import DDO
from squid_py.ocean import Ocean

# Disable low level loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)


def test_create_asset_simple():
    # An asset can be be created directly
    asset1 = Asset(asset_id='TestID', publisher_id='TestPID', price=0, ddo=None)
    assert not asset1.is_valid_did()

    # Can gen the DID locally BUT it requires a DDO!
    with pytest.raises(AttributeError):
        asset1.generate_did()


def test_create_asset_ddo_file():
    # An asset can be created directly from a DDO .json file
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    asset1 = Asset.from_ddo_json_file(sample_ddo_path)

    assert isinstance(asset1.ddo, DDO)
    assert asset1.ddo.is_valid
    asset1.generate_did()

    assert asset1.has_metadata
    print(asset1.metadata)


def test_register_data_asset_market():
    """
    Setup accounts and asset, register this asset in Keeper node (On-chain only)
    """
    logging.debug("".format())
    ocean = Ocean('config_local.ini')
    asset_price = 100
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup 2 accounts
    ##########################################################
    aquarius_address = list(ocean.accounts)[0]
    consumer_address = list(ocean.accounts)[1]
    aquarius_acct = ocean.accounts[aquarius_address]
    consumer_acct = ocean.accounts[consumer_address]

    # ensure Ocean token balance
    if aquarius_acct.ocean == 0:
        rcpt = aquarius_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)
    if consumer_acct.ocean == 0:
        rcpt = consumer_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert aquarius_acct.get_ocean_balance() > 0
    assert consumer_acct.get_ocean_balance() > 0

    ##########################################################
    # Create an Asset with valid metadata
    ##########################################################

    asset = Asset.from_ddo_json_file(sample_ddo_path)

    ##########################################################
    # Register
    ##########################################################
    # The asset requires an ID before registration!
    asset.generate_did()

    # Call the Register function
    result = ocean.keeper.market.register_asset(asset, asset_price, aquarius_acct.address)

    # Check exists
    chain_asset_exists = ocean.keeper.market.check_asset(asset.asset_id)
    logging.info("check_asset = {}".format(chain_asset_exists))
    assert chain_asset_exists

    # Check price
    chain_asset_price = ocean.keeper.market.get_asset_price(asset.asset_id)
    assert asset_price == chain_asset_price
    logging.info("chain_asset_price = {}".format(chain_asset_price))


def test_publish_data_asset_aquarius():
    """
    Setup accounts and asset, register this asset on Aquarius (MetaData store)
    """
    logging.debug("".format())
    ocean = Ocean('config_local.ini')
    asset_price = 100
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup 2 accounts
    ##########################################################
    aquarius_address = list(ocean.accounts)[0]
    consumer_address = list(ocean.accounts)[1]
    aquarius_acct = ocean.accounts[aquarius_address]
    consumer_acct = ocean.accounts[consumer_address]

    # ensure Ocean token balance
    if aquarius_acct.ocean == 0:
        rcpt = aquarius_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)
    if consumer_acct.ocean == 0:
        rcpt = consumer_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert aquarius_acct.ocean > 0
    assert consumer_acct.ocean > 0

    ##########################################################
    # Create an Asset with valid metadata
    ##########################################################
    asset = Asset.from_ddo_json_file(sample_ddo_path)
    asset.generate_did()

    ##########################################################
    # List currently published assets
    ##########################################################
    meta_data_assets = ocean.metadata.list_assets()
    print("Currently registered assets:")
    print(meta_data_assets['assetsIds'])

    if asset.asset_id in meta_data_assets['assetsIds']:
        ocean.metadata.get_asset_metadata(asset.asset_id)
        ocean.metadata.retire_asset_metadata(asset.asset_id)
    # Publish the metadata
    this_metadata = ocean.metadata.publish_asset_metadata(asset)

    print("Publishing again should raise error")
    with pytest.raises(ValueError):
        this_metadata = ocean.metadata.publish_asset_metadata(asset)

    # TODO: Ensure returned metadata equals sent!
    # get_asset_metadata only returns 'base' key, is this correct?
    published_metadata = ocean.metadata.get_asset_metadata(asset.asset_id)

    # only compare top level keys
    assert sorted(list(asset.metadata['base'].keys())) == sorted(list(published_metadata['base'].keys()))
    # asset.metadata == published_metadata


def test_ocean_publish():
    """
    Setup accounts and asset, register this asset on Aquarius (MetaData store)
    """
    logging.debug("".format())
    ocean = Ocean('config_local.ini')
    asset_price = 100
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup account
    ##########################################################
    publisher_address = list(ocean.accounts)[0]
    publisher_acct = ocean.accounts[publisher_address]

    # ensure Ocean token balance
    if publisher_acct.ocean == 0:
        rcpt = aquarius_acct.request_tokens(200)
        ocean._web3.eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert publisher_acct.ocean > 0

    ##########################################################
    # Create an Asset with valid metadata
    ##########################################################
    asset = Asset.from_ddo_json_file(sample_ddo_path)
    asset.generate_did()

    # For this test, ensure the asset does not exist in Aquarius
    meta_data_assets = ocean.metadata.list_assets()
    if asset.asset_id in meta_data_assets['assetsIds']:
        ocean.metadata.get_asset_metadata(asset.asset_id)
        ocean.metadata.retire_asset_metadata(asset.asset_id)

    ##########################################################
    # Register using high-level interface
    ##########################################################
    ocean.register(asset, 100, publisher_acct)
