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
        self._metadata_text = None
        self._agent_did = None
        if did:
            # look for did:op:xxxx/yyy, where xxx is the agent and yyy is the asset id
            data = did_parse(did)
            if data['id_hex'] and data['path']:
                self._agent_did = id_to_did(data['id_hex'])
                self._id = Web3.toHex(hexstr=data['path'])

    def register(self, metadata, did):
        """
        Register an asset by writing it's meta data to the meta storage agent
        :param metadata: dict of the metadata
        :param agent_did: did of the meta stroage agent
        :return The new asset registered, or return None on error
        """

        metadata_text = json.dumps(metadata)
        asset_id = Asset._get_asset_id_from_metadata(metadata_text)
        if asset_id:
            agent = MetadataAgent(self._client, did)
            if agent.is_valid:
                if agent.save(asset_id, metadata_text):
                    self._id = asset_id
                    self._agent_did = did
                    self._metadata_text = metadata_text
                    return True
        return None

    def read_metadata(self):
        """read the asset metadata from an Ocean Agent, using the agents DID"""
        agent = MetadataAgent(self._client, self._agent_did)
        metadata_text = agent.read(self._id)
        # only return the valid metadata
        if Asset.is_metadata_valid(self._id, metadata_text):
            self._metadata_text = metadata_text
            return self.metadata
        return None

    @property
    def asset_id(self):
        """return the asset id"""
        return self._id

    @property
    def metadata(self):
        """return the associated metadata for this assset"""
        if self._metadata_text:
            return json.loads(self._metadata_text)
        return None

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
        if not self.is_empty:
            return self._agent_did + '/' + self._id
        return None

    @staticmethod
    def is_metadata_valid(asset_id, metadata_text):
        """
        validate metadata, by calcualating the hash (asset_id) and compare this to the 
        given asset_id, if both are equal then the metadata is valid
        :param asset_id: asset id to compare with
        :param metadata: dict of metadata to calculate the hash ( asset_id)
        :return bool True if metadata is valid for the asset_id provided
        """
        if metadata_text:
            # the calc asset_id from the metadata should be same as this asset_id
            metadata_id = Asset._get_asset_id_from_metadata(metadata_text)
            return metadata_id == asset_id
        return False

    @staticmethod
    def _get_asset_id_from_metadata(metadata_text):
        """
        return the asset_id calculated from the metadata
        :param metadata: dict of metadata to hash
        a 64 char hex string, which is the asset id
        :return 64 char hex string, with no leading '0x'
        """
        return Web3.toHex(Web3.sha3(metadata_text.encode()))[2:]
