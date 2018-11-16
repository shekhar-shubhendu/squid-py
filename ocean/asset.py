"""
    Asset class to hold Ocean asset information such as asset id and metadata
"""
import hashlib
import json
from web3 import Web3

from ocean.metadata_agent import MetadataAgent
from squid_py.did import (
    did_parse,
    id_to_did,
)

class Asset():
    def __init__(self, client, did=None):
        """
        init an asset class with the following:
        :param client: OceanClient to use to connect to the ocean network
        :param metadata: Optional metadata to use for a new asset
        :param asset_id: Optional asset id to use for an already existing asset
        """
        self._client = client
        self._id = None
        self._metadata = None
        self._agent_did = None
        if did:
            # look for did:op:xxxx/yyy, where xxx is the agent and yyy is the asset
            data = did_parse(did)
            if data['id_hex'] and data['path']:
                self._agent_did = id_to_did(data['id_hex'])
                self._id = Web3.toHex(hexstr=data['path'])

    def register(self, metadata, did):
        """
        Register an asset by writing it's meta data to the meta storage agent
        :param metadata: dict of the metadata, munt contain the key ['base']
        :param agent_did: did of the meta stroage agent
        :return The new asset registered, or return None on error
        :raise IndexError if no 'base' field is found in the metadata
        """

        asset_id = Asset._get_asset_id_from_metadata(metadata)
        if asset_id:
            agent = MetadataAgent(self._client, did)
            if agent.is_valid:
                if agent.save(asset_id, metadata):
                    self._id = asset_id
                    self._agent_did = did
                    return True
        return None

    def read_metadata(self):
        """read the asset metadata from an Ocean Agent, using the agents DID"""
        agent = MetadataAgent(self._client, self._agent_did)
        metadata = agent.read(self._id)
        # only return the valid metadata
        if Asset.is_metadata_valid(self._id, metadata):
            self._metadata = metadata
            return self._metadata
        return None


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
        return self._id is None or self._agent_did is None

    @property
    def agent_did(self):
        """DID of the metadata agent for this asset"""
        return self._agent_did

    @property
    def did(self):
        """return the DID of the asset"""
        if not is_empty:
            return self._agent_did + '/' + self._id
        return None

    @staticmethod
    def is_metadata_valid(asset_id, metadata):
        if metadata:
            # the calc asset_id from the metadata should be same as this asset_id
            metadata_id = Asset._get_asset_id_from_metadata(metadata)
            return metadata_id == asset_id
        return False

    @staticmethod
    def _get_asset_id_from_metadata(metadata):
        asset_id = None
        if 'base' in metadata:
            asset_id = hashlib.sha256(json.dumps(metadata['base']).encode('utf-8')).hexdigest()
        else:
            raise IndexError('Cannot find "base" field in the metadata structure')
        return asset_id
