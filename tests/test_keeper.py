from squid_py.ocean import Ocean
import time
import squid_py.acl as acl


def test_keeper():
    expire_seconds = 9999999999
    asset_price = 100
    ocean = Ocean(host='http://localhost', port=8545, config_path='config_local.ini')
    market = ocean.market
    token = ocean.token
    auth = ocean.auth
    provider_account = ocean.helper.web3.eth.accounts[0]
    consumer_account = ocean.helper.web3.eth.accounts[1]
    assert market.request_tokens(2000, provider_account)
    assert market.request_tokens(2000, consumer_account)

    # 1. Provider register an asset
    asset_id = market.register_asset('description', 'name', asset_price, provider_account)
    assert market.check_asset(asset_id)
    assert asset_price == market.get_asset_price(asset_id)

    expiry = int(time.time() + expire_seconds)

    pubprivkey = acl.generate_encryption_keys()
    pubkey = pubprivkey.public_key
    privkey = pubprivkey.private_key
    req = auth.concise_contract.initiateAccessRequest(asset_id,
                                                      provider_account,
                                                      pubkey,
                                                      expiry,
                                                      transact={'from': consumer_account})
    receipt = ocean.helper.get_tx_receipt(req)

    send_event = auth.contract.events.AccessConsentRequested().processReceipt(receipt)
    request_id = send_event[0]['args']['_id']
