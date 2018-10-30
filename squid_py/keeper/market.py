import logging

from web3 import Web3

from squid_py.constants import OCEAN_MARKET_CONTRACT
from squid_py.keeper.contract_base import ContractBase

DEFAULT_GAS_LIMIT = 400000


class Market(ContractBase):

    def __init__(self, web3, contract_path, address):
        ContractBase.__init__(self, web3, OCEAN_MARKET_CONTRACT, 'market', contract_path, address)
        self._defaultGas = DEFAULT_GAS_LIMIT

    # call functions (costs no gas)
    def check_asset(self, asset_id):
        """
        Check that this particular asset is already registered on chain."
        :param asset_id: ID of the asset to check for existance
        :return: Boolean
        """
        asset_id_bytes = Web3.toBytes(hexstr=asset_id)
        return self.contract_concise.checkAsset(asset_id_bytes)

    def verify_order_payment(self, order_id):
        return self.contract_concise.verifyPaymentReceived(order_id)

    def get_asset_price(self, asset_id):
        """Return the price of an asset already registered."""
        asset_id_bytes = Web3.toBytes(hexstr=asset_id)
        try:
            return self.contract_concise.getAssetPrice(asset_id_bytes)
        except Exception:
            logging.error("There are no assets registered with id: %s" % asset_id)

    # Transactions with gas cost
    def request_tokens(self, amount, address):
        """Request an amount of tokens for a particular address."""
        try:
            receipt = self.contract_concise.requestTokens(amount, transact={'from': address})
            logging.info("{} requests {} tokens, returning receipt".format(address, amount))
            return receipt
        except:
            # TODO: Specify error
            raise
            return False

    def register_asset(self, asset, price, publisher_address):
        """
        Register an asset on chain.

        Calls the OceanMarket.register function, .sol code below:

            function register(bytes32 assetId, uint256 price) public validAddress(msg.sender) returns (bool success) {
                require(mAssets[assetId].owner == address(0), 'Owner address is not 0x0.');
                mAssets[assetId] = Asset(msg.sender, price, false);
                mAssets[assetId].active = true;

                emit AssetRegistered(assetId, msg.sender);
                return true;
            }

        :param asset:
        :param price:
        :param publisher_address:
        :return:
        """
        asset_id_bytes = Web3.toBytes(hexstr=asset.asset_id)
        assert asset_id_bytes
        assert len(asset_id_bytes) == 32
        # assert all(c in string.hexdigits for c in asset.asset_id)

        result = self.contract_concise.register(
            asset_id_bytes,
            price,
            transact={'from': publisher_address, 'gas': self._defaultGas}
        )

        self.get_tx_receipt(result)
        logging.info("Registered Asset {} into blockchain".format(asset.asset_id))
        return result

    def purchase_asset(self, asset_id, order, publisher_address, sender_address):
        asset_id_bytes = Web3.toBytes(hexstr=asset_id)
        asset_price = self.contract.getAssetPrice(asset_id_bytes)
        return self.contract.sendPayment(order.id, publisher_address, asset_price, order.timeout, {
            'from': sender_address,
            'gas': self._defaultGas
        })

    def calculate_message_hash(self, message):
        return self.contract_concise.generateId(message)

    def generate_did(self, content):
        pass

    def resolve_did(self, did):
        pass
