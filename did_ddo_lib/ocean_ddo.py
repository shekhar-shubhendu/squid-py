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

from .public_key_base import (
    PublicKeyBase,
    PUBLIC_KEY_STORE_TYPE_PEM,
    PUBLIC_KEY_STORE_TYPE_JWK,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_BASE64,
)

from .public_key_rsa import (
    PublicKeyRSA,
    AUTHENTICATION_TYPE_RSA,
    PUBLIC_KEY_TYPE_RSA,

)

from .constants import (
    KEY_PAIR_MODULUS_BIT,
    DID_DDO_CONTEXT_URL,
)

class OceanDDO(object):

    def __init__(self, did = None, ddo_text = None):
        self.clear()
        self._did = did
        self._created = self._get_timestamp()

        if ddo_text:
            self.read_json(ddo_text)

    # clear the DDO data values
    def clear(self):
        self._public_keys = []
        self._authentications = []
        self._services = []
        self._proof = None
        self._created = None


    # create a public key object based on the values from the JSON record
    def create_public_key(self, values):
        # currently we only support RSA public keys
        public_key = PublicKeyRSA(values['id'], owner = values.get('owner', None))
        public_key.set_key_value(values)
        return public_key

    # add a public key object to the list of public keys
    def add_public_key(self, public_key):        
        self._public_keys.append(public_key)

    # add a authentication public key id and type to the list of authentications
    def add_authentication(self, key_id, authentication_type = None):
        if isinstance(key_id, PublicKeyBase) and authentication_type == None:
            public_key = key_id
            row = {
                'publicKey' : public_key.get_id(),
                'type' : public_key.get_authentication_type()
            }
        else:
            if authentication_type == None:
                raise ValueError
            row = {
                'type' : authentication_type,
                'publicKey' : key_id,
            }
        self._authentications.append(row)

    # add a signature with a public key and authentication entry for validating this DDO
    # returns the private key as part of the private/public key pair
    def add_signature(self, public_key_store_type = PUBLIC_KEY_STORE_TYPE_PEM):

        key_pair = RSA.generate(KEY_PAIR_MODULUS_BIT, e=65537)
        public_key_raw = key_pair.publickey()
        private_key_pem = key_pair.exportKey("PEM")
        index = len(self._public_keys) + 1
        key_id = '{0}#keys={1}'.format(self._did, index)
        
        public_key = PublicKeyRSA(key_id, owner = key_id)
        
        public_key.set_encode_key_value(public_key_raw, public_key_store_type)
                
        # add the public key to the DDO list of public keys
        self.add_public_key(public_key)
        
        # also add the authentication id for this key
        self.add_authentication(public_key)

        return private_key_pem

    # add a service to the list of services on the DDO
    def add_service(self, service_type, service_endpoint):
        row = {
            'type' : service_type,
            'serviceEndpoint': service_endpoint,
        }
        self._services.append(row)

    # return the DDO as a JSON text
    # if is_proof == False then do not include the 'proof' element
    def as_text(self, is_proof = True):
        if self._created == None:
            self._created = self._get_timestamp()

        data = {
          "@context": DID_DDO_CONTEXT_URL,
          'id': self._did,
          'created': self._created,
        }
        if len(self._public_keys) > 0:
            values = []
            for public_key in self._public_keys:
                values.append(public_key.as_text())
            data['publicKey'] = values
        if len(self._authentications) > 0:
            data['authentication'] = self._authentications
        if len(self._services) > 0:
            data['service'] = self._services
        if self._proof and is_proof == True:
            data['proof'] = self._proof

        return json.dumps(data)

    # import a JSON text into this DDO
    def read_json(self, ddo_json):
        values = json.loads(ddo_json)
        self._id = values['id']
        self._created = values.get('created', None)
        if 'publicKey' in values:
            self._public_keys = []
            for value in values['publicKey']:
                self._public_keys.append(self.create_public_key(json.loads(value)))
        if 'authentication' in values:
            self._authentications = values['authentication']
        if 'service' in values:
            self._services = values['service']
        if 'proof' in values:
            self._proof = values['proof']

    # add a proof to the DDO, based on the public_key id/index and signed with the private key
    def add_proof(self, index, private_key):
        # add a static proof to the DDO, based on one of the public keys
        # find the key using an index, or key name
        sign_key = self.get_public_key(index)
        if sign_key == None:
            raise IndexError
        # just incase clear out the current static proof property
        self._proof = None
        # get the complete DDO as jSON text without the static proof field
        signature = OceanDDO.sign_text(self.as_text(False), private_key, sign_key.get_type())

        self._proof = {
            'type': sign_key.get_type(),
            'created': self._get_timestamp(),
            'creator': sign_key.get_id(),
            'signatureValue': str(b64encode(signature))
        }


    # validate the static proof created with this DDO, return True if valid
    # if no static proof exists then return False
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

    # return true if a static proof exists in this DDO
    def is_proof_defined(self):
        return not self._proof == None

    # validate a signature based on a given public_key key_id/name
    def validate_from_key(self, key_id, signature_text, signature_value):
        public_key = self.get_public_key(key_id)
        if public_key == None:
            return False
            
        key_value = public_key.get_decode_value()
        if key_value == None:
            return False
            
        authentication = self.get_authentication_from_public_key_id(public_key.get_id())
        if authentication == None:
            return False
            
        # if public_key.get_store_type() != PUBLIC_KEY_STORE_TYPE_PEM:
            # key_value = key_value.decode()
            
        return OceanDDO.validate_signature(signature_text, key_value, signature_value, authentication['type'])

    # key_id can be a string, or int. If int then the index in the list of keys
    def get_public_key(self, id):
        if isinstance(id, int):
            return self._public_keys[id]

        for item in self._public_keys:
            if item.get_id() == id:
                return item
        return None

    # return the authentication based on it's id
    def get_authentication_from_public_key_id(self, id):

        for item in self._authentications:
            if item['publicKey'] == id:
                return item
        return None

    # return true if the authentication has the correct field data
    def validate_authentication(self, authentication):
        if isinstance(authentication, dict):
            return 'type' in authentication and 'publicKey' in authentication
        return False

    # return true if a service has the correct field data.
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
                if not public_key.is_valid():
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
        if self._created:
            hash_text.append(self._created)

        if self._public_keys:
            for public_key in self._public_keys:
                hash_text.append(public_key.get_store_type())
                hash_text.append(public_key.as_text())

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
    def sign_text(text, private_key, sign_type = PUBLIC_KEY_TYPE_RSA):
        signed_text = None
        if sign_type == PUBLIC_KEY_TYPE_RSA:
            signer = PKCS1_v1_5.new(RSA.import_key(private_key))
            text_hash = SHA256.new(text.encode())
            signed_text = signer.sign(text_hash)
        else:
            raise NotImplementedError
        return signed_text

    @staticmethod
    def validate_signature(text, key, signature, sign_type = AUTHENTICATION_TYPE_RSA):
#        try:
        if sign_type == AUTHENTICATION_TYPE_RSA:
            rsa_key = RSA.import_key(key)
            validater = PKCS1_v1_5.new(rsa_key)
            text_hash = SHA256.new(text.encode())
            validater.verify(text_hash, signature)
            return True
        else:
            raise NotImplementedError
#        except (ValueError, TypeError):
#            return False

    def _get_timestamp(self):
        return str(datetime.datetime.now())
