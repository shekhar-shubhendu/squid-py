"""
    DID Lib to do DID's and DDO's

"""

import re

from web3 import (
    Web3
)


def did_generate(id, path = None, fragment = None, method = 'ocean'):

    method = re.sub('[^a-z0-9]', '', method.lower())
    id = re.sub('[^a-zA-Z0-9\-\.]', '', id)
    did = ['did:', method, ':', id]
    if path:
        did.append('/')
        did.append(path)
    if fragment:
        did.append('#')
        did.append(fragment)
    return "".join(did)
