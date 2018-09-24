import json

import requests


class Metadata(object):

    def __init__(self, provider_uri):
        self.base_url = provider_uri + '/api/v1/provider/assets'  # http://localhost:5000/api/v1/provider/assets/
        self.headers = {'content-type': 'application/json'}

    def get_assets(self):
        return json.loads(requests.get(self.base_url).content)

    def get_asset_metadata(self, asset_id):
        return json.loads(requests.get(self.base_url + '/metadata/%s' % asset_id).content)

    def get_assets_metadata(self):
        return json.loads(requests.get(self.base_url + '/metadata').content)

    def register_asset(self, data):
        data = json.dumps(data)
        return json.loads(requests.post(self.base_url + '/metadata', data=data, headers=self.headers).content)

    def update_asset(self, data):
        data = json.dumps(data)
        return json.loads(requests.put(self.base_url + '/metadata', data=data, headers=self.headers).content)

    def retire_asset(self, asset_id):
        return requests.delete(self.base_url + '/metadata/%s' % asset_id, headers=self.headers)
