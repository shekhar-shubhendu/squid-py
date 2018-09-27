import logging

from squid_py.constants import OCEAN_TOKEN_CONTRACT


class Token(object):
    def __init__(self, web3_helper):
        token = web3_helper.load(OCEAN_TOKEN_CONTRACT, 'token')
        self.helper = web3_helper
        self.contract_concise = token[0]
        self.contract = token[1]
        self.address = web3_helper.to_checksum_address(token[2])

    def get_token_balance(self, account_address):
        """Retrieve the ammount of tokens of an account address"""
        return self.contract_concise.balanceOf(account_address)

    def token_approve(self, market_address, price, account_address):
        return self.contract_concise.approve(self.helper.to_checksum_address(market_address),
                                             price,
                                             transact={'from': account_address})

    def get_eth_balance(self, account):
        try:
            return self.helper.web3.eth.getBalance(account, 'latest')
        except Exception as e:
            logging.error(e)
            raise e
