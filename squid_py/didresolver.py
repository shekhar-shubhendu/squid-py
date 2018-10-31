"""
     DID Resolver Class

"""
import logging

from eth_abi import (
    decode_single,
)

from web3 import (
    Web3,
)

from squid_py.exceptions import (
    OceanDIDCircularReference,
    OceanDIDNotFound,
    OceanDIDUnknownValueType
)

DIDREGISTRY_EVENT_NAME = 'DIDAttributeRegistered'

VALUE_TYPE_DID =        0
VALUE_TYPE_DID_REF =    1
VALUE_TYPE_URL =        2
VALUE_TYPE_DDO =        3


logger = logging.getLogger()

class DIDResolver():

    def __init__(self, ocean, is_cache = True):
        self._web3 = ocean._web3
        self._didregistry = ocean.keeper.didregistry
        if not self._didregistry:
            raise ValueError('Cannot load didregistry contract object')

        # TODO: FIX ME!
        # the current ABI is out of sync with the keeper-contract build
        # so hard coding the signature !
        self._event_signature = Web3.sha3(text="{}(bytes32,address,uint8,bytes32,string,uint256)".format(DIDREGISTRY_EVENT_NAME)).hex()
        # self._event_signature = self._didregistry.get_event_signature(DIDREGISTRY_EVENT_NAME)
        if not self._event_signature:
            raise ValueError('Cannot find Event {} signature'.format(DIDREGISTRY_EVENT_NAME))

        self._cache = None
        if is_cache:
            self._cache = {}

    def clear_cache(self):
        if self._cache:
            self._cache = {}

    def resolve(self, did, max_hop_count = 0):
        """
            Resolve a DID to an URL/DDO or later an internal/extrenal DID

            :param did:             32 byte value to resolver, this is part of the ocean DID did:op:<32 byte value>
            :param max_hop_count:   max number of hops allowed to find the destination URL/DDO
            :return string URL or DDO of the resolved DID
            :return None if the DID cannot be resolved

            :raises TypeError - on non 32byte value as the DID
            :raises TypeError - on any of the resolved values are not string/DID bytes.
            :raises OceanDIDCircularReference - on the chain being pointed back to itself.
            :rasies OceanDIDNotFound    - if no DID can be found to resolve.

        """
        if not isinstance(did, bytes):
            raise TypeError('You must provide a 32 Byte value')

        result = None
        did_visited = {}

        # resolve a DID to a URL or DDO
        data = self.get_did(did)
        hop_count = 0
        while data and ( max_hop_count == 0 or hop_count < max_hop_count):
            if data['value_type'] == VALUE_TYPE_URL or data['value_type'] == VALUE_TYPE_DDO:
                logger.info('found did {0} -> {1}'.format(Web3.toHex(did), data['value']))
                if data['value']:
                    try:
                        result = data['value'].decode('utf8')
                    except:
                        raise TypeError('Invalid string (URL or DDO) data type for a DID value at {}'.format(Web3.toHex(did)))
                data = None
                break
            elif data['value_type'] == VALUE_TYPE_DID:
                logger.info('found did {0} -> did:op:{1}'.format(Web3.toHex(did), data['value']))
                try:
                    did = Web3.toBytes(hexstr=data['value'].decode('utf8'))
                except:
                    raise TypeError('Invalid data type for a DID value at {}'.format(Web3.toHex(did)))
                result = did
            elif data['value_type'] == VALUE_TYPE_DID_REF:
                # at the moment the same method as DID, get the hexstr and convert to bytes
                logger.info('found did {0} -> #{1}'.format(Web3.toHex(did), data['value']))
                try:
                    did = Web3.toBytes(hexstr=data['value'].decode('utf8'))
                except:
                    raise TypeError('Invalid data type for a DID value at {}'.format(Web3.toHex(did)))
                result = did
            else:
                raise OceanDIDUnknownValueType('Unknown value type {}'.format(data['value_type']))

            data = None
            if did:
                if did not in did_visited:
                    did_visited[did] = True
                else:
                    raise OceanDIDCircularReference('circular reference found at did {}'.format(Web3.toHex(did)))
                data = self.get_did(did)

            hop_count = hop_count + 1
        return result


    def get_did(self, did):
        # return a did value and value type from the block chain event record using 'did'
        # if the cache is enabled, then get this from the cache if available
        result = None

        if self._cache:
            if did in self._cache:
                return self._cache[did]

        block_number = self._didregistry.get_update_at(did)
        if block_number == 0:
            raise OceanDIDNotFound('cannot find DID {}'.format(Web3.toHex(did)))

        block_filter = self._web3.eth.filter({
            'fromBlock': block_number,
            'toBlock': block_number,
            'topics': [self._event_signature, Web3.toHex(did)]
        })
        log_items = block_filter.get_all_entries()
        if log_items and len(log_items) > 0:
            log_item = log_items[len(log_items) - 1]

            # TODO: The contract currently has a different event variable sequence, we will need to change this to ..
            # value, value_type, block_number = '(string,uint8,uint256)'
            value_type, value, block_number = decode_single('(uint8,string,uint256)', Web3.toBytes(hexstr=log_item['data']))
            result = {
                'value_type': value_type,
                'value': value
            }
        if self._cache:
            self._cache[did] = result
        return result
