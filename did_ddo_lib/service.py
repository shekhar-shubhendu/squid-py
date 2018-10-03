"""

    Service Class
    To handle service items in a DDO record
"""

import json


class Service(object):

    def __init__(self, service_id, endpoint, service_type):
        self._id = service_id
        self._endpoint = endpoint
        self._type = service_type

    def get_id(self):
        return self._id
        
    def get_type(self):
        return self._type
                
    def get_endpoint(self):
        return self._endpoint
        
    def as_text(self):
        values = {
            'id': self._id,
            'type': self._type,
            'serviceEndpoint': self._endpoint
        }            
        return json.dumps(values)
            

    def is_valid(self):
        return self._endpoint != None and self._type != None
        
