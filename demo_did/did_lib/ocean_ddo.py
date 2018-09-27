"""
    DID Lib to do DID's and DDO's

"""
import json

from web3 import (
    Web3
)

from Crypto.PublicKey import (
 	RSA,
)

from Crypto.Cipher import (
	PKCS1_OAEP,
)

from did_lib.constants import (
    KEY_PAIR_MODULUS_BIT,
    DID_DDO_CONTEXT_URL,
)

class OceanDDO(object):

    def __init__(self, did):
        self._did = did
        self.clear()

    def clear(self):
        self._public_keys = []
        self._authentications = []
        self._services = []

    def add_signature(self):
        key_pair = RSA.generate(KEY_PAIR_MODULUS_BIT, e=65537)
        public_key = key_pair.publickey()
        public_key_pem = public_key.exportKey("PEM")
        private_key_pem = key_pair.exportKey("PEM")
        key_type = 'RsaVerificationKey2018'
        index = len(self._public_keys) + 1
        key_id = '{0}#keys={1}'.format(self._did, index)

        row = {
            'id': key_id,
            'type': key_type,
            'owner': self._did,
            'publicKeyPem': str(public_key_pem),
        }
        self._public_keys.append(row)
        row = {
            'id' : key_id,
            'publicKey' : key_type,
        }
        self._authentications.append(row)
        return private_key_pem


    def add_service(self, service_type, service_endpoint):
        row = {
            'type' : service_type,
            'serviceEndpoint': service_endpoint,
        }
        self._services.append(row)

    def as_text(self):
        data = {
          "@context": DID_DDO_CONTEXT_URL,
          'id': self._did,
          'publicKey': self._public_keys,
          'authentication': self._authentications,
          'service': self._services,
        }
        return json.dumps(data)

    @property
    def public_keys(self):
        return self._public_keys

    @property
    def authentications(self):
        return self._authentications

    @property
    def services(self):
        return self._services
