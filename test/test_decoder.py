import json

import pytest

from openpaygo import OpenPAYGOTokenDecoder, TokenType

with open("test/test_tokens.jsonl") as f:
    sample_data = [json.loads(line) for line in f]


@pytest.fixture
def decoder():
    return OpenPAYGOTokenDecoder()


@pytest.fixture
def token_type_lookup():
    return {
        "ADD_TIME": TokenType.ADD_TIME,
        "SET_TIME": TokenType.SET_TIME,
        "DISABLE_PAYG": TokenType.DISABLE_PAYG,
        "COUNTER_SYNC": TokenType.COUNTER_SYNC,
    }


@pytest.mark.parametrize("data", sample_data)
def test_parse_token(decoder, token_type_lookup, data):
    token_value, token_type, new_count, _ = decoder.decode_token(
        secret_key=data["key"],
        starting_code=data["starting_code"],
        restricted_digit_set=data["restricted_digit_set"],
        token=data["token"],
        count=data["count"],
    )

    assert token_value == data["value_raw"]
    assert token_type == token_type_lookup[data["token_type"]]
    assert new_count == data["new_count"]
