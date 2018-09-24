from squid_py.constants import OCEAN_ACL_CONTRACT


class Auth(object):

    def __init__(self, web3_helper):
        auth = web3_helper.load(OCEAN_ACL_CONTRACT, 'auth')
        self.concise_contract = auth[0]
        self.contract = auth[1]
        self.address = web3_helper.to_checksum_address(auth[2])

    def cancel_access_request(self, order_id, sender_address):
        return self.concise_contract.cancelAccessRequest(order_id, call={'from': sender_address})

    def get_order_status(self, order_id):
        return self.concise_contract.statusOfAccessRequest(order_id)

    def get_encrypted_access_token(self, order_id, sender_address):
        return self.concise_contract.getEncryptedAccessToken(order_id, call={'from': sender_address})
