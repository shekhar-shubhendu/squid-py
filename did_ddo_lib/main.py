"""
    DID Lib to do DID's and DDO's

"""

import re

from web3 import (
    Web3
)

from urllib.parse import (
    urlparse,
)


# generate a DID based in it's id, path, fragment and method
def did_generate(id, path = None, fragment = None, method = 'ocean'):

    method = re.sub('[^a-z0-9]', '', method.lower())
    id = re.sub('[^a-zA-Z0-9-.]', '', id)
    did = ['did:', method, ':', id]
    if path:
        did.append('/')
        did.append(path)
    if fragment:
        did.append('#')
        did.append(fragment)
    return "".join(did)

# split a DID into it's parts
def did_parse(did):
    result = None
    match = re.match('^did:([a-z0-9]+):([a-zA-Z0-9-.]+)(.*)', did)
    if match:
        result = {
            'method' : match.group(1),
            'id': match.group(2),
            'path': None,
            'fragment': None
        }
        uri_text = match.group(3)
        if uri_text and len(uri_text) > 0:
            uri = urlparse(uri_text)
            result['fragment'] = uri.fragment
            if len(uri.path) > 0:
                result['path'] = uri.path[1:]
    return result
