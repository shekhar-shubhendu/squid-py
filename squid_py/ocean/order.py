from .ocean_base import OceanBase


class Order(OceanBase):

    def __init__(self, id, asset, timeout, pub_key, key, paid, status):
        OceanBase.__init__(id)
        self.asset = asset
        self.asset_id = self.asset.id
        self.timeout = timeout
        self.pub_key = pub_key
        self.key = key
        self.paid = paid
        self.status = status

    def verify_payment(self):
        return

    def pay(self):
        return

    def commit(self):
        return

    def consume(self):
        return
