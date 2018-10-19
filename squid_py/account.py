

class Account:
    def __init__(self, keeper, address):
        """
        Hold account address, and update balances of Ether and Ocean token

        :param keeper: The instantiated Keeper
        :param address: The address of this account
        """
        self.keeper = keeper
        self.address = address

        # Inititalize the balances with the current values from the Blockchain
        self.ether = self.get_ether_balance()
        self.ocean = self.get_ocean_balance()

    def get_ether_balance(self):
        """
        Call the Token contract method .web3.eth.getBalance()
        :return: Ether balance, int
        """
        self.ether = self.keeper.token.get_ether_balance(self.address)
        return self.ether

    def get_ocean_balance(self):
        """
        Call the Token contract method .balanceOf(account_address)
        :return: Ocean token balance, int
        """
        self.ocean = self.keeper.token.get_token_balance(self.address)
        return self.ocean

    def request_tokens(self,amount):
        return self.keeper.market.request_tokens(amount,self.address)

    def get_balance(self):
        pass

    def __str__(self):
        return "Account {} with {} Eth, {} Ocean".format(self.address, self.ether, self.ocean)
