from web3 import Web3

from squid_py.utils import utilities


def test_split_signature():
    signature = b'\x19\x15!\xecwnX1o/\xdeho\x9a9\xdd9^\xbb\x8c2z\x88!\x95\xdc=\xe6\xafc\x0f\xe9\x14\x12\xc6\xde\x0b\n\xa6\x11\xc0\x1cvv\x9f\x99O8\x15\xf6f\xe7\xab\xea\x982Ds\x0bX\xd9\x94\xa42\x01'
    split_signature = utilities.split_signature(Web3, signature=signature)
    assert split_signature.v == 28
    assert split_signature.r == b'\x19\x15!\xecwnX1o/\xdeho\x9a9\xdd9^\xbb\x8c2z\x88!\x95\xdc=\xe6\xafc\x0f\xe9'
    assert split_signature.s == b'\x14\x12\xc6\xde\x0b\n\xa6\x11\xc0\x1cvv\x9f\x99O8\x15\xf6f\xe7\xab\xea\x982Ds\x0bX\xd9\x94\xa42'


def test_convert():
    input_text = "my text"
    print("output %s" % utilities.convert_to_string(Web3, utilities.convert_to_bytes(Web3, input_text)))
    assert utilities.convert_to_text(Web3, utilities.convert_to_bytes(Web3, input_text)) == input_text
