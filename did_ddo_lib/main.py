"""
    DID Lib to do DID's and DDO's

"""

from web3 import (
    Web3
)


def did_generate(id, path = None, fragment = None, method = 'ocean'):

    did = ['did:', method.lower(), ':', id]
    if path:
        did.append('/')
        did.append(path)
    if fragment:
        did.append('#')
        did.append(fragment)
    return "".join(did)
