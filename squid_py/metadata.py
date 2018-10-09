import json

import requests


class Metadata(object):

    def __init__(self, provider_uri):
        self._base_url = provider_uri + '/api/v1/provider/assets'  # http://localhost:5000/api/v1/provider/assets/
        self._headers = {'content-type': 'application/json'}

    def get_assets(self):
        return json.loads(requests.get(self._base_url).content)

    def get_asset_ddo(self, asset_did):
        return json.loads(requests.get(self._base_url + '/metadata/%s' % asset_did).content)

    def get_assets_metadata(self):
        return json.loads(requests.get(self._base_url + '/metadata').content)

    def register_asset(self, data):
        return json.loads(requests.post(self._base_url + '/metadata', data=json.dumps(data), headers=self._headers).content)

    def update_asset(self, data):
        return json.loads(requests.put(self._base_url + '/metadata', data=json.dumps(data), headers=self._headers).content)

    def retire_asset(self, asset_id):
        return requests.delete(self._base_url + '/metadata/%s' % asset_id, headers=self._headers)
