import json
from .metrics_shared import OpenPAYGOMetricsShared
import copy
from datetime import datetime, timedelta

class MetricsResponseHandler(object):

    def __init__(self, received_metrics, data_format=None, secret_key=None, last_request_count=None, last_request_timestamp=None):
        self.received_metrics = received_metrics
        self.request_dict = json.loads(received_metrics)
        # We convert the base variable names to simple
        self.request_dict = OpenPAYGOMetricsShared.convert_dict_keys_to_simple(self.request_dict)
        # We add the reception timestamp if not timestamp was provided
        if not self.request_dict.get('timestamp'):
            self.timestamp = int(datetime.now().timestamp())
        else:
            self.timestamp = self.request_dict.get('timestamp')
        self.response_dict = {}
        self.secret_key = secret_key
        self.data_format = data_format
        self.last_request_count = last_request_count
        self.last_request_timestamp = last_request_timestamp
        if not self.data_format and self.request_dict.get('data_format'):
            self.data_format = self.request_dict.get('data_format')

    def get_device_serial(self):
        return self.request_dict.get('serial_number')
    
    def get_data_format_id(self):
        return self.request_dict.get('data_format_id')
    
    def data_format_available(self):
        return self.data_format != None
    
    def set_device_parameters(self, secret_key=None, data_format=None, last_request_count=None, last_request_timestamp=None):
        if secret_key:
            self.secret_key = secret_key
        if data_format:
            self.data_format = data_format
        if last_request_count:
            self.last_request_count = last_request_count
        if last_request_timestamp:
            self.last_request_timestamp = last_request_timestamp

    def is_auth_valid(self):
        auth_string = self.request_dict.get('auth', None)
        if not auth_string:
            return True
        elif not self.secret_key:
            raise ValueError('Secret key is required to check the auth.')
        self.auth_method = auth_string[:2]
        new_signature = OpenPAYGOMetricsShared.generate_request_signature_from_data(self.request_dict, self.auth_method, self.secret_key)
        if auth_string == new_signature:
            request_count = self.request_dict.get('request_count')
            if request_count and self.last_request_count and request_count <= self.last_request_count:
                return False
            timestamp = self.request_dict.get('timestamp')
            if timestamp and self.last_request_timestamp and timestamp <= self.last_request_timestamp:
                return False
            return True
        return False

    def get_simple_metrics(self):
        # We start the process by making a copy of the dict to work with
        simple_dict = copy.deepcopy(self.request_dict)
        simple_dict.pop('auth') if 'auth' in simple_dict else None # We remove the auth
        # We process the data and replace it
        simple_dict['data'] = self._get_simple_data()
        # We process the historical data
        simple_dict['historical_data'] = self._get_simple_historical_data()
        # We fill in the timestamps for each time step
        simple_dict['historical_data'] = self._fill_timestamp_in_historical_data(simple_dict['historical_data'])
        return simple_dict
    
    def get_data_timestamp(self):
        return self.request_dict.get('data_collection_timestamp', self.request_dict.get('timestamp'))
    
    def get_token_count(self):
        data = self._get_simple_data()
        return data.get('token_count')
    
    def expects_token_answer(self):
        return self.get_token_count() is not None

    def add_tokens_to_answer(self, token_list):
        self.response_dict['token_list'] = token_list

    def expects_time_answer(self):
        data = self._get_simple_data()
        if data.get('active_until_timestamp_requested', False) or data.get('active_seconds_left_requested', False):
            return True
        return False

    def add_time_to_answer(self, target_datetime):
        data = self._get_simple_data()
        if data.get('active_until_timestamp_requested', False):
            self.response_dict['active_until_timestamp'] = target_datetime.timestamp()
        elif data.get('active_seconds_left_requested', False):
            self.response_dict['active_seconds_left'] = (datetime.now() - target_datetime).total_seconds()
        else:
            raise ValueError('No time requested')
        
    def add_new_base_url_to_answer(self, new_base_url):
        self.add_settings_to_answer({'base_url': new_base_url})

    def add_settings_to_answer(self, settings_dict):
        if not self.response_dict.get('settings'):
            self.response_dict['settings'] = {}
        self.response_dict['settings'].update(settings_dict)

    def add_extra_data_to_answer(self, extra_data_dict):
        if not self.response_dict.get('extra_data'):
            self.response_dict['extra_data'] = {}
        self.response_dict['extra_data'].update(extra_data_dict)

    def get_answer_payload(self):
        payload = self.get_answer_dict()
        return OpenPAYGOMetricsShared.convert_to_metrics_json(payload)

    def get_answer_dict(self):
        # If there is not data format, we just return the full response
        condensed_answer = copy.deepcopy(self.response_dict)
        condensed_answer['auth'] = OpenPAYGOMetricsShared.generate_response_signature_from_data(
            serial_number=self.request_dict.get('serial_number'),
            request_count=self.request_dict.get('request_count'),
            data=condensed_answer,
            timestamp=self.request_dict.get('timestamp'),
            secret_key=self.secret_key
        )
        return OpenPAYGOMetricsShared.convert_dict_keys_to_condensed(condensed_answer)

    def _get_simple_data(self):
        data = copy.deepcopy(self.request_dict.get('data'))
        # If no data or not condensed in list, we just return it
        if not data:
            return {}
        if not isinstance(data, list):
            return data
        data_order = self.data_format.get('data_order')
        if not data_order:
            raise ValueError('Data Format does not contain data_order')
        clean_data = {}
        data_len = len(data)
        for idx, var in enumerate(data_order):
            clean_data[var] = data[idx] if idx < data_len else None
        data = data[data_len:]
        if len(data) > 0:
            raise ValueError('Additional variables not present in the data format: '+str(data))
        return OpenPAYGOMetricsShared.convert_dict_keys_to_simple(clean_data)
    
    def _get_simple_historical_data(self):
        historical_data = copy.deepcopy(self.request_dict.get('historical_data'))
        if not historical_data:
            return []
        historical_data_order = self.data_format.get('historical_data_order')
        clean_historical_data = []
        for time_step in historical_data:
            time_step_data = {}
            if isinstance(time_step, list):
                if not historical_data_order:
                    raise ValueError('Data Format does not contain historical_data_order')
                timse_step_len = len(time_step)
                for idx, var in enumerate(historical_data_order):
                    if idx < timse_step_len:
                        time_step_data[var] = time_step[idx]
                time_step = time_step[timse_step_len:]
                if len(time_step) > 0:
                    raise ValueError('Additional variables not present in the historical data format: '+str(time_step))
            elif isinstance(time_step, dict):
                for key in time_step:
                    if key.isdigit() and int(key) < len(historical_data_order):
                        time_step_data[historical_data_order[int(key)]] = time_step[key]
                    else:
                        time_step_data[key] = time_step[key]
            else:
                raise ValueError('Invalid historical data step type: '+str(time_step))
            clean_historical_data.append(time_step_data)
        return clean_historical_data
    
    def _fill_timestamp_in_historical_data(self, historical_data):
        last_timestamp = datetime.fromtimestamp(self.get_data_timestamp())
        for idx, time_step in enumerate(historical_data):
            if time_step.get('relative_time') is not None:
                last_timestamp = last_timestamp + timedelta(seconds=int(time_step.get('relative_time')))
                historical_data[idx]['timestamp'] = int(last_timestamp.timestamp())
                del historical_data[idx]['relative_time']
            elif time_step.get('timestamp'):
                last_timestamp = datetime.fromtimestamp(time_step.get('timestamp'))
            else:
                if idx != 0:
                    last_timestamp = last_timestamp + timedelta(seconds=int(self.data_format.get('historical_data_interval')))
                historical_data[idx]['timestamp'] = int(last_timestamp.timestamp())
        return historical_data
