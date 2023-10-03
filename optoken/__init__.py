from .encode_token import OpenPAYGOTokenEncoder
from .shared import TokenType


def generate_token(**kwargs):
    return OpenPAYGOTokenEncoder.generate_token(**kwargs)