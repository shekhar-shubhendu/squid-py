"""
    Asset class to hold Ocean asset information such as asset id and metadata
"""
import hashlib
import json

from ocean.metadata_agent import MetadataAgent

class Asset():
    def __init__(self, client, asset_id=None):
        """
        init an asset class with the following:
        :param client: OceanClient to use to connect to the ocean network
        :param metadata: Optional metadata to use for a new asset
        :param asset_id: Optional asset id to use for an already existing asset
        """
        self._client = client
        self._id = asset_id
        self._metadata = None

    def register(self, metadata, did):
        """
        Register an asset by writing it's meta data to the meta storage agent
        :param metadata: dict of the metadata, munt contain the key ['base']
        :param agent_did: did of the meta stroage agent
        :return The new asset registered, or return None on error
        :raise IndexError if no 'base' field is found in the metadata
        """

        if 'base' in metadata:
            self._id = hashlib.sha256(json.dumps(metadata['base']).encode('utf-8')).hexdigest()
        else:
            raise IndexError('Cannot find "base" field in the metadata structure')

        agent = MetadataAgent(self._client, did)
        if agent.is_valid:
            return agent.save(self._id, metadata)
        return None

    def read_metadata(self, did):
        """read the asset metadata from an Ocean Agent, using the agents DID"""
        agent = MetadataAgent(self._client, did)
        self._metadata = agent.read(self._id)
        return self._metadata

    @property
    def asset_id(self):
        """return the asset id"""
        return self._id

    @property
    def metadata(self):
        """return the associated metadata for this assset"""
        return self._metadata

    @property
    def is_empty(self):
        return self._id is None
