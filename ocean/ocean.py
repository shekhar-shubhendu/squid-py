"""
    Basic Ocean class to allow for registration and obtaining assets and agents

"""
import secrets

from ocean.ocean_client import OceanClient
from ocean.asset import Asset
from ocean.metadata_agent import MetadataAgent
from ocean.ocean_agent import OceanAgent
from squid_py.did import id_to_did

class Ocean():

    def __init__(self, ocean_url, contracts_path):
        """init the basic OceanClient for the connection and contract info"""
        self._client = OceanClient(ocean_url, contracts_path)

    def register_asset(self, metadata, agent_did):
        """
        Register an asset by writing it's meta data to the meta storage agent
        :param metadata: dict of the metadata, munt contain the key ['base']
        :param agent_did: did of the meta stroage agent
        :return The new asset registered, or return None on error
        """
        asset = Asset(self._client, metadata)
        agent = MetadataAgent(self._client, agent_did)
        agent.save(asset.id, metadata)
        return asset

    def register_agent(self, name, endpoint, account, did = None):
        """
        Register an agent with the ocean network
        :param name: name of the agent's endpoint in the DDO record
        :param endpoint: url of the agents end point
        :return registered did of the agent, and DDO private password in PEM format
        of the signed DDO record
        """
        agent = OceanAgent(self._client)
        if did is None:
            did = id_to_did(secrets.token_hex(32))
        return did, agent.register(did, name, endpoint, account)


    def get_agent(self, did):
        """return an agent that is registered with the did"""
        agent = OceanAgent(self._client, did)
        if agent.ddo:
            return agent
        return None

    def get_asset(self, did, asset_id):
        """return a registered asset given a DID of the agent and asset id"""
        asset = Asset(self._client, asset_id)
        if asset.read_metadata(did):
            return asset
        return None


    @property
    def client(self):
        """return the OceanClient used to access the ocean network"""
        return self._client