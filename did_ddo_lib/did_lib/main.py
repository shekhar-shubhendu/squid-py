"""
    DID Lib to do DID's and DDO's

"""

from web3 import (
    Web3
)


def generate_did(id, fragment = None):
    did = 'did:ocean:{}'.format(id)
    if fragment:
        did = '{0}/{1}'.format(did, fragment)
    return did
