"""
    DID Lib to do DID's and DDO's

"""

from web3 import (
    Web3
)


def did_generate(id, did_path = None, did_fragment = None, did_method = 'ocean'):

    did = ['did:', did_method, ':', id]
    if did_path:
        did.append('/')
        did.append(did_path)
    if did_fragment:
        did.append('#')
        did.append(did_fragment)
    return "".join(did)
