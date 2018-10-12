import logging

from squid_py.constants import OCEAN_TOKEN_CONTRACT
from squid_py.keeper.keeper_contract import (
    KeeperContract,
)


class Token(KeeperContract):
    def __init__(self, web3_helper, contract_path, address):
        KeeperContract.__init__(self, web3_helper, OCEAN_TOKEN_CONTRACT, 'token', contract_path, address)

    def get_token_balance(self, account_address):
        """Retrieve the ammount of tokens of an account address"""
        return self._contract_concise.balanceOf(account_address)

    def token_approve(self, market_address, price, account_address):
        """Approve the passed address to spend the specified amount of tokens."""
        return self._contract_concise.approve(self._helper.to_checksum_address(market_address),
                                              price,
                                              transact={'from': account_address})

    def get_ether_balance(self, account_address):
        try:
            return self._helper.get_balance(account_address, 'latest')
        except Exception as e:
            logging.error(e)
            raise e
