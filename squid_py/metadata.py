import ast
import json

import requests


class Metadata(object):

    def __init__(self, provider_uri):
        self.base_url = provider_uri + '/api/v1/provider/assets'  # http://localhost:5000/api/v1/provider/assets/
        self.headers = {'content-type': 'application/json'}

    def list_assets(self):
        return json.loads(requests.get(self.base_url).content)

    def get_asset_metadata(self, asset_did):
        return json.loads(requests.get(self.base_url + '/metadata/%s' % asset_did).content)

    def list_assets_metadata(self):
        return json.loads(requests.get(self.base_url + '/metadata').content)

    def publish_asset_metadata(self, data):
        return json.loads(requests.post(self.base_url + '/metadata', data=json.dumps(data), headers=self.headers).content)

    def update_asset_metadata(self, data):
        return json.loads(requests.put(self.base_url + '/metadata', data=json.dumps(data), headers=self.headers).content)

    def search(self, search_query):
        return ast.literal_eval(json.loads(
            requests.post(self.base_url + '/metadata/query', data=json.dumps(search_query),
                          headers=self.headers).content))

    def retire_asset_metadata(self, asset_id):
        return requests.delete(self.base_url + '/metadata/%s' % asset_id, headers=self.headers)
