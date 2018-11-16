"""
    OceanAgent class to provide basic functionality for all Ocean Agents
"""
from squid_py.ddo import DDO
from squid_py.didresolver import DIDResolver

class OceanAgent():
    def __init__(self, client, did=None):
        """init the Agent with a connection client and optional DID"""
        self._client = client
        self._did = did
        self._ddo = None
        # if DID then try to load in the linked DDO
        if did:
            self._ddo = self._resolve_did_to_ddo(self._did)

    def register(self, did, name, endpoint, account):
        """
        Register this agent on the block chain
        :param did: DID of the agent to register
        :param name: name of the service endpoint to register
        :param endpoint: URL of the agents service to register
        :param account: Ethereum account to use as the owner of the DID->DDO registration
        :return private password of the signed DDO
        """
        self._did = did

        # create a new DDO
        self._ddo = DDO(self._did)
        # add a signature
        private_password = self._ddo.add_signature()
        # add the service endpoint with the meta data
        self._ddo.add_service(name, endpoint)
        # add the static proof
        self._ddo.add_proof(0, private_password)
        # register/update the did->ddo to the block chain
        self._client.keeper.didregistry.register(did, ddo=self._ddo, account=account)

        return private_password

    @property
    def ddo(self):
        """return the DDO stored for this agent"""
        return self._ddo

    @property
    def did(self):
        """return the DID used for this agent"""
        return self._did

    def _resolve_did_to_ddo(self, did):
        """resolve a DID to a given DDO, return the DDO if found"""
        did_resolver = DIDResolver(self._client.web3, self._client.keeper.didregistry)
        resolved = did_resolver.resolve(did)
        if resolved and resolved.is_ddo:
            ddo = DDO(json_text = resolved.value)
            return ddo
        return None

    def _get_endpoint(self, name):
        """return the endpoint based on the service name"""
        if self._ddo:
            service = self._ddo.get_service(name)
            if service:
                return service.get_endpoint()
        return None


