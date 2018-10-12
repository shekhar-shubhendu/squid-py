import logging

from squid_py.constants import (
    OCEAN_MARKET_CONTRACT
)
from squid_py.keeper.keeper_contract import (
    KeeperContract,
)

DEFAULT_GAS_LIMIT = 400000


class Market(KeeperContract):

    def __init__(self, web3_helper, contract_path, address):
        KeeperContract.__init__(self, web3_helper, OCEAN_MARKET_CONTRACT, 'market', contract_path, address)
        self._defaultGas = DEFAULT_GAS_LIMIT

    # call functions (costs no gas)
    def check_asset(self, asset_id):
        """Check that this particular asset is already registered on chain."""
        return self._contract_concise.checkAsset(asset_id)

    def verify_order_payment(self, order_id):
        return self._contract_concise.verifyPaymentReceived(order_id)

    def get_asset_price(self, asset_id):
        """Return the price of an asset already registered."""
        try:
            return self._contract_concise.getAssetPrice(asset_id)
        except Exception:
            logging.error("There are no assets registered with id: %s" % asset_id)

    # Transactions with gas cost
    def request_tokens(self, amount, address):
        """Request an amount of tokens for a particular address."""
        try:
            self._contract_concise.requestTokens(amount, transact={'from': address})
            logging.info("Requesting %s tokens" % amount)
            return True
        except:
            return False

    def register_asset(self, name, description, price, publisher_address):
        """Register an asset on chain."""
        asset_id = self._contract_concise.generateId(name + description)
        result = self._contract_concise.register(
            asset_id,
            price,
            transact={'from': publisher_address, 'gas': self._defaultGas}
        )
        self._helper.get_tx_receipt(result)
        logging.info('registered: %s' % result)
        return asset_id

    def purchase_asset(self, asset_id, order, publisher_address, sender_address):
        asset_price = self._contract.getAssetPrice(asset_id)
        return self._contract.sendPayment(order.id, publisher_address, asset_price, order.timeout, {
            'from': sender_address,
            'gas': self._defaultGas
        })

    def calculate_message_hash(self, message):
        return self._contract_concise.generateId(message)

    def generate_did(self, content):
        pass

    def resolve_did(self, did):
        pass
