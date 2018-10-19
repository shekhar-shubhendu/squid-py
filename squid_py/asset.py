class Asset:
    def __init__(self, asset_id, publisher_id, price):
        """
        Represent an asset in the MetaData store

        :param asset_id:
        :param publisher_id:
        :param price:
        """

        self.asset_id = asset_id
        self.publisher_id = publisher_id
        self.price = price


    def purchase(self, consumer, timeout):
        """
        Generate an order for purchase of this Asset

        :param timeout:
        :param consumer: Account object of the requester
        :return: Order object
        """
        # Check if asset exists

        # Approve the token transfer

        # Submit access request

        return

    def consume(self, order, consumer):
        """

        :param order: Order object
        :param consumer: Consumer Account
        :return: access_url
        :rtype: string
        :raises :
        """

        # Get access token (jwt)

        # Download the asset from the provider using the URL in access token
        # Decode the the access token, get service_endpoint and request_id

        return

    def get_DDO(self):
        """

        :return:
        """

    def get_DID(self):
        pass

    def publish_metadata(self):
        pass

    def get_metadata(self):
        pass

    def update_metadata(self):
        pass

    def retire_metadata(self):
        pass

    def get_service_agreements(self):
        pass
