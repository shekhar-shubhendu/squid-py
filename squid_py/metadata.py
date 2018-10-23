import ast
import json

import requests

from squid_py.asset import Asset
import logging

class Metadata(object):

    def __init__(self, provider_url):
        """
        The Metadata class is a wrapper on the Metadata Store, which has exposed a REST API

        :param provider_url:
        """
        self._base_url = '{}/api/v1/provider/assets'.format(provider_url)
        self._headers = {'content-type': 'application/json'}

        logging.debug("Metadata Store connected at {}".format(provider_url))
        logging.debug("Metadata assets at {}".format(self._base_url))

    def list_assets(self):
        return json.loads(requests.get(self._base_url).content)

    def get_asset_metadata(self, asset_did):
        return json.loads(requests.get(self._base_url + '/metadata/%s' % asset_did).content)

    def list_assets_metadata(self):
        return json.loads(requests.get(self._base_url + '/metadata').content)

    def publish_asset_metadata(self, data):
        # asset = Asset
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
