import json


class MetricsResponseHandler(object):

    def __init__(self, received_metrics, data_format=None, secret_key=None):
        self.received_metrics = received_metrics
        self.metrics_dict = json.loads(received_metrics)
        self.answer_dict = {}

    def get_device_serial(self):
        return self.received_metrics.get('sn', self.received_metrics.get('serial_number'))
    
    def set_device_parameters(self, secret_key, data_format):
        pass

    def is_auth_valid(self):
        pass

    def get_simple_metrics(self):
        pass

    def expects_token_answer(self):
        pass

    def add_tokens_to_answer(self, token_list):
        pass

    def expects_time_answer(self):
        pass

    def add_time_to_answer(self, target_datetime):
        pass

    def add_settings_to_answer(self, settings_dict):
        pass

    def add_extra_data_to_answer(self, extra_data_dict):
        pass

    def get_answer(self):
        pass

    def _check_data_auth(self):
        data = self.metrics_dict.get('data', None)
        data_string = json.dumps(data, separators=(',', ':')) if data else ''
        historical_data = self.metrics_dict.get('historical_data', None)
        historical_data_string = json.dumps(historical_data, separators=(',', ':')) if historical_data else ''

