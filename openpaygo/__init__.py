from .metrics_request import MetricsRequestHandler
from .metrics_response import MetricsResponseHandler
from .metrics_shared import AuthMethod
from .token_decode import OpenPAYGOTokenDecoder
from .token_encode import OpenPAYGOTokenEncoder
from .token_shared import TokenType


def generate_token(**kwargs):
    return OpenPAYGOTokenEncoder.generate_token(**kwargs)


def decode_token(**kwargs):
    return OpenPAYGOTokenDecoder.decode_token(**kwargs)


__all__ = [
    MetricsRequestHandler,
    MetricsResponseHandler,
    AuthMethod,
    OpenPAYGOTokenDecoder,
    OpenPAYGOTokenEncoder,
    TokenType,
]
