"""
    Helper functions in using web3 module

"""

from web3 import Web3


def convert_to_bytes(data):
    return Web3.toBytes(text=data)


def convert_to_string(data):
    return Web3.toHex(data)


def convert_to_text(data):
    return Web3.toText(data)
