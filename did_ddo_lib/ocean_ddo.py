"""
    DID Lib to do DID's and DDO's

"""
import datetime
import json
import re
from base64 import b64encode

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from web3 import Web3

from .authentication import Authentication
from .constants import KEY_PAIR_MODULUS_BIT, DID_DDO_CONTEXT_URL
from .public_key_base import PublicKeyBase, PUBLIC_KEY_STORE_TYPE_PEM
from .public_key_rsa import PublicKeyRSA, AUTHENTICATION_TYPE_RSA, PUBLIC_KEY_TYPE_RSA
from .service import Service

class OceanDDO(object):

    def __init__(self, did = '', ddo_text = None , created = None):
        self.clear()
        self._did = did
        if created == None:
            self._created = OceanDDO.get_timestamp()
        else:
            self._created = created

        if ddo_text:
            self.read_json(ddo_text)

    # clear the DDO data values
    def clear(self):
        self._did = ''
        self._public_keys = []
        self._authentications = []
        self._services = []
        self._proof = None
        self._created = None


    # add a public key object to the list of public keys
    def add_public_key(self, public_key):
        self._public_keys.append(public_key)

    # add a authentication public key id and type to the list of authentications
    def add_authentication(self, key_id, authentication_type = None):
        if isinstance(key_id, Authentication):
            # adding an authentication object
            authentication = key_id
        elif isinstance(key_id, PublicKeyBase):
            public_key = key_id
            # this is going to be a embedded public key
            authentication = Authentication(public_key, public_key.get_authentication_type())
        else:
            # with key_id as a string, we also need to provide the authentication type
            if authentication_type == None:
                raise ValueError
            authentication = Authentication(key_id, authentication_type)

        self._authentications.append(authentication)

    # add a signature with a public key and authentication entry for validating this DDO
    # returns the private key as part of the private/public key pair
    def add_signature(self, public_key_store_type = PUBLIC_KEY_STORE_TYPE_PEM, is_embedded = False):

        key_pair = RSA.generate(KEY_PAIR_MODULUS_BIT, e=65537)
        public_key_raw = key_pair.publickey()
        private_key_pem = key_pair.exportKey("PEM")

        # find the current public key count
        next_index = self.get_public_key_count() + 1
        key_id = '{0}#keys={1}'.format(self._did, next_index)

        public_key = PublicKeyRSA(key_id, owner = key_id)

        public_key.set_encode_key_value(public_key_raw, public_key_store_type)

        if is_embedded:
            # also add the authentication key as embedded key with the authentication
            self.add_authentication(public_key)
        else:
            # add the public key to the DDO list of public keys
            self.add_public_key(public_key)

            # add the public key id and type for this key to the authentication
            self.add_authentication(public_key.get_id(), public_key.get_authentication_type())

        return private_key_pem

    # add a service to the list of services on the DDO
    def add_service(self, service_type, service_endpoint = None, service_id = None, values = None):
        if isinstance(service_type, Service):
            service = service_type
        else:
            if service_id == None:
                service_id = self._did
            service = Service(service_id, service_endpoint, service_type, values)
        self._services.append(service)

    # return the DDO as a JSON text
    # if is_proof == False then do not include the 'proof' element
    def as_text(self, is_proof = True):
        if self._created == None:
            self._created = OceanDDO.get_timestamp()

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
            values = []
            for authentication in self._authentications:
                values.append(authentication.as_text())
            data['authentication'] = values
        if len(self._services) > 0:
            values = []
            for service in self._services:
                values.append(service.as_text())
            data['service'] = values
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
                if isinstance(value, str):
                    value = json.loads(value)
                self._public_keys.append(OceanDDO.create_public_key_from_json(value))
        if 'authentication' in values:
            self._authentications = []
            for value in values['authentication']:
                if isinstance(value, str):
                    value = json.loads(value)
                self._authentications.append(OceanDDO.create_authentication_from_json(value))
        if 'service' in values:
            self._services = []
            for value in values['service']:
                if isinstance(value, str):
                    value = json.loads(value)
                self.services.append(OceanDDO.create_service_from_json(value))
        if 'proof' in values:
            self._proof = values['proof']

    # add a proof to the DDO, based on the public_key id/index and signed with the private key
    def add_proof(self, authorisation_index, private_key = None):
        # add a static proof to the DDO, based on one of the public keys
        # find the key using an index, or key name
        if isinstance(authorisation_index, dict):
            self._proof = authorisation_index
            return

        if private_key == None:
            raise ValueError

        authentication = self._authentications[authorisation_index]
        if not authentication:
            raise IndexError
        if authentication.is_public_key():
            sign_key = authentication.get_public_key()
        else:
            sign_key = self.get_public_key(authentication.get_public_key_id())

        if sign_key == None:
            raise IndexError
        # just incase clear out the current static proof property
        self._proof = None
        # get the complete DDO as jSON text without the static proof field
        signature = OceanDDO.sign_text(self.as_text(False), private_key, sign_key.get_type())

        self._proof = {
            'type': sign_key.get_type(),
            'created': OceanDDO.get_timestamp(),
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

        public_key = self.get_public_key(key_id, True)
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

        return OceanDDO.validate_signature(signature_text, key_value, signature_value, authentication.get_type())

    # key_id can be a string, or int. If int then the index in the list of keys
    def get_public_key(self, key_id, is_search_embedded = False):
        if isinstance(key_id, int):
            return self._public_keys[key_id]

        for item in self._public_keys:
            if item.get_id() == key_id:
                return item

        if is_search_embedded:
            for authentication in self._authentications:
                if authentication.get_public_key_id() == key_id:
                    return authentication.get_public_key()
        return None

    # return the count of public keys in the list and embedded
    def get_public_key_count(self):
        index = len(self._public_keys)
        for authentication in self._authentications:
            if authentication.is_public_key():
                index += 1
        return index

    # return the authentication based on it's id
    def get_authentication_from_public_key_id(self, key_id):
        for authentication in self._authentications:
            if authentication.is_key_id(key_id):
                return authentication
        return None

    # return a service using
    def get_service(self, service_type = None, service_id = None):
        for service in self._services:
            if service.get_id() == service_id and service_id:
                return service
            if service.get_type() == service_type and service_type:
                return service
        return None

    # validate the ddo data structure
    def validate(self):
        if self._public_keys and self._authentications:
            for authentication in self._authentications:
                if not authentication.is_valid():
                    return False
                if authentication.is_public_key():
                    public_key = authentication.get_public_key()
                else:
                    key_id = authentication.get_public_key_id()
                    public_key = self.get_public_key(key_id)
                if not public_key.is_valid():
                    return False
        if self._services:
            for service in self._services:
                if not service.is_valid():
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
                hash_text.append(public_key.get_type())
                hash_text.append(public_key.get_value())

        if self._authentications:
            for authentication in self._authentications:
                if authentication.is_public_key():
                    public_key = authentication.get_public_key()
                    hash_text.append(public_key.get_type())
                    hash_text.append(public_key.get_value())

        if self._services:
            for service in self._services:
                hash_text.append(service.get_type())
                hash_text.append(service.get_endpoint())

        # if no data can be found to hash then raise an error
        if len(hash_text) == 0:
            raise ValueError
        return Web3.sha3(text="".join(hash_text))

    def is_empty(self):
        return self._did == ''                          \
                and len(self._public_keys) == 0         \
                and len(self._authentications) == 0     \
                and len(self._services) == 0            \
                and self._proof == None                 \
                and self._created == None

    def is_did_assigend(self):
        return self._did != ''

    def get_created_time(self):
        return self._created

    # method to copy a DDO and assign a new did to all of the keys to an empty/non DID assigned DDO.
    # we assume that this ddo has been created as empty ( no did )
    def create_new(self, did):

        if self.is_did_assigend():
            raise Exception('Cannot assign a DID to a completed DDO object')
        ddo = OceanDDO(did, created = self._created)
        for public_key in self._public_keys:
            public_key.assign_did(did)
            ddo.add_public_key(public_key)

        for authentication in self._authentications:
            authentication.assign_did(did)
            ddo.add_authentication(authentication)

        for service in self._services:
            service.assign_did(did)
            ddo.add_service(service)


        if self.is_proof_defined():
            if re.match('^#.*', self._proof['creator']):
                proof = self._proof
                proof['creator'] = did + proof['creator']
            ddo.add_proof(proof)

        return ddo

    @property
    def public_keys(self):
        return self._public_keys

    @property
    def authentications(self):
        return self._authentications

    @property
    def services(self):
        return self._services

    @property
    def proof(self):
        return self._proof

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

    # create a public key object based on the values from the JSON record
    @staticmethod
    def create_public_key_from_json(values):
        # currently we only support RSA public keys
        public_key = PublicKeyRSA(values['id'], owner = values.get('owner', None))
        public_key.set_key_value(values)
        return public_key


    @staticmethod
    def create_authentication_from_json(values):
        key_id = values['publicKey']
        authentication_type = values['type']
        if isinstance(key_id, dict):
            public_key = OceanDDO.create_public_key_from_json(key_id)
            authentication = Authentication(public_key, public_key.get_authentication_type())
        else:
            authentication = Authentication(key_id, authentication_type)

        return authentication

    @staticmethod
    def create_service_from_json(values):
        if not 'id' in values:
            raise IndexError
        if not 'serviceEndpoint' in values:
            raise IndexError
        if not 'type' in values:
            raise IndexError
        service = Service(values['id'], values['serviceEndpoint'], values['type'], values)
        return service

    @staticmethod
    def get_timestamp():
        return str(datetime.datetime.now())
