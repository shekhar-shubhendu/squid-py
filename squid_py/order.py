
class Order:
    def __init__(self, order_id, asset_id):
        """

        :param order_id:
        :param asset_id:
        """

        self._id = order_id

    def get_status(self):
        return 0

    def verify_payment(self):
        return False

    def commit(self):
        return False

    def pay(self):
        return ''

    def consume(self):
        return ''
