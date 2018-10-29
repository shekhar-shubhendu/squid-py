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
def did_generate(did_id, path = None, fragment = None, method = 'op'):

    method = re.sub('[^a-z0-9]', '', method.lower())
    did_id = re.sub('[^a-zA-Z0-9-.]', '', did_id)
    did = ['did:', method, ':', did_id]
    if path:
        did.append('/')
        did.append(path)
    if fragment:
        did.append('#')
        did.append(fragment)
    return "".join(did)

# generate a base did-id, using user defined id, and ddo
def did_generate_base_id(did_id, ddo):
    values = []
    values.append(did_id)
    # remove the leading '0x' on the DDO hash
    values.append(Web3.toHex(ddo.calculate_hash())[2:])
    # return the hash as a string with no leading '0x'
    return Web3.toHex(Web3.sha3(text="".join(values)))[2:]

# generate a new DID from a configured DDO, returns the new DID, and a new DDO with the id values already assigned
def did_generate_from_ddo(did_id, ddo, path = None, fragment = None, method = 'op'):
    base_id = did_generate_base_id(did_id, ddo)
    did =  did_generate(base_id, method = method)
    assigned_ddo = ddo.create_new(did)
    return did_generate(base_id, path, fragment, method), assigned_ddo

# validate a DID and check to see it matches the user defined 'id', and DDO
def did_validate(did, did_id, ddo):
    base_id = did_generate_base_id(did_id, ddo)
    did_items = did_parse(did)
    if did_items:
        return did_items['id'] == base_id
    return False

# parse a DID into it's parts
def did_parse(did):
    result = None
    if not isinstance(did, str):
        raise TypeError('DID must be a string')

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

def is_did_valid(did):
    """
        Return True if the did is a valid DID with the method name 'op' and the id
        in the Ocean format
    """
    result = did_parse(did)
    if result:
        return result['method'] == 'op' and re.match('^[0-9A-Fa-f]{1,64}$', result['id'])
    return False


def did_generate_from_id(did_id, method='op'):

    if isinstance(did_id, bytes):
        did_id = Web3.toHex(did_id)

    # remove leading '0x' of a hex string
    if isinstance(did_id, str):
        did_id = re.sub('^0x', '', did_id)
    else:
        raise TypeError("did id must be a hex string or bytes")

    # test for zero address
    if Web3.toBytes(hexstr=did_id) == b'':
        did_id = '0'
    return 'did:{0}:{1}'.format(method, did_id)

def get_id_from_did(did):
    if is_did_valid(did):
        result = did_parse(did)
        if result:
            return re.sub('^0x', '', Web3.toHex(hexstr=result['id']))
    return None
