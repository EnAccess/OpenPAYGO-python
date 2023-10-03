from .encode_token import OpenPAYGOTokenEncoder
from .decode_token import OpenPAYGOTokenDecoder
from .shared import TokenType


def generate_token(**kwargs):
    return OpenPAYGOTokenEncoder.generate_token(**kwargs)


def decode_token(**kwargs):
    return OpenPAYGOTokenDecoder.decode_token(**kwargs)