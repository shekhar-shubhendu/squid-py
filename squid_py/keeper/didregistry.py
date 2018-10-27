from squid_py.constants import OCEAN_DID_REGISTRY_CONTRACT
from squid_py.keeper.contract_base import ContractBase

class DIDRegistry(ContractBase):
    def __init__(self, web3, contract_path, address):
        ContractBase.__init__(self, web3, OCEAN_DID_REGISTRY_CONTRACT, 'didregistry', contract_path, address)

    def register_attribute(self, did_hash, value_type, key, value, account_address ):
        """Register an DID attribute as an event on the block chain

            did_hash: 32 byte string/hex of the DID
            value_type: 0 = DID, 1 = DIDREf, 2 = URL, 3 = DDO
            key: 32 byte string/hex free format
            value: string can be anything, probably DDO or URL
            account_address: owner of this DID registration record
        """
        return self.contract_concise.registerAttribute(
                did_hash,
                value_type,
                key,
                value,
                transact={'from': account_address}
        )


    def get_update_at(self, did):
        return self.contract_concise.getUpdateAt(did)
