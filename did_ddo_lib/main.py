"""
    DID Lib to do DID's and DDO's

"""

import re

from web3 import (
    Web3
)


# generate a DID based in it's id, path, fragment and method
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

# split a DID into it's parts
def did_split(did):
    result = None
    match = re.match('^did:([a-z0-9]+):([a-zA-Z0-9\-\.]+)(.*)', did)
    if match:
        result = {
            'method' : match.group(1),
            'id': match.group(2),
            'path': None,
            'fragment': None
        }
        tail_text = match.group(3)
        if tail_text and len(tail_text) > 0:
            match = re.match('.*\#(.*)$', tail_text)
            if match:

                result['fragment'] = match.group(1)
                # now remove ending fragment '#...'
                tail_text = re.sub('\#.*$', '', tail_text)

            if len(tail_text) > 0 and tail_text[0] == '/':
                result['path'] = tail_text[1:]
    return result
