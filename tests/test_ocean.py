"""
    Test ocean class

"""

import logging
import os

from squid_py.constants import KEEPER_CONTRACTS
from squid_py.ocean import Ocean
from squid_py.utils.web3_helper import convert_to_bytes, convert_to_string, convert_to_text

from squid_py.config import (
    Config,
)

def test_ocean_contracts():
    os.environ['CONFIG_FILE'] = 'config_local.ini'
    os.environ['KEEPER_URL'] = 'http://0.0.0.0:8545'
    ocean = Ocean()
    assert ocean.token is not None
    assert ocean.keeper_url == os.environ['KEEPER_URL']
    


def test_ocean_contracts_with_conf(caplog):
    caplog.set_level(logging.DEBUG)
    # Need to ensure config.ini is populated!
    ocean = Ocean(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    config = Config('config_local.ini')
    validate_market_addess = ocean.web3.toChecksumAddress(config.get(KEEPER_CONTRACTS, 'market.address'))
    assert ocean.market.address == validate_market_addess
    assert ocean.address_list
    assert ocean.address_list['market'] == validate_market_addess
    assert ocean.gas_limit == int(config.get(KEEPER_CONTRACTS, 'gas_limit'))
    assert ocean.provider_url == 'http://localhost:5000'


def test_split_signature():
    ocean = Ocean(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    signature = b'\x19\x15!\xecwnX1o/\xdeho\x9a9\xdd9^\xbb\x8c2z\x88!\x95\xdc=\xe6\xafc\x0f\xe9\x14\x12\xc6\xde\x0b\n\xa6\x11\xc0\x1cvv\x9f\x99O8\x15\xf6f\xe7\xab\xea\x982Ds\x0bX\xd9\x94\xa42\x01'
    split_signature = ocean.helper.split_signature(signature=signature)
    assert split_signature.v == 28
    assert split_signature.r == b'\x19\x15!\xecwnX1o/\xdeho\x9a9\xdd9^\xbb\x8c2z\x88!\x95\xdc=\xe6\xafc\x0f\xe9'
    assert split_signature.s == b'\x14\x12\xc6\xde\x0b\n\xa6\x11\xc0\x1cvv\x9f\x99O8\x15\xf6f\xe7\xab\xea\x982Ds\x0bX\xd9\x94\xa42'


def test_convert():
    input_text = "my text"
    print("output %s" % convert_to_string(convert_to_bytes(input_text)))
    assert convert_to_text(convert_to_bytes(input_text)) == input_text

def test_accounts():
    ocean = Ocean(keeper_url='http://0.0.0.0:8545', config_file='config_local.ini')
    assert ocean.accounts
    assert len(ocean.accounts) == 10
    for account in ocean.accounts:
        assert 'address' in account
        assert 'token' in account
        assert 'ether' in account
        assert account['ether'] > 0
        assert isinstance(account['token'], int)
