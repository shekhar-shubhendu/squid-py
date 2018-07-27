from web3py_wrapper.ocean_contracts import OceanContracts

ocn_contracts = OceanContracts()
ocn_contracts.init_contracts()
market_concise = ocn_contracts.concise_contracts['Market.json']
market = ocn_contracts.contracts['Market.json']


def test_connect():
    assert '0.3' == market_concise.version()
