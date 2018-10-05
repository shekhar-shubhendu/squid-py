"""
    Public key base

    Currently this class stores the public keys in the same form as in the JSON
    text data.

"""

import json
import re

from base64 import (
    b64decode,
    b64encode,
    b85encode,
    b85decode,
)

PUBLIC_KEY_STORE_TYPE_PEM = 'publicKeyPem'
PUBLIC_KEY_STORE_TYPE_JWK = 'publicKeyJwk'
PUBLIC_KEY_STORE_TYPE_HEX = 'publicKeyHex'
PUBLIC_KEY_STORE_TYPE_BASE64 = 'publicKeyBase64'
PUBLIC_KEY_STORE_TYPE_BASE85 = 'publicKeyBase85'


class PublicKeyBase(object):
    def __init__(self, key_id, **kwargs):
        self._id = key_id
        self._store_type = kwargs.get('store_type', None)
        self._value = kwargs.get('value', None)
        self._owner = kwargs.get('owner', None)
        self._type = kwargs.get('type', None)

    def get_id(self):
        return self._id

    def assign_did(self, did):
        if re.match('^#.*', self._id):
            self._id = did + self._id
        if re.match('^#.*', self._owner):
            self._owner = did + self._owner

    def get_owner(self):
        return self._owner

    # def set_owner(self, value):
        # self._owner = value

    def get_type(self):
        return self._type

    def get_store_type(self):
        return self._store_type

    def set_key_value(self, value, store_type = PUBLIC_KEY_STORE_TYPE_BASE64):
        if isinstance(value, dict):
            if PUBLIC_KEY_STORE_TYPE_HEX in value:
                self.set_key_value(value[PUBLIC_KEY_STORE_TYPE_HEX], PUBLIC_KEY_STORE_TYPE_HEX)
            elif PUBLIC_KEY_STORE_TYPE_BASE64 in value:
                self.set_key_value(value[PUBLIC_KEY_STORE_TYPE_BASE64], PUBLIC_KEY_STORE_TYPE_BASE64)
            elif PUBLIC_KEY_STORE_TYPE_BASE85 in value:
                self.set_key_value(value[PUBLIC_KEY_STORE_TYPE_BASE85], PUBLIC_KEY_STORE_TYPE_BASE85)
            elif PUBLIC_KEY_STORE_TYPE_JWK in value:
                self.set_key_value(value[PUBLIC_KEY_STORE_TYPE_JWK], PUBLIC_KEY_STORE_TYPE_JWK)
            elif PUBLIC_KEY_STORE_TYPE_PEM in value:
                self.set_key_value(value[PUBLIC_KEY_STORE_TYPE_PEM], PUBLIC_KEY_STORE_TYPE_PEM)
        else:
            self._value = value
            self._store_type = store_type

    def set_encode_key_value(self, value, store_type):
        self._store_type = store_type
        if store_type == PUBLIC_KEY_STORE_TYPE_HEX:
            self._value = value.hex()
        elif store_type == PUBLIC_KEY_STORE_TYPE_BASE64:
            self._value = b64encode(value).decode()
        elif store_type == PUBLIC_KEY_STORE_TYPE_BASE85:
            self._value = b85encode(value).decode()
        elif store_type == PUBLIC_KEY_STORE_TYPE_JWK:
            # TODO: need to decide on which jwk library to import?
            raise NotImplementedError
        else:
            self._value = value
        return value

    def get_decode_value(self):
        if self._store_type == PUBLIC_KEY_STORE_TYPE_HEX:
            value = bytes.fromhex(self._value)
        elif self._store_type == PUBLIC_KEY_STORE_TYPE_BASE64:
           value = b64decode(self._value)
        elif self._store_type == PUBLIC_KEY_STORE_TYPE_BASE85:
           value = b85decode(self._value)
        elif self._store_type == PUBLIC_KEY_STORE_TYPE_JWK:
            # TODO: need to decide on which jwk library to import?
            raise NotImplementedError
        else:
            value = self._value
        return value

    def get_value(self):
        return self._value

    def as_text(self):
        values = {
            'id': self._id,
            'type': self._type,
        }
        values[self._store_type] = self._value
        if self._owner:
            values['owner'] = self._owner
        return json.dumps(values)

    def is_valid(self):
        return self._id and self._type

    def get_authentication_type(self):
        raise NotImplementedError
