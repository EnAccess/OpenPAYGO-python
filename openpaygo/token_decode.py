from .token_shared import OpenPAYGOTokenShared, TokenType
from .token_shared_extended import OpenPAYGOTokenSharedExtended


class OpenPAYGOTokenDecoder(object):
    MAX_TOKEN_JUMP = 64
    MAX_TOKEN_JUMP_COUNTER_SYNC = 100
    MAX_UNUSED_OLDER_TOKENS = 8*2

    @classmethod
    def decode_token(cls, token, secret_key, count, used_counts=None, starting_code=None, value_divider=1, restricted_digit_set=False):
        secret_key = OpenPAYGOTokenShared.load_secret_key_from_hex(secret_key)
        if not starting_code:
            # We generate the starting code from the key if not provided
            starting_code = OpenPAYGOTokenShared.generate_starting_code(secret_key)
        if not restricted_digit_set:
            if len(token) <= 9:
                extended_token = False
            elif len(token) <= 12:
                extended_token = True
            else:
                raise ValueError("Token is too long")
        elif restricted_digit_set:
            if len(token) <= 15:
                extended_token = False
            elif len(token) <= 20:
                extended_token = True
            else:
                raise ValueError("Token is too long")
        token = int(token)
        if not extended_token:
            value, token_type, count, updated_counts = cls.get_activation_value_count_and_type_from_token(token, starting_code, secret_key, count, restricted_digit_set, used_counts)
        else:
            value, token_type, count, updated_counts = cls.get_activation_value_count_from_extended_token(token, starting_code, secret_key, count, restricted_digit_set, used_counts)
        if value and value_divider:
            value = value / value_divider
        return value, token_type, count, updated_counts

    @classmethod
    def get_activation_value_count_and_type_from_token(cls, token, starting_code, key, last_count,
                                                       restricted_digit_set=False, used_counts=None):
        if restricted_digit_set:
            token = OpenPAYGOTokenShared.convert_from_4_digit_token(token)
        valid_older_token = False
        token_base = OpenPAYGOTokenShared.get_token_base(token)  # We get the base of the token
        current_code = OpenPAYGOTokenShared.put_base_in_token(starting_code, token_base)  # We put it into the starting code
        starting_code_base = OpenPAYGOTokenShared.get_token_base(starting_code)  # We get the base of the starting code
        value = cls._decode_base(starting_code_base, token_base)  # If there is a match we get the value from the token
        # We try all combination up until last_count + TOKEN_JUMP, or to the larger jump if syncing counter
        # We could start directly the loop at the last count if we kept the token value for the last count
        if value == OpenPAYGOTokenShared.COUNTER_SYNC_VALUE:
            max_count_try = last_count + cls.MAX_TOKEN_JUMP_COUNTER_SYNC + 1
        else:
            max_count_try = last_count + cls.MAX_TOKEN_JUMP + 1
        for count in range(0, max_count_try):
            masked_token = OpenPAYGOTokenShared.put_base_in_token(current_code, token_base)
            if count % 2:
                if value == OpenPAYGOTokenShared.COUNTER_SYNC_VALUE:
                    this_type = TokenType.COUNTER_SYNC
                elif value == OpenPAYGOTokenShared.PAYG_DISABLE_VALUE:
                    this_type = TokenType.DISABLE_PAYG
                else:
                    this_type = TokenType.SET_TIME
            else:
                this_type = TokenType.ADD_TIME
            if masked_token == token:
                if cls._count_is_valid(count, last_count, value, this_type, used_counts):
                    updated_counts = cls.update_used_counts(used_counts, value, count, this_type)
                    return value, this_type, count, updated_counts
                else:
                    valid_older_token = True
            current_code = OpenPAYGOTokenShared.generate_next_token(current_code, key)  # If not we go to the next token
        if valid_older_token:
            return None, TokenType.ALREADY_USED, None, None
        return None, TokenType.INVALID, None, None

    @classmethod
    def _count_is_valid(cls, count, last_count, value, type, used_counts):
        if value == OpenPAYGOTokenShared.COUNTER_SYNC_VALUE:
            if count > (last_count - cls.MAX_TOKEN_JUMP):
                return True
        elif count > last_count:
            return True
        elif cls.MAX_UNUSED_OLDER_TOKENS > 0:
            if count > last_count - cls.MAX_UNUSED_OLDER_TOKENS:
                if count not in used_counts and type == TokenType.ADD_TIME:
                    return True
        return False

    @classmethod
    def update_used_counts(cls, past_used_counts, value, new_count, type):
        if not past_used_counts:
            return None
        highest_count = max(past_used_counts) if past_used_counts else 0
        if new_count > highest_count:
            highest_count = new_count
        bottom_range = highest_count-cls.MAX_UNUSED_OLDER_TOKENS
        used_counts = []
        if type != TokenType.ADD_TIME or value == OpenPAYGOTokenShared.COUNTER_SYNC_VALUE or value == OpenPAYGOTokenShared.PAYG_DISABLE_VALUE:
            # If it is not an Add-Time token, we mark all the past tokens as used in the range
            for count in range(bottom_range, highest_count+1):
                used_counts.append(count)
        else:
            # If it is an Add-Time token, we just mark the tokens actually used in the range
            for count in range(bottom_range, highest_count+1):
                if count == new_count or count in past_used_counts:
                    used_counts.append(count)
        return used_counts

    @classmethod
    def _decode_base(cls, starting_code_base, token_base):
        decoded_value = token_base - starting_code_base
        if decoded_value < 0:
            return decoded_value + 1000
        else:
            return decoded_value

    @classmethod
    def get_activation_value_count_from_extended_token(cls, token, starting_code, key, last_count,
                                                       restricted_digit_set=False, used_counts=None):
        if restricted_digit_set:
            token = OpenPAYGOTokenSharedExtended.convert_from_4_digit_token(token)
        token_base = OpenPAYGOTokenSharedExtended.get_token_base(token) # We get the base of the token
        current_code = OpenPAYGOTokenSharedExtended.put_base_in_token(starting_code, token_base) # We put it into the starting code
        starting_code_base = OpenPAYGOTokenSharedExtended.get_token_base(starting_code) # We get the base of the starting code
        value = cls._decode_base_extended(starting_code_base, token_base)  # If there is a match we get the value from the token
        max_count_try = last_count + cls.MAX_TOKEN_JUMP + 1
        for count in range(0, max_count_try):
            masked_token = OpenPAYGOTokenSharedExtended.put_base_in_token(current_code, token_base)
            if count % 2:
                this_type = TokenType.SET_TIME
            else:
                this_type = TokenType.ADD_TIME
            if masked_token == token:
                if cls._count_is_valid(count, last_count, value, this_type, used_counts):
                    updated_counts = cls.update_used_counts(used_counts, value, count, this_type)
                    return value, this_type, count, updated_counts
                else:
                    valid_older_token = True
            current_code = OpenPAYGOTokenSharedExtended.generate_next_token(current_code, key) # If not we go to the next token
        if valid_older_token:
            return None, TokenType.ALREADY_USED, None, None
        return None, TokenType.INVALID, None, None

    @classmethod
    def _decode_base_extended(cls, starting_code_base, token_base):
        decoded_value = token_base - starting_code_base
        if decoded_value < 0:
            return decoded_value + 1000000
        else:
            return decoded_value
