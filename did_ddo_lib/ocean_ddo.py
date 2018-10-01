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
from .constants import (
    KEY_PAIR_MODULUS_BIT,
    DID_DDO_CONTEXT_URL,
)

PUBLIC_KEY_STORE_TYPE_PEM = 'publicKeyPem'
PUBLIC_KEY_STORE_TYPE_JWK = 'publicKeyJwk'
PUBLIC_KEY_STORE_TYPE_HEX = 'publicKeyHex'
PUBLIC_KEY_STORE_TYPE_BASE64 = 'publicKeyBase64'


AUTHENTICATION_TYPE_RSA = 'RsaVerificationKey2018'
PUBLIC_KEY_SIGN_TYPE_RSA = 'RsaSignatureAuthentication2018'

class OceanDDO(object):

    def __init__(self, did = None, ddo_text = None):
        self.clear()
        self._did = did
        self._created = self._get_timestamp()

        if ddo_text:
            self.read_json(ddo_text)

    def clear(self):
        self._public_keys = []
        self._authentications = []
        self._services = []
        self._proof = None
        self._created = None


    def convert_public_key_as(self):
        publicKeyPem, publicKeyJwk, publicKeyHex, publicKeyBase64

    def add_signature(self, public_key_type = PUBLIC_KEY_STORE_TYPE_PEM):

        key_pair = RSA.generate(KEY_PAIR_MODULUS_BIT, e=65537)
        public_key = key_pair.publickey()
        private_key_pem = key_pair.exportKey("PEM")
        key_type = PUBLIC_KEY_SIGN_TYPE_RSA
        index = len(self._public_keys) + 1
        key_id = '{0}#keys={1}'.format(self._did, index)

        row = {
            'id': key_id,
            'type': key_type,
            'owner': self._did,
        }

        if public_key_type == PUBLIC_KEY_STORE_TYPE_HEX:
            row[PUBLIC_KEY_STORE_TYPE_HEX] = public_key.exportKey("DER").hex()
        elif public_key_type == PUBLIC_KEY_STORE_TYPE_BASE64:
            row[PUBLIC_KEY_STORE_TYPE_BASE64] = b64encode(public_key.exportKey("DER")).decode()
        elif public_key_type == PUBLIC_KEY_STORE_TYPE_JWK:
            # TODO: need to decide on which jwk library to import?
            raise NotImplementedError
        elif public_key_type == PUBLIC_KEY_STORE_TYPE_PEM:
            row[PUBLIC_KEY_STORE_TYPE_PEM] = public_key.exportKey("PEM").decode()
        else:
            raise TypeError

        self._public_keys.append(row)
        if key_type == PUBLIC_KEY_SIGN_TYPE_RSA:
            authentication_type = AUTHENTICATION_TYPE_RSA
        else:
            raise NotImplementedError

        row = {
            'type' : authentication_type,
            'publicKey' : key_id,
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
            self._services = values['service']
        if 'proof' in values:
            self._proof = values['proof']

    def add_proof(self, index, private_key):
        # add a static proof to the DDO, based on one of the public keys
        # find the key using an index, or key name
        sign_key = self.get_public_key(index)
        if sign_key == None:
            raise IndexError
        # just incase clear out the current static proof property
        self._proof = None
        # get the complete DDO as jSON text without the static proof field
        signature = OceanDDO.sign_text(self.as_text(False), private_key, sign_key['type'])

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
        if not isinstance(self._proof, dict):
            return False
        if 'type' in self._proof and 'creator' in self._proof and 'signatureValue' in self._proof:
            return self.validate_from_key(self._proof['creator'], signature_text, self._proof['signatureValue'])
        return False

    def is_proof_defined(self):
        return not self._proof == None


    def validate_from_key(self, key_id, signature_text, signature_value):
        public_key = self.get_public_key(key_id)
        if public_key:
            key_value = None
            if PUBLIC_KEY_STORE_TYPE_HEX in public_key:
                key_value = bytes.fromhex(public_key[PUBLIC_KEY_STORE_TYPE_HEX])
            elif PUBLIC_KEY_STORE_TYPE_BASE64 in public_key:
                key_value = b64decode(public_key[PUBLIC_KEY_STORE_TYPE_BASE64])
            elif PUBLIC_KEY_STORE_TYPE_JWK in public_key:
                raise NotImplementedError
            else:
                key_value = public_key[PUBLIC_KEY_STORE_TYPE_PEM].encode()
            if key_value:
                authentication = self.get_authentication_from_public_key_id(public_key['id'])
                if authentication:
                    return OceanDDO.validate_signature(signature_text, key_value, signature_value, authentication['type'])
        return False

    # key_id can be a string, or int. If int then the index in the list of keys
    def get_public_key(self, id):
        if isinstance(id, int):
            return self._public_keys[id]

        for item in self._public_keys:
            if item['id'] == id:
                return item
        return None

    # return the authentication based on it's id
    def get_authentication_from_public_key_id(self, id):

        for item in self._authentications:
            if item['publicKey'] == id:
                return item
        return None

    def validate_public_key(self, public_key):
        if isinstance(public_key, dict):
            return 'id' in public_key and 'type' in public_key
        return False

    def validate_authentication(self, authentication):
        if isinstance(authentication, dict):
            return 'type' in authentication and 'publicKey' in authentication
        return False

    def validate_service(self, service):
        if isinstance(service, dict):
            return 'type' in service and 'serviceEndpoint' in service
        return False

    # validate the ddo data structure
    def validate(self):
        if self._public_keys and self._authentications:
            for authentication in self._authentications:
                if not self.validate_authentication(authentication):
                    return False
                key_id = authentication['publicKey']
                public_key = self.get_public_key(key_id)
                if not self.validate_public_key(public_key):
                    return False
        if self._services:
            for service in self._services:
                if not self.validate_service(service):
                    return False
        return True

    # return a sha3 hash of important bits of the DDO, excluding any DID portion,
    # as this hash can be used to generate the DID
    def calculate_hash(self):
        hash_text = []
        public_key_store_types = [
            PUBLIC_KEY_STORE_TYPE_PEM,
            PUBLIC_KEY_STORE_TYPE_JWK,
            PUBLIC_KEY_STORE_TYPE_HEX,
            PUBLIC_KEY_STORE_TYPE_BASE64,
        ]
        if self._created:
            hash_text.append(self._created)

        if self._public_keys:
            for public_key in self._public_keys:
                hash_text.append(public_key['type'])
                for public_key_store_type in public_key_store_types:
                    if public_key_store_type in public_key:
                        hash_text.append(public_key[public_key_store_type])

        if self._authentications:
            for authentication in self._authentications:
                hash_text.append(authentication['type'])

        if self._services:
            for service in self._services:
                hash_text.append(service['type'])
                hash_text.append(service['serviceEndpoint'])

        # if no data can be found to hash then raise an error
        if len(hash_text) == 0:
            raise ValueError
        return Web3.sha3(text="".join(hash_text))

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
    def sign_text(text, private_key, sign_type = PUBLIC_KEY_SIGN_TYPE_RSA):
        signed_text = None
        if sign_type == PUBLIC_KEY_SIGN_TYPE_RSA:
            signer = PKCS1_v1_5.new(RSA.import_key(private_key))
            text_hash = SHA256.new(text.encode())
            signed_text = signer.sign(text_hash)
        else:
            raise NotImplementedError
        return signed_text

    @staticmethod
    def validate_signature(text, key, signature, sign_type = AUTHENTICATION_TYPE_RSA):
        try:
            if sign_type == AUTHENTICATION_TYPE_RSA:
                rsa_key = RSA.import_key(key)
                validater = PKCS1_v1_5.new(rsa_key)
                text_hash = SHA256.new(text.encode())
                validater.verify(text_hash, signature)
                return True
            else:
                raise NotImplementedError
        except (ValueError, TypeError):
            return False

    def _get_timestamp(self):
        return str(datetime.datetime.now())
