"""
    DID Lib to do DID's and DDO's

"""
import json
import datetime

from web3 import (
    Web3
)

from Crypto.PublicKey import (
 	RSA,
)

from Crypto.Cipher import (
	PKCS1_OAEP,
)

from Crypto.Signature import (
    PKCS1_v1_5
)

from Crypto.Hash import (
   SHA256
)

from base64 import (
    b64decode,
    b64encode
)
from did_lib.constants import (
    KEY_PAIR_MODULUS_BIT,
    DID_DDO_CONTEXT_URL,
)

class OceanDDO(object):

    def __init__(self, did):
        self.clear()
        self._did = did

    def clear(self):
        self._public_keys = []
        self._authentications = []
        self._services = []
        self._proof = None
        self._created = None

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
        if self._created == None:
            self._created = self._get_timestamp()

        data = {
          "@context": DID_DDO_CONTEXT_URL,
          'id': self._did,
          'created': self._created,
        }
        if len(self._public_keys) > 0:
            data['publicKey'] = self._public_keys
        if len(self._authentications) > 0:
            data['authentication'] = self._authentications
        if len(self._services) > 0:
            data['service'] = self._services
        if self._proof:
            data['proof'] = self._proof

        return json.dumps(data)

    def add_proof(self, index, private_key_pem):
        # add a static proof to the DDO, based on one of the public keys
        signer = PKCS1_v1_5.new(RSA.import_key(private_key_pem))
        sign_key = self._public_keys[index]
#        hash_ddo = Web3.toBytes(Web3.sha3(text=self.as_text()))
        self._proof = None
        ddo_hash = SHA256.new(self.as_text().encode())
        signature = signer.sign(ddo_hash)
        self._proof = {
            'type': sign_key['type'],
            'created': self._get_timestamp(),
            'creator': sign_key['id'],
            'signatureValue': str(b64encode(signature))
        }

    @property
    def public_keys(self):
        return self._public_keys

    @property
    def authentications(self):
        return self._authentications

    @property
    def services(self):
        return self._services

    def _get_timestamp(self):
        return str(datetime.datetime.now())
