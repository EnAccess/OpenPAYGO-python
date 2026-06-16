import copy
from typing import Any, Dict, List, Optional, Union

from .metrics_shared import OpenPAYGOMetricsShared
from .models import MetricsDataFormat, MetricsHistoricalDataStep


class MetricsRequestHandler(object):
    def __init__(
        self,
        serial_number: str,
        data_format: Optional[Union[Dict[str, Any], MetricsDataFormat]] = None,
        secret_key: Optional[str] = None,
        auth_method: Optional[str] = None,
    ) -> None:
        self.secret_key = secret_key
        self.auth_method = auth_method
        self.request_dict: Dict[str, Any] = {
            "serial_number": serial_number,
        }
        if data_format is not None:
            self.data_format: Optional[Dict[str, Any]] = dict(data_format)
        else:
            self.data_format = None

        if self.data_format:
            if self.data_format.get("id"):
                self.request_dict["data_format_id"] = self.data_format.get("id")
            else:
                self.request_dict["data_format"] = self.data_format
        self.data: Dict[str, Any] = {}
        self.historical_data: List[Dict[str, Any]] = []

    def set_request_count(self, request_count: int) -> None:
        self.request_dict["request_count"] = request_count

    def set_timestamp(self, timestamp: int) -> None:
        self.request_dict["timestamp"] = timestamp

    def set_data(self, data: Dict[str, Any]) -> None:
        self.data = data

    def set_historical_data(
        self, historical_data: List[Union[Dict[str, Any], MetricsHistoricalDataStep]]
    ) -> None:
        validated_historical_data = []
        for time_step in historical_data:
            step = dict(time_step)
            validated_historical_data.append(step)

        if self.data_format and not self.data_format.get("historical_data_interval"):
            for time_step in validated_historical_data:
                if not time_step.get("timestamp"):
                    raise ValueError(
                        "Historical Data objects must have a time stamp if no "
                        "historical_data_interval is defined."
                    )
        self.historical_data = validated_historical_data

    def get_simple_request_payload(self) -> str:
        payload = self.get_simple_request_dict()
        return OpenPAYGOMetricsShared.convert_to_metrics_json(payload)

    def get_simple_request_dict(self) -> Dict[str, Any]:
        simple_request = self.request_dict
        simple_request["data"] = self.data
        simple_request["historical_data"] = self.historical_data
        # We prepare the auth
        if self.auth_method:
            simple_request["auth"] = (
                OpenPAYGOMetricsShared.generate_request_signature_from_data(
                    simple_request, self.auth_method, self.secret_key
                )
            )
        return simple_request

    def get_condensed_request_payload(self) -> str:
        payload = self.get_condensed_request_dict()
        return OpenPAYGOMetricsShared.convert_to_metrics_json(payload)

    def get_condensed_request_dict(self) -> Dict[str, Any]:
        if not self.data_format:
            raise ValueError("No Data Format provided for condensed request")
        data_order = self.data_format.get("data_order") or []
        if self.data and not data_order:
            raise ValueError("Data Format does not contain data_order")
        historical_data_order = self.data_format.get("historical_data_order") or []
        if self.historical_data and not historical_data_order:
            raise ValueError("Data Format does not contain historical_data_order")
        condensed_request = copy.deepcopy(self.request_dict)
        condensed_request["data"] = []
        condensed_request["historical_data"] = []
        # We add the data
        data_copy = copy.deepcopy(self.data)
        for var in data_order:
            condensed_request["data"].append(
                data_copy.pop(var) if var in data_copy else None
            )
        if len(data_copy) > 0:
            raise ValueError(
                "Additional variables not present in the data format: " + str(data_copy)
            )
        condensed_request["data"] = (
            OpenPAYGOMetricsShared.remove_trailing_empty_elements(
                condensed_request["data"]
            )
        )
        # We add the historical data
        historical_data_copy = copy.deepcopy(self.historical_data)
        for time_step in historical_data_copy:
            time_step_data = []
            for var in historical_data_order:
                time_step_data.append(time_step.pop(var) if var in time_step else None)
            if len(time_step) > 0:
                raise ValueError(
                    "Additional variables not present in the historical data format: "
                    + str(time_step)
                )
            time_step_data = OpenPAYGOMetricsShared.remove_trailing_empty_elements(
                time_step_data
            )
            condensed_request["historical_data"].append(time_step_data)
        # We prepare the auth
        if self.auth_method:
            condensed_request["auth"] = (
                OpenPAYGOMetricsShared.generate_request_signature_from_data(
                    condensed_request, self.auth_method, self.secret_key
                )
            )
        # We replace the key names by the condensed ones
        condensed_request = OpenPAYGOMetricsShared.convert_dict_keys_to_condensed(
            condensed_request
        )
        return condensed_request
