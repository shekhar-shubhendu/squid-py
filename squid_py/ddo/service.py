"""

    Service Class
    To handle service items in a DDO record
"""

import json
import re


class Service(object):

    def __init__(self, service_id, endpoint, service_type, values):
        self._id = service_id
        self._endpoint = endpoint
        self._type = service_type

        # assign the _values property to empty until they are used
        self._values = None
        reserved_names =  ['id', 'serviceEndpoint', 'type']
        if values:
            for name, value in values.items():
                if name not in reserved_names:
                    if not self._values:
                        self._values = {}
                    self._values[name]= value


    def get_id(self):
        return self._id

    def assign_did(self, did):
        if re.match('^#.*', self._id):
            self._id = did + self._id

    def get_type(self):
        return self._type

    def get_endpoint(self):
        return self._endpoint

    def get_values(self):
        return self._values

    def as_text(self):
        values = {
            'id': self._id,
            'type': self._type,
            'serviceEndpoint': self._endpoint
        }
        if self._values:
            # add extra service values to the dictonairy
            for name, value in self._values.items():
                values[name] = value
        return json.dumps(values)

    def is_valid(self):
        return self._endpoint != None and self._type != None
