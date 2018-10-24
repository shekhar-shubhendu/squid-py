import os
import json
import logging

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
        logging.debug("DDO created for {} with {} public keys, {} authentications, {} services ".format(
            this_ddo['id'],
            len(this_ddo['publicKey']),
            len(this_ddo['authentication']),
            len(this_ddo['service']),
        ))
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
    def is_valid(self):
        required_keys = ['@context', 'id', 'publicKey', 'authentication', 'service']
        return all(req_key in self for req_key in required_keys)

    @property
    def raw_string(self):
        return json.dumps(self)

