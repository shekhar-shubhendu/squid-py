import logging
import math
import pytest
import secrets

from web3 import (
    Web3,
)

from eth_abi import (
    decode_single,
)

from squid_py.ocean import Ocean

from squid_py.didresolver import (
    DIDResolver,
    VALUE_TYPE_DID,
    VALUE_TYPE_DID_REF,
    VALUE_TYPE_URL,
    VALUE_TYPE_DDO,
)

from squid_py.exceptions import (
    OceanDIDCircularReference,
    OceanDIDNotFound,
    OceanDIDUnknownValueType
)

from did_ddo_lib import (
    did_parse,
    did_validate,
    OceanDDO,
)

logger = logging.getLogger()

def test_did_resolver_raw_test():

    # test basic didregistry , contract loading and register a DID
    ocean = Ocean(config_file='config_local.ini')
    didregistry = ocean.keeper.didregistry
    register_account = list(ocean.accounts)[1]
    did_test = 'did:op:' + secrets.token_hex(32)
    did_hash = Web3.sha3(text=did_test)
    value_type = VALUE_TYPE_URL
    key_test = Web3.sha3(text='provider')
    key_test = did_hash
    value_test = 'http://localhost:5000'
    register_did = didregistry.register_attribute(did_hash, value_type, key_test, value_test, register_account)
    receipt = didregistry.get_tx_receipt(register_did)

    block_number = didregistry.get_update_at(did_hash)
    assert block_number > 0

    event_signature = didregistry.get_event_signature('DIDAttributeRegistered')
    assert event_signature

    actual_signature = Web3.toHex(receipt['logs'][0]['topics'][0])
    # print('Actual Signature', actual_signature)
    # print('event ABI', event_signature)

    calc_signature = Web3.sha3(text="DIDAttributeRegistered(bytes32,address,uint8,bytes32,string,uint256)").hex()
    # print('Calc signature', Web3.toHex(calc_signature))

    assert actual_signature == calc_signature

    # TODO: fix sync with keeper-contracts
    # at the moment assign the calc signature, since the loadad ABI sig is incorret

    event_signature = calc_signature

    # transaction_count = ocean._web3.eth.getBlockTransactionCount(block_number)
    # for index in range(0, transaction_count):
        # transaction = ocean._web3.eth.getTransactionByBlock(block_number, index)
        # print('transaction', transaction)
        # receipt = ocean._web3.eth.getTransactionReceipt(transaction['hash'])
        # print('receipt', receipt)

    # because createFilter does not return any log events
    test_filter = ocean._web3.eth.filter({'fromBlock': block_number, 'topics': [event_signature, Web3.toHex(did_hash)]})
    log_items = test_filter.get_all_entries()
    assert log_items

    assert len(log_items) > 0
    log_item = log_items[len(log_items) - 1]
    decode_value_type, decode_value = decode_single('(uint,string)', Web3.toBytes(hexstr=log_item['data']))
    assert decode_value_type == value_type
    assert decode_value.decode('utf8') == value_test

