from datetime import datetime, timedelta

from openpaygo.token_decode import OpenPAYGOTokenDecoder, TokenType
from openpaygo.token_shared import OpenPAYGOTokenShared


class DeviceSimulator(object):

    def __init__(
        self,
        starting_code,
        key,
        starting_count=1,
        restricted_digit_set=False,
        waiting_period_enabled=True,
        time_divider=1,
    ):
        self.starting_code = starting_code
        self.key = key
        self.time_divider = time_divider
        self.restricted_digit_set = restricted_digit_set
        self.waiting_period_enabled = (
            waiting_period_enabled  # Should always be true except for testing
        )

        self.payg_enabled = True
        self.count = starting_count
        self.expiration_date = datetime.now()
        self.invalid_token_count = 0
        self.token_entry_blocked_until = datetime.now()
        self.used_counts = []

    def print_status(self):
        print("-------------------------")
        print("Expiration Date: " + str(self.expiration_date))
        print("Current count: " + str(self.count))
        print("PAYG Enabled: " + str(self.payg_enabled))
        print("Active: " + str(self.is_active()))
        print("-------------------------")

    def is_active(self):
        return self.expiration_date > datetime.now()

    def enter_token(self, token, show_result=True):
        if len(token) == 9:
            token_int = int(token)
            return self._update_device_status_from_token(token_int, show_result)
        else:
            token_int = int(token)
            return self._update_device_status_from_extended_token(
                token_int, show_result
            )

    def get_days_remaining(self):
        if self.payg_enabled:
            td = self.expiration_date - datetime.now()
            days, hours, minutes = td.days, td.seconds // 3600, (td.seconds // 60) % 60
            days = days + (hours + minutes / 60) / 24
            return round(days)
        else:
            return "infinite"

    def _update_device_status_from_token(self, token, show_result=True):
        if (
            self.token_entry_blocked_until > datetime.now()
            and self.waiting_period_enabled
        ):
            if show_result:
                print("TOKEN_ENTRY_BLOCKED")
            return False

        token_value, token_type, token_count, updated_counts = (
            OpenPAYGOTokenDecoder.get_activation_value_count_and_type_from_token(
                token=token,
                starting_code=self.starting_code,
                key=self.key,
                last_count=self.count,
                restricted_digit_set=self.restricted_digit_set,
                used_counts=self.used_counts,
            )
        )
        if token_value is None:
            if token_type == TokenType.ALREADY_USED:
                if show_result:
                    print("OLD_TOKEN")
                return -2
            if show_result:
                print("TOKEN_INVALID")
            self.invalid_token_count += 1
            self.token_entry_blocked_until = datetime.now() + timedelta(
                minutes=2**self.invalid_token_count
            )
            return -1
        elif token_value == -2:
            if show_result:
                print("OLD_TOKEN")
            return -2
        else:
            if show_result:
                print("TOKEN_VALID", " | Value:", token_value)
            if (
                token_count > self.count
                or token_value == OpenPAYGOTokenShared.COUNTER_SYNC_VALUE
            ):
                self.count = token_count
            self.used_counts = updated_counts
            self.invalid_token_count = 0
            self._update_device_status_from_token_value(token_value, token_type)
            return 1

    def _update_device_status_from_extended_token(self, token, show_result=True):
        if (
            self.token_entry_blocked_until > datetime.now()
            and self.waiting_period_enabled
        ):
            if show_result:
                print("TOKEN_ENTRY_BLOCKED")

        token_value, token_count = (
            OpenPAYGOTokenDecoder.get_activation_value_count_from_extended_token(
                token=token,
                starting_code=self.starting_code,
                key=self.key,
                last_count=self.count,
                restricted_digit_set=self.restricted_digit_set,
            )
        )
        if token_value is None:
            if show_result:
                print("TOKEN_INVALID")
            self.invalid_token_count += 1
            self.token_entry_blocked_until = datetime.now() + timedelta(
                minutes=2**self.invalid_token_count
            )
        else:
            if show_result:
                print("Special token entered, value: " + str(token_value))

    def _update_device_status_from_token_value(self, token_value, token_type):
        if token_value <= OpenPAYGOTokenShared.MAX_ACTIVATION_VALUE:
            if not self.payg_enabled and token_type == TokenType.SET_TIME:
                self.payg_enabled = True
            if self.payg_enabled:
                self._update_expiration_date_from_value(token_value, token_type)
        elif token_value == OpenPAYGOTokenShared.PAYG_DISABLE_VALUE:
            self.payg_enabled = False
        elif token_value != OpenPAYGOTokenShared.COUNTER_SYNC_VALUE:
            # We do nothing if its the sync counter value, the counter has been synced
            # already
            print("COUNTER_SYNCED")
        else:
            # If it's another value we also do nothing, as they are not defined
            print("UNKNOWN_COMMAND")

    def _update_expiration_date_from_value(self, toke_value, token_type):
        number_of_days = toke_value / self.time_divider
        if token_type == TokenType.SET_TIME:
            self.expiration_date = datetime.now() + timedelta(days=number_of_days)
        else:
            if self.expiration_date < datetime.now():
                self.expiration_date = datetime.now()
            self.expiration_date = self.expiration_date + timedelta(days=number_of_days)
