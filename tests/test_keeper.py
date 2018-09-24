from squid_py.utils.web3_helper import Web3Helper
from squid_py.keeper.market import Market
from squid_py.keeper.token import Token
from squid_py.keeper.auth import Auth
from squid_py.ocean import Ocean
import time


def test_keeper():
    expire_seconds = 9999999999
    ocean = Ocean(host='http://localhost', port=8545, config_path='config_local.ini')
    market = ocean.market
    # token = Token(helper)
    # auth = Token(helper)
    provider_account = ocean.helper.web3.eth.accounts[0]
    consumer_account = ocean.helper.web3.eth.accounts[1]
    assert market.request_tokens(2000, provider_account)
    assert market.request_tokens(2000, consumer_account)

    # 1. Provider register an asset
    asset_id = market.register_asset('description', 'name', 100, provider_account)
    # TODO wait until register is mined
    assert market.check_asset(asset_id)
    assert 100 == market.get_asset_price(asset_id)
    # expiry = int(time.time() + expire_seconds)
    # req = auth.initiateAccessRequest(asset_id,
    #                                         provider_account,
    #                                         pubkey,
    #                                         expiry,
    #                                         transact={'from': consumer_account})
