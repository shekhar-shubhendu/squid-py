import logging
import time
from collections import namedtuple
from threading import Thread

Signature = namedtuple('Signature', ('v', 'r', 's'))


def sign(web3, account_address, message):
    return web3.eth.sign(account_address, message)


def get_balance(web3, account_address, block_identifier):
    return web3.eth.getBalance(account_address, block_identifier)


def watch_event(contract_name, event_name, callback, interval, fromBlock=0, toBlock='latest', filters=None, ):
    event_filter = install_filter(
        contract_name, event_name, fromBlock, toBlock, filters
    )
    event_filter.poll_interval = interval
    Thread(
        target=watcher,
        args=(event_filter, callback),
        daemon=True,
    ).start()
    return event_filter


def install_filter(contract, event_name, fromBlock=0, toBlock='latest', filters=None):
    # contract_instance = self.contracts[contract_name][1]
    event = getattr(contract.events, event_name)
    event_filter = event.createFilter(
        fromBlock=fromBlock, toBlock=toBlock, argument_filters=filters
    )
    return event_filter


def to_32byte_hex(web3, val):
    return web3.toBytes(val).rjust(32, b'\0')


def split_signature(web3, signature):
    v = web3.toInt(signature[-1])
    r = to_32byte_hex(web3, int.from_bytes(signature[:32], 'big'))
    s = to_32byte_hex(web3, int.from_bytes(signature[32:64], 'big'))
    if v != 27 and v != 28:
        v = 27 + v % 2
    return Signature(v, r, s)


# properties

@property
def network_name(web3):
    """Give the network name."""
    network_id = web3.version.network
    switcher = {
        1: 'Main',
        2: 'orden',
        3: 'Ropsten',
        4: 'Rinkeby',
        42: 'Kovan',
    }
    return switcher.get(network_id, 'development')


# static methods
def watcher(event_filter, callback):
    while True:
        try:
            events = event_filter.get_all_entries()
        except ValueError as err:
            # ignore error, but log it
            print('Got error grabbing keeper events: ', str(err))
            events = []

        for event in events:
            callback(event)
            # time.sleep(0.1)

        # always take a rest
        time.sleep(0.1)


def convert_to_bytes(web3, data):
    return web3.toBytes(text=data)


def convert_to_string(web3, data):
    return web3.toHex(data)


def convert_to_text(web3, data):
    return web3.toText(data)
