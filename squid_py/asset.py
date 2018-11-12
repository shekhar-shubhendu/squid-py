import hashlib
import json
import logging
import re

from squid_py.services import ServiceTypes
from .ddo import DDO


class Asset:
    def __init__(self, ddo, publisher_id=None):
        """
        Represent an asset in the MetaData store

        Constructor methods:
            1. Direct instantiation Asset(**kwargs)
                - Use this method to manually build an asset
            2. From a json DDO file Asset.from_ddo_json_file()
                - Create an asset based on a DDO file
            3.

        :param did: `did:op:0x...`, the 0x id portion must be of length 64 (or 32 bytes)
        :param publisher_id:
        :param ddo: DDO instance
        """

        self.ddo = ddo
        self.publisher_id = publisher_id
        self.asset_id = None
        if self.ddo and self.ddo.is_did_assigend():
            self.assign_did_from_ddo()

    def __str__(self):
        return "Asset {}, publisher: {}".format(self.did, self.publisher_id)

    def assign_did_from_ddo(self):
        """
        #TODO: This is a temporary hack, need to clearly define how DID is assigned!
        :return:
        """
        did = self.ddo.did
        match = re.match('^did:op:([0-9a-f]+)', did)
        if match:
            self.asset_id = match.groups(1)[0]

    @classmethod
    def from_ddo_json_file(cls, json_file_path):
        this_asset = cls(DDO(json_filename=json_file_path))
        logging.debug("Asset {} created from ddo file {} ".format(this_asset.did, json_file_path))
        return this_asset

    @property
    def metadata(self):
        assert self.has_metadata
        return self.get_metadata()

    @property
    def has_metadata(self):
        return self.get_metadata() is not None

    @property
    def did(self):
        return self.ddo.did

    def getId(self):
        return self.asset_id

    def generate_did(self):
        """
        During development, the DID can be generated here for convenience.
        """
        if not self.ddo:
            raise AttributeError("No DDO object in {}".format(self))
        if not self.ddo.is_valid:
            raise ValueError("Invalid DDO object in {}".format(self))

        metadata = self.get_metadata()
        if not metadata:
            raise ValueError("No metedata in {}".format(self))

        if not 'base' in metadata:
            raise ValueError("Invalid metedata in {}".format(self))

        self.asset_id = hashlib.sha256(json.dumps(metadata['base']).encode('utf-8')).hexdigest()
        self.ddo = self.ddo.create_new('did:op:%s' % self.asset_id)

    def purchase(self, consumer, timeout):
        """
        Generate an order for purchase of this Asset

        :param timeout:
        :param consumer: Account object of the requester
        :return: Order object
        """
        # Check if asset exists

        # Approve the token transfer

        # Submit access request

        return

    def get_DDO(self):
        """

        :return:
        """
        return self.ddo

    def get_DID(self):
        return self.ddo.did

    def get_metadata(self):
        result = None
        metadata_service = self.ddo.get_service(ServiceTypes.METADATA)
        if metadata_service:
            values = metadata_service.get_values()
            if 'metadata' in values:
                result = values['metadata']
        return result

    def publish_metadata(self):
        pass

    def update_metadata(self):
        pass

    def retire_metadata(self):
        pass

    def get_service_agreements(self):
        pass
