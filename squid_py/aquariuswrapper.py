import ast
import json
import logging

import requests


class AquariusWrapper(object):

    def __init__(self, aquarius_url):
        """
        The Metadata class is a wrapper on the Metadata Store, which has exposed a REST API

        :param aquarius_url:
        """

        self._base_url = '{}/api/v1/aquarius/assets'.format(aquarius_url)
        self._headers = {'content-type': 'application/json'}

        logging.debug("Metadata Store connected at {}".format(aquarius_url))
        logging.debug("Metadata Store API documentation at {}/api/v1/docs".format(aquarius_url))
        logging.debug("Metadata assets at {}".format(self._base_url))

    def list_assets(self):
        return json.loads(requests.get(self._base_url).content)

    def get_asset_metadata(self, asset_did):
        response = requests.get(self._base_url + '/ddo/%s' % asset_did).content
        response_dict = json.loads(response)
        # metadata_base = response_dict['base']
        # metadata = dict()
        # metadata['base'] = metadata_base
        return response_dict

    def list_assets_metadata(self):
        return json.loads(requests.get(self._base_url + '/ddo').content)

    def publish_asset_metadata(self, asset):
        response = requests.post(self._base_url + '/ddo', data=json.dumps(asset.ddo), headers=self._headers)
        if response.status_code == 500:
            raise ValueError("This Asset ID already exists! \n\tHTTP Error message: \n\t\t{}".format(response.text))
        elif response.status_code == 400:
            raise Exception("400 ERROR Full error: \n{}".format(response.text))
        elif response.status_code != 201:
            raise Exception("{} ERROR Full error: \n{}".format(response.status_code, response.text))
        elif response.status_code == 201:
            response = json.loads(response.content)
            logging.debug("Published {}".format(asset))
            return response
        else:
            raise Exception("ERROR")

    def update_asset_metadata(self, asset):
        return json.loads(
            requests.put(self._base_url + '/ddo/%s' % asset.ddo['id'], data=json.dumps(asset.ddo),
                         headers=self._headers).content)

    def text_search(self, text, sort=None, offset=100, page=0):
        payload = {"text": text, "sort": sort, "offset": offset, "page": page}
        request = json.loads(
            requests.get(self._base_url + '/ddo/query',
                         params=payload,
                         headers=self._headers).content)
        if request is None:
            return {}
        else:
            return ast.literal_eval(request)

    def query_search(self, search_query):
        return ast.literal_eval(json.loads(
            requests.post(self._base_url + '/ddo/query', data=json.dumps(search_query),
                          headers=self._headers).content))

    def retire_asset_metadata(self, asset_id):
        response = requests.delete(self._base_url + '/ddo/%s' % asset_id, headers=self._headers)
        logging.debug("Removed asset_id: {} from metadata store".format(asset_id))
        return response
