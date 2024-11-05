import json

import pytest

from openpaygo import OpenPAYGOTokenEncoder, TokenType

with open("test/test_tokens.jsonl") as f:
    sample_data = [json.loads(line) for line in f]


@pytest.fixture
def encoder():
    return OpenPAYGOTokenEncoder()


@pytest.fixture
def token_type_lookup():
    return {
        "ADD_TIME": TokenType.ADD_TIME,
        "SET_TIME": TokenType.SET_TIME,
        "DISABLE_PAYG": TokenType.DISABLE_PAYG,
        "COUNTER_SYNC": TokenType.COUNTER_SYNC,
    }


@pytest.mark.parametrize("data", sample_data)
def test_generate_token(encoder, token_type_lookup, data):
    new_count, final_token = encoder.generate_token(
        secret_key=data["key"],
        count=data["count"],
        value=data["value_raw"],
        token_type=token_type_lookup[data["token_type"]],
        starting_code=data["starting_code"],
        restricted_digit_set=data["restricted_digit_set"],
        extended_token=data["extended_token"],
    )

    assert new_count == data["new_count"]
    assert final_token == data["token"]
