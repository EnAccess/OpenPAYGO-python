from .token_decode import OpenPAYGOTokenDecoder
from .token_encode import OpenPAYGOTokenEncoder


def generate_token(**kwargs):
    return OpenPAYGOTokenEncoder.generate_token(**kwargs)


def decode_token(**kwargs):
    return OpenPAYGOTokenDecoder.decode_token(**kwargs)
