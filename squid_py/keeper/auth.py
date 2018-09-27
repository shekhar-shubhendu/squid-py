from squid_py.constants import OCEAN_ACL_CONTRACT


class Auth(object):

    def __init__(self, web3_helper):
        auth = web3_helper.load(OCEAN_ACL_CONTRACT, 'auth')
        self.concise_contract = auth[0]
        self.contract = auth[1]
        self.address = web3_helper.to_checksum_address(auth[2])

    def cancel_access_request(self, order_id, sender_address):
        """You can cancel consent and do refund only after consumer makes the payment and timeout."""
        return self.concise_contract.cancelAccessRequest(order_id, call={'from': sender_address})

    def initiate_access_request(self, asset_id, provider_address, pubkey, expiry, sender_address):
        """Consumer initiates access request of service"""
        return self.concise_contract.initiateAccessRequest(asset_id,
                                                           provider_address,
                                                           pubkey,
                                                           expiry,
                                                           transact={'from': sender_address})

    def commit_access_request(self, order_id, is_available, expiration_date, discovery, permissions,
                              access_agreement_ref, accesss_agreement_type, sender_address, gas_amount):
        """Provider commits the access request of service"""
        return self.concise_contract.commitAccessRequest(order_id,
                                                         is_available,
                                                         expiration_date,
                                                         discovery,
                                                         permissions,
                                                         access_agreement_ref,
                                                         accesss_agreement_type,
                                                         transact={
                                                             'from': sender_address,
                                                             'gas': gas_amount}
                                                         )

    def deliver_access_token(self, order_id, enc_jwt, sender_address):
        """Provider delivers the access token of service to on-chain"""
        return self.concise_contract.deliverAccessToken(order_id,
                                                        enc_jwt,
                                                        transact={'from': sender_address,
                                                                  'gas': 4000000})

    def get_order_status(self, order_id):
        return self.concise_contract.statusOfAccessRequest(order_id)

    def get_encrypted_access_token(self, order_id, sender_address):
        return self.concise_contract.getEncryptedAccessToken(order_id, call={'from': sender_address})