def test_did_resolver_library():

    ocean = Ocean(config_file='config_local.ini')

    register_account = list(ocean.accounts)[1]
    didregistry = ocean.keeper.didregistry
    did_id = secrets.token_hex(32)
    did_test = 'did:op:' + did_id
    value_type = VALUE_TYPE_URL
    key_test = Web3.sha3(text='provider')
    value_test = 'http://localhost:5000'

    didresolver = DIDResolver(ocean)

    # resolve URL from a direct DID ID value
    did_id_bytes = Web3.toBytes(hexstr=did_id)

    register_did = didregistry.register_attribute(did_id_bytes, value_type, key_test, value_test, register_account)
    receipt = didregistry.get_tx_receipt(register_did)

    with pytest.raises(TypeError, message = 'You must provide a 32 byte value'):
        didresolver.resolve(did_test)

    with pytest.raises(TypeError, message = 'You must provide a 32 byte value'):
        didresolver.resolve(did_id)

    result = didresolver.resolve(did_id_bytes)
    assert result == value_test

    # resolve URL from a hash of a DID string
    did_hash = Web3.sha3(text=did_test)

    register_did = didregistry.register_attribute(did_hash, value_type, key_test, value_test, register_account)
    receipt = didregistry.get_tx_receipt(register_did)
    gas_used_url = receipt['gasUsed']
    result = didresolver.resolve(did_hash)
    assert result == value_test


    # clear the cache to get next DID update
    didresolver.clear_cache()

    # test update of an already assigned DID
    value_test_new = 'http://aquarius:5000'
    register_did = didregistry.register_attribute(did_hash, value_type, key_test, value_test_new, register_account)
    receipt = didregistry.get_tx_receipt(register_did)
    result = didresolver.resolve(did_hash)
    assert result == value_test_new

    # resolve DDO from a direct DID ID value
    ddo = OceanDDO(did_test)
    ddo.add_signature()
    ddo.add_service('meta-store', value_test)
    did_id = secrets.token_hex(32)
    did_id_bytes = Web3.toBytes(hexstr=did_id)
    value_type = VALUE_TYPE_DDO


    register_did = didregistry.register_attribute(did_id_bytes, value_type, key_test, ddo.as_text(), register_account)
    receipt = didregistry.get_tx_receipt(register_did)
    gas_used_ddo = receipt['gasUsed']

    result = didresolver.resolve(did_id_bytes)
    resolved_ddo = OceanDDO(ddo_text = result)
    assert ddo.calculate_hash() == resolved_ddo.calculate_hash()

    logger.info('gas used URL: %d, DDO: %d, DDO +%d extra', gas_used_url, gas_used_ddo, gas_used_ddo - gas_used_url)

    # clear the cache to build the chain
    didresolver.clear_cache()

    value_type = VALUE_TYPE_URL
    # resolve chain of direct DID IDS to URL
    chain_length = 10
    ids = []
    for i in range(0, chain_length):
        ids.append(secrets.token_hex(32))

    
    for i in range(0, chain_length):
        did_id_bytes = Web3.toBytes(hexstr=ids[i])
        if i < len(ids) - 1:
            next_did_id = Web3.toHex(hexstr=ids[i + 1])
            logger.info('add chain {0} -> {1}'.format(Web3.toHex(did_id_bytes), next_did_id))
            register_did = didregistry.register_attribute(did_id_bytes, VALUE_TYPE_DID, key_test, next_did_id, register_account)
        else:
            logger.info('end chain {0} -> URL'.format(Web3.toHex(did_id_bytes)))
            register_did = didregistry.register_attribute(did_id_bytes, VALUE_TYPE_URL, key_test, value_test, register_account)
        receipt = didregistry.get_tx_receipt(register_did)

    did_id_bytes = Web3.toBytes(hexstr=ids[0])
    result = didresolver.resolve(did_id_bytes)
    assert result == value_test


    # clear the cache to re-build the chain
    didresolver.clear_cache()

    # test circular chain

    # get the did at the end of the chain
    did_id_bytes = Web3.toBytes(hexstr=ids[len(ids) - 1])
    # make the next DID at the end of the chain to point to the first DID
    next_did_id = Web3.toHex(hexstr=ids[0])
    logger.info('set end chain {0} -> {1}'.format(Web3.toHex(did_id_bytes), next_did_id))
    register_did = didregistry.register_attribute(did_id_bytes, VALUE_TYPE_DID, key_test, next_did_id, register_account)
    receipt = didregistry.get_tx_receipt(register_did)
    # get the first DID in the chain
    did_id_bytes = Web3.toBytes(hexstr=ids[0])
    with pytest.raises(OceanDIDCircularReference):
        didresolver.resolve(did_id_bytes)

    # clear the cache to test hop count
    didresolver.clear_cache()

    # test hop count
    hop_count = math.floor(len(ids) / 2)
    result = didresolver.resolve(did_id_bytes, hop_count)
    assert result == Web3.toBytes(hexstr=ids[hop_count])

    # test DID not found
    did_id = secrets.token_hex(32)
    did_id_bytes = Web3.toBytes(hexstr=did_id)
    with pytest.raises(OceanDIDNotFound):
        didresolver.resolve(did_id_bytes)

    # clear the cache to test unknown value
    didresolver.clear_cache()

    # test value type error on a linked DID
    register_did = didregistry.register_attribute(did_id_bytes, VALUE_TYPE_DID, key_test, value_test, register_account)
    receipt = didregistry.get_tx_receipt(register_did)

    # resolve to get the error
    with pytest.raises(TypeError):
        didresolver.resolve(did_id_bytes)


    # test value type error on a linked DID_REF
    register_did = didregistry.register_attribute(did_id_bytes, VALUE_TYPE_DID_REF, key_test, value_test, register_account)
    receipt = didregistry.get_tx_receipt(register_did)

    # resolve to get the error
    with pytest.raises(TypeError):
        didresolver.resolve(did_id_bytes)
