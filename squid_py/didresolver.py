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

from squid_py.did import did_to_id_bytes



DIDREGISTRY_EVENT_NAME = 'DIDAttributeRegistered'

VALUE_TYPE_DID = 0
VALUE_TYPE_DID_REF = 1
VALUE_TYPE_URL = 2
VALUE_TYPE_DDO = 3

logger = logging.getLogger()


class DIDResolver():
    """
    DID Resolver class
    Resolve DID to a URL/DDO
    """

    def __init__(self, web3, didregistry):
        self._web3 = web3
        self._didregistry = didregistry

        if not self._didregistry:
            raise ValueError('No didregistry contract object provided')

        self._event_signature = self._didregistry.get_event_signature(DIDREGISTRY_EVENT_NAME)
        if not self._event_signature:
            raise ValueError('Cannot find Event {} signature'.format(DIDREGISTRY_EVENT_NAME))

    def resolve(self, did, max_hop_count=0):
        """
        Resolve a DID to an URL/DDO or later an internal/extrenal DID

        :param did: 32 byte value or DID string to resolver, this is part of the ocean DID did:op:<32 byte value>
        :param max_hop_count: max number of hops allowed to find the destination URL/DDO
        :return string URL or DDO of the resolved DID
        :return None if the DID cannot be resolved

        :raises TypeError - on non 32byte value as the DID
        :raises TypeError - on any of the resolved values are not string/DID bytes.
        :raises OceanDIDCircularReference - on the chain being pointed back to itself.
        :rasies OceanDIDNotFound    - if no DID can be found to resolve.

        """

        did_bytes = did_to_id_bytes(did)

        if not isinstance(did_bytes, bytes):
            raise TypeError('You must provide a 32 Byte value')

        result = None
        did_visited = {}

        # resolve a DID to a URL or DDO
        data = self.get_did(did_bytes)
        hop_count = 0
        while data and (max_hop_count == 0 or hop_count < max_hop_count):
            if data['value_type'] == VALUE_TYPE_URL or data['value_type'] == VALUE_TYPE_DDO:
                logger.info('found did {0} -> {1}'.format(Web3.toHex(did_bytes), data['value']))
                if data['value']:
                    try:
                        result = data['value'].decode('utf8')
                    except:
                        raise TypeError('Invalid string (URL or DDO) data type for a DID value at {}'.format(Web3.toHex(did_bytes)))
                data = None
                break
            elif data['value_type'] == VALUE_TYPE_DID:
                logger.info('found did {0} -> did:op:{1}'.format(Web3.toHex(did_bytes), data['value']))
                try:
                    did_bytes = Web3.toBytes(hexstr=data['value'].decode('utf8'))
                except:
                    raise TypeError('Invalid data type for a DID value at {}'.format(Web3.toHex(did_bytes)))
                result = did_bytes
            elif data['value_type'] == VALUE_TYPE_DID_REF:
                # at the moment the same method as DID, get the hexstr and convert to bytes
                logger.info('found did {0} -> #{1}'.format(Web3.toHex(did_bytes), data['value']))
                try:
                    did_bytes = Web3.toBytes(hexstr=data['value'].decode('utf8'))
                except:
                    raise TypeError('Invalid data type for a DID value at {}'.format(Web3.toHex(did_bytes)))
                result = did_bytes
            else:
                raise OceanDIDUnknownValueType('Unknown value type {}'.format(data['value_type']))

            data = None
            if did_bytes:
                if did_bytes not in did_visited:
                    did_visited[did_bytes] = True
                else:
                    raise OceanDIDCircularReference('circular reference found at did {}'.format(Web3.toHex(did_bytes)))
                data = self.get_did(did_bytes)

            hop_count = hop_count + 1
        return result

    def get_did(self, did_bytes):
        """return a did value and value type from the block chain event record using 'did'"""
        result = None

        block_number = self._didregistry.get_update_at(did_bytes)

        if block_number == 0:
            raise OceanDIDNotFound('cannot find DID {}'.format(Web3.toHex(did_bytes)))

        block_filter = self._web3.eth.filter({
            'fromBlock': block_number,
            'toBlock': block_number,
            'topics': [self._event_signature, Web3.toHex(did_bytes)]
        })
        log_items = block_filter.get_all_entries()
        if log_items and len(log_items) > 0:
            log_item = log_items[len(log_items) - 1]
            value, value_type, block_number = decode_single('(string,uint8,uint256)', \
                                                            Web3.toBytes(hexstr=log_item['data']))
            result = {
                'value_type': value_type,
                'value': value
            }
        return result
