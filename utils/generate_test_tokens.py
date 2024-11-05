import json

from openpaygo import OpenPAYGOTokenEncoder, TokenType

encoder = OpenPAYGOTokenEncoder()

token_types = [
    "ADD_TIME",
    "SET_TIME",
    "DISABLE_PAYG",
    "COUNTER_SYNC",
]

token_add_set_time_values = [
    1,
    2,
    5,
    995,  # highest allowed value without special meaning
]
token_type_lookup = {
    "ADD_TIME": TokenType.ADD_TIME,
    "SET_TIME": TokenType.SET_TIME,
    "DISABLE_PAYG": TokenType.DISABLE_PAYG,
    "COUNTER_SYNC": TokenType.COUNTER_SYNC,
}

restricted_digit_set_values = [False, True]

extended_token_values = [False, True]

all_cases = [
    {
        "token_type": token_type,
        "token_value": token_value,
        "restricted_digit_set": restricted_digit_set,
        "extended_token": extended_token,
    }
    for token_type in token_types
    for token_value in (
        token_add_set_time_values if token_type in ["ADD_TIME", "SET_TIME"] else [None]
    )
    for restricted_digit_set in restricted_digit_set_values
    for extended_token in extended_token_values
]


def array_of_dicts_to_jsonl(array, filename):
    with open(filename, "w") as outfile:
        for item in array:
            json.dump(item, outfile)
            outfile.write("\n")


if __name__ == "__main__":
    device_data1 = {
        "serial_number": "TEST220000001",
        "starting_code": 516959010,
        "key": "bc41ec9530f6dac86b1a29ab82edc5fb",
        "count": 1,
    }
    device_data2 = {
        "serial_number": "TEST240000002",
        "starting_code": 432435255,
        "key": "dac86b1a29ab82edc5fbbc41ec9530f6",
        "count": 10,
    }

    test_cases = []

    # DEVICE 1
    for t in all_cases:
        new_count, final_token = encoder.generate_token(
            secret_key=device_data1["key"],
            count=device_data1["count"],
            value=t["token_value"],
            token_type=token_type_lookup[t["token_type"]],
            starting_code=device_data1["starting_code"],
            restricted_digit_set=t["restricted_digit_set"],
            extended_token=t["extended_token"],
        )

        result = {
            **device_data1,
            **{
                "token_type": t["token_type"],
                "value_raw": t["token_value"],
                "restricted_digit_set": t["restricted_digit_set"],
                "extended_token": t["extended_token"],
            },
            **{"new_count": new_count, "token": final_token.replace(" ", "")},
        }
        test_cases.append(result)

    # DEVICE 2
    for t in all_cases:
        new_count, final_token = encoder.generate_token(
            secret_key=device_data2["key"],
            count=device_data2["count"],
            value=t["token_value"],
            token_type=token_type_lookup[t["token_type"]],
            starting_code=device_data2["starting_code"],
            restricted_digit_set=t["restricted_digit_set"],
            extended_token=t["extended_token"],
        )

        result = {
            **device_data2,
            **{
                "token_type": t["token_type"],
                "value_raw": t["token_value"],
                "restricted_digit_set": t["restricted_digit_set"],
                "extended_token": t["extended_token"],
            },
            **{"new_count": new_count, "token": final_token.replace(" ", "")},
        }
        test_cases.append(result)

    array_of_dicts_to_jsonl(test_cases, "test/test_tokens.jsonl")
