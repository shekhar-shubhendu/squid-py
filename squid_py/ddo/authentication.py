"""

    Authentication Class
    To handle embedded public keys

"""

import json
import re

from .public_key_base import (
    PublicKeyBase,
)

class Authentication(object):

    def __init__(self, key_id, authentication_type):
        self._public_key = None
        self._public_key_id = None
        if isinstance(key_id, PublicKeyBase):
            self._public_key = key_id
        else:
            self._public_key_id = key_id
        self._type = authentication_type

    def assign_did(self, did):
        if self._public_key_id:
            if re.match('^#.*', self._public_key_id):
                self._public_key_id = did + self._public_key_id
        if self._public_key:
            self._public_key.assign_did(did)

    def get_type(self):
        return self._type

    def get_public_key_id(self):
        if self._public_key_id:
            return self._public_key_id
        if self._public_key:
            return self._public_key.get_id()
        return None

    def get_public_key(self):
        return self._public_key

    def as_text(self):
        values = {
            'type': self._type
        }
        if self._public_key:
            values['publicKey'] = self._public_key.as_text()
        elif self._public_key_id:
            values['publicKey'] = self._public_key_id
        return json.dumps(values)


    def is_valid(self):
        return self.get_public_key_id() != None and self._type != None

    def is_public_key(self):
        return self._public_key != None

    def is_key_id(self, key_id):
        if self.get_public_key_id() and self.get_public_key_id() == key_id:
            return True
        return False
