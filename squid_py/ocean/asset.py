import hashlib
import json
import logging
import re

from squid_py.ddo import DDO
from squid_py.ocean.ocean_base import OceanBase


class Asset:
    def __init__(self, asset_id=None, publisher_id=None, price=None, ddo=None):
        """
        Represent an asset in the MetaData store

        Constructor methods:
            1. Direct instantiation Asset(**kwargs)
                - Use this method to manually build an asset
            2. From a json DDO file Asset.from_ddo_json_file()
                - Create an asset based on a DDO file
            3.

        :param asset_id: AKA the DID. This is generated by the market contract, on chain!
        :param publisher_id:
        :param price:
        :param ddo: DDO instance
        """

        self.asset_id =asset_id
        self.publisher_id = publisher_id
        self.price = price
        self.ddo = ddo

    @property
    def bare_did_string(self):
        # TODO: This is temp, until the proper handling is implemented!
        return self.asset_id.split(':')[-1]

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
        this_asset = cls()
        this_asset.ddo = DDO(json_filename=json_file_path)
        this_asset.asset_id = this_asset.ddo.did
        logging.debug("Asset {} created from ddo file {} ".format(this_asset.asset_id, json_file_path))
        return this_asset

    @property
    def metadata(self):
        assert self.has_metadata
        return self._get_metadata()

    @property
    def has_metadata(self):
        return not self._get_metadata() == None

    def _get_metadata(self):
        result = None
        metadata_service = self.ddo.get_service('Metadata')
        if metadata_service:
            values = metadata_service.get_values()
            if 'metadata' in values:
                result = values['metadata']
        return result

    def is_valid_did(self, length=64):
        """The Asset.asset_id must conform to the specification"""
        return len(self.asset_id) == length

    def generate_did(self):
        """
        During development, the DID can be generated here for convenience.
        """
        if not self.ddo:
            raise AttributeError("No DDO object in {}".format(self))
        if not self.ddo.is_valid:
            raise ValueError("Invalid DDO object in {}".format(self))

        metadata = self._get_metadata()
        if not metadata:
            raise ValueError("No metedata in {}".format(self))

        if not 'base' in metadata:
            raise ValueError("Invalid metedata in {}".format(self))

        self.asset_id = hashlib.sha256(json.dumps(metadata['base']).encode('utf-8')).hexdigest()

    def assign_metadata(self):
        pass

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

    def consume(self, order, consumer):
        """

        :param order: Order object
        :param consumer: Consumer Account
        :return: access_url
        :rtype: string
        :raises :
        """

        # Get access token (jwt)

        # Download the asset from the aquarius using the URL in access token
        # Decode the the access token, get service_endpoint and request_id

        return

    def get_DDO(self):
        """

        :return:
        """

    def get_DID(self):
        pass

    def get_metadata(self):
        return self.metadata

    def get_service_agreements(self):
        pass

    def __str__(self):
        return "Asset {}, price: {}, publisher: {}".format(self.asset_id, self.price, self.publisher_id)
