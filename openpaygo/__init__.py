from .token_encode import OpenPAYGOTokenEncoder
from .token_decode import OpenPAYGOTokenDecoder
from .token_shared import TokenType
from .metrics_request import MetricsRequestHandler
from .metrics_response import MetricsResponseHandler
from .metrics_shared import AuthMethod


def generate_token(**kwargs):
    return OpenPAYGOTokenEncoder.generate_token(**kwargs)


def decode_token(**kwargs):
    return OpenPAYGOTokenDecoder.decode_token(**kwargs)
