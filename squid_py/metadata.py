import ast
import json

import requests


class Metadata(object):

    def __init__(self, provider_url):
        self._base_url = '{}/api/v1/provider/assets'.format(provider_url)
        self._headers = {'content-type': 'application/json'}

    def list_assets(self):
        return json.loads(requests.get(self._base_url).content)

    def get_asset_metadata(self, asset_did):
        return json.loads(requests.get(self._base_url + '/metadata/%s' % asset_did).content)

    def list_assets_metadata(self):
        return json.loads(requests.get(self._base_url + '/metadata').content)

    def publish_asset_metadata(self, data):
        return json.loads(
            requests.post(self._base_url + '/metadata', data=json.dumps(data), headers=self._headers).content)

    def update_asset_metadata(self, data):
        return json.loads(
            requests.put(self._base_url + '/metadata', data=json.dumps(data), headers=self._headers).content)

    def search(self, search_query):
        return ast.literal_eval(json.loads(
            requests.post(self._base_url + '/metadata/query', data=json.dumps(search_query),
                          headers=self._headers).content))

    def retire_asset_metadata(self, asset_id):
        return requests.delete(self._base_url + '/metadata/%s' % asset_id, headers=self._headers)
