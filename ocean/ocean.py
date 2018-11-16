"""
    Basic Ocean class to allow for registration and obtaining assets and agents

"""
import secrets

from ocean.client import Client
from ocean.asset import Asset
from ocean.agent import Agent
from ocean.metadata_agent import METADATA_AGENT_ENDPOINT_NAME

from squid_py.did import id_to_did

class Ocean():

    def __init__(self, ocean_url, contracts_path, metadata_agent_auth=None):
        """init the basic OceanClient for the connection and contract info"""
        self._client = Client(ocean_url, contracts_path, metadata_agent_auth)

    def register_asset(self, metadata, did):
        """
        Register an asset by writing it's meta data to the meta storage agent
        :param metadata: dict of the metadata, munt contain the key ['base']
        :param did: did of the meta storage agent
        :return The new asset registered, or return None on error
        """
        asset = Asset(self._client)
        if asset.register(metadata, did):
            return asset
        return None

    def register_agent(self, name, endpoint, account, did=None):
        """
        Register an agent with the ocean network
        :param name: name of the agent's endpoint in the DDO record.
        :param endpoint: url of the agents end point.
        :param account: ethereum account to register for.
        :param did: optional did of the current DID to update.
        :returns a valid agent object, and the DDO private password
        """
        agent = Agent(self._client)
        if did is None:
            # if no did then we need to create a new one
            did = id_to_did(secrets.token_hex(32))
        ddo_password = agent.register(did, name, endpoint, account)
        if ddo_password:
            return agent, ddo_password
        return None

    def register_agent_metadata(self, endpoint, account, did=None):
        """convenience method to register a metadata storage agent URL"""
        return self.register_agent(METADATA_AGENT_ENDPOINT_NAME, endpoint, account, did)

    def get_agent(self, did):
        """return an agent that is registered with the did"""
        agent = Agent(self._client, did)
        if agent.ddo:
            return agent
        return None

    def get_asset(self, did):
        """return a registered asset given a DID of the asset"""
        asset = Asset(self._client, did)
        if not asset.is_empty:
            if asset.read_metadata():
                return asset
        return None

    @property
    def client(self):
        """return the OceanClient used to access the ocean network"""
        return self._client
