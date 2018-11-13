"""
    Test ocean class

"""

import logging
import os

import pytest
from web3 import Web3

from squid_py.config import Config
from squid_py.ocean.ocean import Ocean
from squid_py.utils import utilities


def test_ocean_instance():
    path_config = 'config_local.ini'
    os.environ['CONFIG_FILE'] = path_config
    ocean = Ocean(os.environ['CONFIG_FILE'])
    ocean.print_config()
    assert ocean.keeper.token is not None

    # There is ONE Web3 instance
    assert ocean.keeper.market.web3 is ocean.keeper.auth.web3 is ocean.keeper.token.web3

    ocean.print_config()


def test_accounts():
    os.environ['CONFIG_FILE'] = 'config_local.ini'
    ocean = Ocean(os.environ['CONFIG_FILE'])
    for address in ocean.accounts:
        print(ocean.accounts[address])

    # These accounts have a positive ETH balance
    for address, account in ocean.accounts.items():
        assert account.ether_balance >= 0
        assert account.ocean_balance >= 0


def test_token_request():
    ocean = Ocean('config_local.ini')

    amount = 2000

    # Get the current accounts, assign 2
    aquarius_address = list(ocean.accounts)[0]
    consumer_address = list(ocean.accounts)[1]

    # Start balances for comparison
    aquarius_start_eth = ocean.accounts[aquarius_address].ether_balance
    aquarius_start_ocean = ocean.accounts[aquarius_address].ocean_balance

    # Make requests, assert success on request
    rcpt = ocean.accounts[aquarius_address].request_tokens(amount)
    ocean._web3.eth.waitForTransactionReceipt(rcpt)
    rcpt = ocean.accounts[consumer_address].request_tokens(amount)
    ocean._web3.eth.waitForTransactionReceipt(rcpt)

    # Update and print balances
    # Ocean.accounts is a dict address: account
    for address in ocean.accounts:
        print(ocean.accounts[address])
    aquarius_current_eth = ocean.accounts[aquarius_address].ether_balance
    aquarius_current_ocean = ocean.accounts[aquarius_address].ocean_balance

    # Confirm balance changes
    assert ocean.accounts[aquarius_address].get_balance().eth == aquarius_current_eth
    assert ocean.accounts[aquarius_address].get_balance().ocn == aquarius_current_ocean
    assert aquarius_current_eth < aquarius_start_eth
    assert aquarius_current_ocean == aquarius_start_ocean + amount


def _test_ocean_contracts_legacy():
    os.environ['CONFIG_FILE'] = 'config_local.ini'
    os.environ['KEEPER_URL'] = 'http://0.0.0.0:8545'
    ocean = Ocean_Legacy()
    assert ocean.contracts.token is not None
    assert ocean.keeper_url == os.environ['KEEPER_URL']


def _test_ocean_contracts_with_conf(caplog):
    caplog.set_level(logging.DEBUG)
    # Need to ensure config.ini is populated!
    ocean = Ocean_Legacy(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    config = Config('config_local.ini')
    validate_market_addess = ocean.web3.toChecksumAddress(config.get(KEEPER_CONTRACTS, 'market.address'))
    assert ocean.contracts.market.address == validate_market_addess
    assert ocean.address_list
    assert ocean.address_list['market'] == validate_market_addess
    assert ocean.gas_limit == int(config.get(KEEPER_CONTRACTS, 'gas_limit'))
    assert ocean.aquarius_url == 'http://localhost:5000'


def test_split_signature():
    signature = b'\x19\x15!\xecwnX1o/\xdeho\x9a9\xdd9^\xbb\x8c2z\x88!\x95\xdc=\xe6\xafc\x0f\xe9\x14\x12\xc6\xde\x0b\n\xa6\x11\xc0\x1cvv\x9f\x99O8\x15\xf6f\xe7\xab\xea\x982Ds\x0bX\xd9\x94\xa42\x01'
    split_signature = utilities.split_signature(Web3, signature=signature)
    assert split_signature.v == 28
    assert split_signature.r == b'\x19\x15!\xecwnX1o/\xdeho\x9a9\xdd9^\xbb\x8c2z\x88!\x95\xdc=\xe6\xafc\x0f\xe9'
    assert split_signature.s == b'\x14\x12\xc6\xde\x0b\n\xa6\x11\xc0\x1cvv\x9f\x99O8\x15\xf6f\xe7\xab\xea\x982Ds\x0bX\xd9\x94\xa42'


def test_convert():
    input_text = "my text"
    print("output %s" % utilities.convert_to_string(Web3, utilities.convert_to_bytes(Web3, input_text)))
    assert utilities.convert_to_text(Web3, utilities.convert_to_bytes(Web3, input_text)) == input_text


def _test_legacy_accounts_legacy():
    ocean = Ocean_Legacy(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    assert ocean.accounts
    assert len(ocean.accounts) == 10
    for account in ocean.accounts:
        assert 'address' in account
        assert 'token' in account
        assert 'ether' in account
        assert account['ether'] > 0
        assert isinstance(account['token'], int)


def _test_aquarius_access():
    ocean = Ocean_Legacy(aquarius_url=None)
    assert ocean
    assert ocean.aquarius_url == None
    config = Config('config_local.ini')
    keeper_url = 'http://0.0.0.0:8545'
    address_list = {
        'market': config.get(KEEPER_CONTRACTS, 'market.address'),
        'token': config.get(KEEPER_CONTRACTS, 'token.address'),
        'auth': config.get(KEEPER_CONTRACTS, 'auth.address'),
    }

    ocean = Ocean_Legacy(keeper_url=keeper_url, aquarius_url=None, address_list=address_list)
    assert ocean
    assert ocean.contracts.market
    assert ocean.contracts.token
    assert ocean.contracts.auth

    # the same above but for a low level access to the modules within squid-py
    web3 = Web3(HTTPProvider(keeper_url))
    assert web3
    helper = Web3Helper(web3)
    assert helper
    contracts = Keeper(helper, get_keeper_path(), address_list)
    assert contracts


def _test_errors_raised():
    config = Config('config_local.ini')
    address_list = {
        'market': config.get(KEEPER_CONTRACTS, 'market.address'),
        'token': config.get(KEEPER_CONTRACTS, 'token.address'),
        'auth': config.get(KEEPER_CONTRACTS, 'auth.address'),
    }

    with pytest.raises(TypeError):
        ocean = Ocean_Legacy(keeper_url=None)
        assert ocean == None
        ocean = Ocean_Legacy()
        assert ocean == None

    with pytest.raises(ValueError):
        ocean = Ocean_Legacy(web3=None)
        assert ocean == None

    with pytest.raises(FileNotFoundError):
        ocean = Ocean_Legacy(config_file='error_file.txt')
        assert ocean == None

    with pytest.raises(OceanInvalidContractAddress, message="Invalid contract address for keeper contract 'market'"):
        ocean = Ocean_Legacy(address_list={'market': '0x00'})
        assert ocean == None

    with pytest.raises(OceanInvalidContractAddress, message="Invalid contract address for keeper contract 'market'"):
        ocean = Ocean_Legacy(address_list={'market': address_list['market'] + 'FF'})
        assert ocean == None

    with pytest.raises(OceanInvalidContractAddress, message="Invalid contract address for keeper contract 'market'"):
        ocean = Ocean_Legacy(address_list={'market': address_list['market'][4:]})
        assert ocean == None
