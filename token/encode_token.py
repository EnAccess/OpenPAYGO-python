from shared import OpenPAYGOTokenShared
from shared_extended import OpenPAYGOTokenSharedExtended


class OpenPAYGOTokenEncoder(object):

    @classmethod
    def generate_token(cls, secret_key, value, count, set_mode=False, starting_code=None, value_divider=1, restricted_digit_set=False, extended_token=False):
        if not starting_code:
            # We generate the starting code from the key if not provided
            starting_code = cls.generate_starting_code(secret_key)
        if set_mode:
            mode = OpenPAYGOTokenShared.TOKEN_TYPE_SET_TIME
        else:
            mode = OpenPAYGOTokenShared.TOKEN_TYPE_ADD_TIME
        value = int(round(value / value_divider))
        if extended_token:
            return cls.generate_extended_token(starting_code, secret_key, value, count, mode, restricted_digit_set)
        else:
            return cls.generate_standard_token(starting_code, secret_key, value, count, mode, restricted_digit_set)

    @classmethod
    def generate_standard_token(cls, starting_code=None, key=None, value=None, count=None,
                                mode=OpenPAYGOTokenShared.TOKEN_TYPE_SET_TIME, restricted_digit_set=False):
        # We get the first 3 digits with encoded value
        starting_code_base = OpenPAYGOTokenShared.get_token_base(starting_code)
        token_base = cls._encode_base(starting_code_base, value)
        current_token = OpenPAYGOTokenShared.put_base_in_token(starting_code, token_base)
        new_count = cls._get_new_count(count, mode)
        for xn in range(0, new_count):
            current_token = OpenPAYGOTokenShared.generate_next_token(current_token, key)
        final_token = OpenPAYGOTokenShared.put_base_in_token(current_token, token_base)
        if restricted_digit_set:
            final_token = OpenPAYGOTokenShared.convert_to_4_digit_token(final_token)
            final_token = '{:015d}'.format(final_token)
        else:
            final_token = '{:09d}'.format(final_token)
        return new_count, final_token

    @classmethod
    def _encode_base(cls, base, number):
        if number + base > 999:
            return number + base - 1000
        else:
            return number + base

    @classmethod
    def generate_extended_token(cls, starting_code, key, value, count, mode=OpenPAYGOTokenShared.TOKEN_TYPE_SET_TIME, restricted_digit_set=False):
        starting_code_base = OpenPAYGOTokenSharedExtended.get_token_base(starting_code)
        token_base = cls._encode_base_extended(starting_code_base, value)
        current_token = OpenPAYGOTokenSharedExtended.put_base_in_token(starting_code, token_base)
        new_count = cls._get_new_count(count, mode)
        for xn in range(0, new_count):
            current_token = OpenPAYGOTokenSharedExtended.generate_next_token(current_token, key)
        final_token = OpenPAYGOTokenSharedExtended.put_base_in_token(current_token, token_base)
        if restricted_digit_set:
            final_token = OpenPAYGOTokenSharedExtended.convert_to_4_digit_token(final_token)
            final_token = '{:020d}'.format(final_token)
        else:
            final_token = '{:012d}'.format(final_token)
        return new_count, final_token
    
    @classmethod
    def generate_starting_code(cls, key):
        # We make a hash of the key
        starting_hash = OpenPAYGOTokenShared.generate_hash(key, key)
        return OpenPAYGOTokenShared.convert_hash_to_token(starting_hash)

    @classmethod
    def _encode_base_extended(cls, base, number):
        if number + base > 999999:
            return number + base - 1000000
        else:
            return number + base
        
    @classmethod
    def _get_new_count(cls, count, mode):
        current_count_odd = count % 2
        if mode == OpenPAYGOTokenShared.TOKEN_TYPE_SET_TIME:
            if current_count_odd: # Odd numbers are for Set Time
                new_count = count+2
            else:
                new_count = count+1
        else:
            if current_count_odd: # Even numbers are for Add Time
                new_count = count+1
            else:
                new_count = count+2
        return new_count
