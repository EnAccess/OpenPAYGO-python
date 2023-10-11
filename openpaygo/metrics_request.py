from .metrics_shared import OpenPAYGOMetricsShared
import copy


class MetricsRequestHandler(object):

    def __init__(self, serial_number, data_format=None, secret_key=None, auth_method=None):
        self.secret_key = secret_key
        self.auth_method = auth_method
        self.request_dict = {
            'serial_number': serial_number,
        }
        self.data_format = data_format
        if self.data_format:
            if self.data_format.get('id'):
                self.request_dict['data_format_id'] = data_format.get('id')
            else:
                self.request_dict['data_format'] = data_format
        self.data = {}
        self.historical_data = {}

    def set_request_count(self, request_count):
        self.request_dict['request_count'] = request_count

    def set_timestamp(self, timestamp):
        self.request_dict['timestamp'] = timestamp

    def set_data(self, data):
        self.data = data

    def set_historical_data(self, historical_data):
        if not self.data_format.get('historical_data_interval'):
            for time_step in historical_data:
                if not time_step.get('timestamp'):
                    raise ValueError('Historical Data objects must have a time stamp if no historical_data_interval is defined.')
        self.historical_data = historical_data

    def get_simple_request_payload(self):
        payload = self.get_simple_request_dict()
        return OpenPAYGOMetricsShared.convert_to_metrics_json(payload)

    def get_simple_request_dict(self):
        simple_request = self.request_dict
        simple_request['data'] = self.data
        simple_request['historical_data'] = self.historical_data
        # We prepare the auth
        if self.auth_method:
            simple_request['auth'] = OpenPAYGOMetricsShared.generate_request_signature_from_data(simple_request, self.auth_method, self.secret_key)
        return simple_request

    def get_condensed_request_payload(self):
        payload = self.get_condensed_request_dict()
        return OpenPAYGOMetricsShared.convert_to_metrics_json(payload)

    def get_condensed_request_dict(self):
        if not self.data_format:
            raise ValueError('No Data Format provided for condensed request')
        data_order = self.data_format.get('data_order')
        if self.data and not data_order:
            raise ValueError('Data Format does not contain data_order')
        historical_data_order = self.data_format.get('historical_data_order')
        if self.historical_data and not historical_data_order:
            raise ValueError('Data Format does not contain historical_data_order')
        condensed_request = copy.deepcopy(self.request_dict)
        condensed_request['data'] = []
        condensed_request['historical_data'] = []
        # We add the data
        data_copy = copy.deepcopy(self.data)
        for var in data_order:
            condensed_request['data'].append(data_copy.pop(var) if var in data_copy else None)
        if len(data_copy) > 0:
            raise ValueError('Additional variables not present in the data format: '+str(data_copy))
        condensed_request['data'] = OpenPAYGOMetricsShared.remove_trailing_empty_elements(condensed_request['data'])
        # We add the historical data
        historical_data_copy = copy.deepcopy(self.historical_data)
        for time_step in historical_data_copy:
            time_step_data = []
            for var in historical_data_order:
                time_step_data.append(time_step.pop(var) if var in time_step else None)
            if len(time_step) > 0:
                raise ValueError('Additional variables not present in the historical data format: '+str(time_step))
            time_step_data = OpenPAYGOMetricsShared.remove_trailing_empty_elements(time_step_data)
            condensed_request['historical_data'].append(time_step_data)
        # We prepare the auth
        if self.auth_method:
            condensed_request['auth'] = OpenPAYGOMetricsShared.generate_request_signature_from_data(condensed_request, self.auth_method, self.secret_key)
        # We replace the key names by the condensed ones
        condensed_request = OpenPAYGOMetricsShared.convert_dict_keys_to_condensed(condensed_request)
        return condensed_request
