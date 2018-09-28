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

    def __init__(self, did = None, ddo_text = None):
        self.clear()
        self._did = did
        if ddo_text:
            self.read_json(ddo_text)

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
            'publicKeyPem': public_key_pem.decode(),
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

    def as_text(self, is_proof = True):
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
        if self._proof and is_proof == True:
            data['proof'] = self._proof

        return json.dumps(data)

    def read_json(self, ddo_json):
        values = json.loads(ddo_json)
        self._id = values['id']
        self._created = values.get('created', None)
        if 'publicKey' in values:
            self._public_keys = values['publicKey']
        if 'authentication' in values:
            self._authentications = values['authentication']
        if 'service' in values:
            self._service = values['service']
        if 'proof' in values:
            self._proof = values['proof']

    def add_proof(self, index, private_key_pem):
        # add a static proof to the DDO, based on one of the public keys
        sign_key = self._public_keys[index]
        self._proof = None
        signature = OceanDDO.sign_text(self.as_text(), private_key_pem)

        self._proof = {
            'type': sign_key['type'],
            'created': self._get_timestamp(),
            'creator': sign_key['id'],
            'signatureValue': str(b64encode(signature))
        }


    def validate_proof(self, signature_text = None):
        if not signature_text:
            signature_text = self.as_text(is_proof = False)
        if self._proof == None:
            return False
        return self.validate_from_key(self._proof['creator'], signature_text, self._proof['signatureValue'])

    def is_proof_defined(self):
        return not self._proof == None


    def validate_from_key(self, key_id, signature_text, signature_value):
        public_key = self.get_public_key(key_id)
        if public_key:
            return OceanDDO.validate_signature(signature_text, public_key['publicKeyPem'].encode(), signature_value)
        return False

    def get_public_key(self, key_id):
        for item in self._public_keys:
            if item['id'] == key_id:
                return item
        return None

    # validate the ddo data structure
    def validate(self):
        if self._public_keys and self._authentications:
            for item in self._authentications:
                key_id = item['id']
                public_key = self.get_public_key(key_id)
                if public_key == None:
                    return False
        return True

    @property
    def public_keys(self):
        return self._public_keys

    @property
    def authentications(self):
        return self._authentications

    @property
    def services(self):
        return self._services

    @staticmethod
    def sign_text(text, key_pem):
        signer = PKCS1_v1_5.new(RSA.import_key(key_pem))
        text_hash = SHA256.new(text.encode())
        return signer.sign(text_hash)

    @staticmethod
    def validate_signature(text, key, signature):
        try:
            rsa_key = RSA.import_key(key)
            validater = PKCS1_v1_5.new(rsa_key)
            text_hash = SHA256.new(text.encode())
            validater.verify(text_hash, signature)
            return True
        except (ValueError, TypeError):
            return False
    def _get_timestamp(self):
        return str(datetime.datetime.now())
