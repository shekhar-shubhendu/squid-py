from ocean_web3.consumer import register, consume
from ocean_web3.ocean_contracts import OceanContractsWrapper

json_consume = {"publisherId": "0x01",
                "metadata": {
                    "name": "testzkp",
                    "links": "https://testocnfiles.blob.core.windows.net/testfiles/testzkp.pdf",
                    "size": "1.08MiB",
                    "format": "pdf",
                    "description": "description"
                },
                "assetId": "0x01"}
json_request_consume = {
    'requestId': "",
    'consumerId': "",
    'fixed_msg': "",
    'sigEncJWT': ""
}


def test_register_consume():
    ocean = OceanContractsWrapper(host='http://0.0.0.0', port=8545)
    resouce_id = register(publisher_account=ocean.web3.eth.accounts[1],
                          provider_account=ocean.web3.eth.accounts[0],
                          price=10,
                          ocean_contracts_wrapper=ocean,
                          json_metadata=json_consume,
                          provider_host='http://0.0.0.0:5000'
                          )
    consum = consume(resource=resouce_id,
                     consumer_account=ocean.web3.eth.accounts[2],
                     provider_account=ocean.web3.eth.accounts[0],
                     ocean_contracts_wrapper=ocean,
                     json_metadata=json_request_consume)
    assert consum.status_code == 200
