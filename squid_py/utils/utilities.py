""" Utilities library, useful functions
"""


from collections import namedtuple
Signature = namedtuple('Signature', ('v', 'r', 's'))


def split_signature(web3, signature):
    """
    :param web3: Web3 instance
    :param signature: Named Tuple object
    :return:
    """
    v = web3._web3.toInt(signature[-1])
    r = web3.to_32byte_hex(int.from_bytes(signature[:32], 'big'))
    s = web3.to_32byte_hex(int.from_bytes(signature[32:64], 'big'))
    if v != 27 and v != 28:
        v = 27 + v % 2
    return Signature(v, r, s)


def network_name(web3):
    """Give the network name."""
    network_id = web3._web3.version.network
    switcher = {
        1: 'Main',
        2: 'orden',
        3: 'Ropsten',
        4: 'Rinkeby',
        42: 'Kovan',
    }
    return switcher.get(network_id, 'development')