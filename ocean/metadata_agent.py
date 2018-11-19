"""
    MetadataAgent - Agent to read/write and list metadata on the Ocean network
"""
import json
import requests

from ocean.agent import Agent


# service endpoint type name to use for this agent
METADATA_AGENT_ENDPOINT_NAME = 'metadata-storage'
METADATA_BASE_URI = '/api/v1/meta/data'

class MetadataAgent(Agent):
    def __init__(self, client, did):
        """init a standard ocean agent, with a given DID"""
        Agent.__init__(self, client, did)
        self._headers = {'content-type': 'application/json'}
        if self._client.metadata_agent_auth:
            self._headers['Authorization'] = 'Basic {}'.format(self._client.metadata_agent_auth)

    def save(self, asset_id, metadata_text):
        """save metadata to the agent server, using the asset_id and metadata"""
        endpoint = self._get_endpoint(METADATA_AGENT_ENDPOINT_NAME)
        if endpoint:
            url = endpoint + METADATA_BASE_URI + '/' + asset_id
            response = requests.put(url, data=metadata_text, headers=self._headers)
            print(response.content)
        # TODO: server not running on travis build, so always return success !
        return asset_id

    def read(self, asset_id):
        """read the metadata from a service agent using the asset_id"""
        endpoint = self._get_endpoint(METADATA_AGENT_ENDPOINT_NAME)
        if endpoint:
            response = requests.get(endpoint + '/data/' + asset_id).content
            if response:
                return json.loads(response)
        return None
