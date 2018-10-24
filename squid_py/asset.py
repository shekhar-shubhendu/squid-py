import os
import logging
import json

class Asset:
    def __init__(self, asset_id, publisher_id, price):
        """
        Represent an asset in the MetaData store

        :param asset_id:
        :param publisher_id:
        :param price:
        """

        self.asset_id = asset_id
        self.publisher_id = publisher_id
        self.price = price


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

        # Download the asset from the provider using the URL in access token
        # Decode the the access token, get service_endpoint and request_id

        return

    def get_DDO(self):
        """

        :return:
        """

    def get_DID(self):
        pass

    def publish_metadata(self):
        pass

    def get_metadata(self):
        pass

    def update_metadata(self):
        pass

    def retire_metadata(self):
        pass

    def get_service_agreements(self):
        pass

    def __str__(self):
        return "Asset {} for {}, published by {}".format(self.asset_id, self.price,self.publisher_id)


class DDO(dict):
    def __init__(self):
        """
        DDO is a dictionary-like class (subclasses python dict)

        The default __init__ constructor should never be called directly, but instead
        called by the various constructor methods.
        """
        super().__init__()

    @classmethod
    def from_json_file(cls,json_file_path):
        """
        Load a DDO file as a dictionary-like object
        :param json_file_path: path to a DDO json file
        :return: DDO object
        """
        assert os.path.exists(json_file_path), "{} not found".format(json_file_path)

        # Load the file into dict
        with open(json_file_path) as f:
            json_dict = json.load(f)

        # Instantiate the dictionary
        this_ddo = cls()
        # Append all loaded values from the dictionary
        this_ddo.update(json_dict)
        return this_ddo

    @classmethod
    def from_json_string(cls,json_string):
        """
        Load a DDO string as a dictionary-like object
        :param json_string: json string
        :return: DDO object
        """
        pass

    @property
    def valid(self):
        required_keys = ['@context', 'id', 'publicKey', 'authentication', 'service']
        return all(req_key in self for req_key in required_keys)

#%%
path = r'/home/batman/ocn/squid-py/tests/resources/ddo/sample1.json'
ddo1 = DDO.from_json_file(path)
assert ddo1.valid
ddo1.keys()
ddo1['id']
