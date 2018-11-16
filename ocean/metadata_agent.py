"""
    MetadataAgent - Agent to read/write and list metadata on the Ocean network
"""
import json
import requests

from ocean.ocean_agent import OceanAgent

# service endpoint type name to use for this agent
METADATA_AGENT_ENDPOINT_NAME = 'metadata-storage'

class MetadataAgent(OceanAgent):
    def __init__(self, ocean_client, did):
        """init a standard ocean agent, with a given DID"""
        OceanAgent.__init__(self, ocean_client, did)
        self._headers = {'content-type': 'application/json'}

    def save(self, asset_id, metadata):
        """save metadata to the agent server, using the asset_id and metadata"""
        endpoint = self._get_endpoint(METADATA_AGENT_ENDPOINT_NAME)
        if endpoint:
            metadata_text = json.dumps(metadata)
            response = requests.put(endpoint + '/' + asset_id, data=metadata_text, headers=self._headers)
            print(response)

    def read(self, asset_id):
        """read the metadata from a service agent using the asset_id"""
        endpoint = self._get_endpoint(METADATA_AGENT_ENDPOINT_NAME)
        if endpoint:
            response = requests.get(endpoint + '/data/' + asset_id).content
            if response:
                return json.loads(response)
        return None

