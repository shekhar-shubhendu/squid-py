"""
    Asset class to hold Ocean asset information such as asset id and metadata
"""
import hashlib
import json

from ocean.ocean_client import OceanClient
from ocean.metadata_agent import MetadataAgent

class Asset():
    def __init__(self, client, metadata = None, asset_id = None):
        """
        init an asset class with the following:
        :param client: OceanClient to use to connect to the ocean network
        :param metadata: Optional metadata to use for a new asset
        :param asset_id: Optional asset id to use for an already existing asset
        """
        self._client = client
        self._metadata = metadata
        self._id = asset_id
        if self._metadata:
            self._id = hashlib.sha256(json.dumps(metadata['base']).encode('utf-8')).hexdigest()

    def read_metadata(self, agent_did):
        """read the asset metadata from an Ocean Agent, using the agents DID"""
        agent = MetadataAgent(self._client, agent_did)
        self._metadata = agent.read_metadat(self._id)
        return self._metadata

    @property
    def id(self):
        """return the asset id"""
        return self._id

    @property
    def metadata(self):
        """return the associated metadata for this assset"""
        return self._metadata

