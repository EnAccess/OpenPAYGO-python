import siphash
import codecs
import json


class AuthMethod(object):
    SIMPLE_AUTH = 'sa'
    TIMESTAMP_AUTH = 'ta'
    COUNTER_AUTH = 'ca'
    DATA_AUTH = 'da'
    RECURSIVE_DATA_AUTH = 'ra'


class OpenPAYGOMetricsShared(object):

    CONDENSED_KEY_NAMES = {
        'serial_number': 'sn',
        'timestamp': 'ts',
        'auth': 'a',
        'request_count': 'rc',
        'data_collection_timestamp': 'dtc',
        'data_format_id': 'df',
        'data_format': 'dfo',
        'data': 'd',
        'historical_data': 'hd',
        'accessories': 'acc'
    }

    @classmethod
    def convert_dict_keys_to_condensed(cls, simple_dict):
        condensed_dict = {}
        for key in simple_dict:
            if key in cls.CONDENSED_KEY_NAMES:
                condensed_dict[cls.CONDENSED_KEY_NAMES[key]] = simple_dict[key]
            else:
                condensed_dict[key] = simple_dict[key]
        return condensed_dict
    
    @classmethod
    def remove_trailing_empty_elements(cls, list_with_empty):
        while list_with_empty and list_with_empty[-1] is None:
            list_with_empty.pop()
        return list_with_empty

    @classmethod
    def convert_to_metrics_json(cls, data):
        return json.dumps(data, separators=(',', ':'))
    
    @classmethod
    def generate_request_signature_from_data(cls, data, auth_method, secret_key):
        if auth_method == AuthMethod.SIMPLE_AUTH:
            signature = cls.generate_hash_string(data.get('serial_number'), secret_key)
        elif auth_method == AuthMethod.TIMESTAMP_AUTH:
            if not data.get('timestamp', None):
                raise ValueError('Timestamp is required for Timestamp Auth')
            signature = cls.generate_hash_string(data.get('serial_number') + str(data.get('timestamp')), secret_key)
        elif auth_method == AuthMethod.COUNTER_AUTH:
            if not data.get('request_count', None):
                raise ValueError('Request Count is required for Counter Auth')
            signature = cls.generate_hash_string(data.get('serial_number') + str(data.get('request_count')), secret_key)
        elif auth_method == AuthMethod.DATA_AUTH:
            payload = data.get('serial_number')
            if data.get('timestamp'):
                payload += str(data.get('timestamp'))
            elif data.get('request_count'):
                payload += str(data.get('request_count'))
            payload += cls.convert_to_metrics_json(data.get('data', []))
            payload += cls.convert_to_metrics_json(data.get('historical_data', []))
            signature = cls.generate_hash_string(payload, secret_key)
        elif auth_method == AuthMethod.RECURSIVE_DATA_AUTH:
            payload = data.get('serial_number')
            payload = cls.generate_hash_string(payload, secret_key)
            if data.get('timestamp'):
                payload = cls.generate_hash_string(payload+str(data.get('timestamp')), secret_key)
            elif data.get('request_count'):
                payload = cls.generate_hash_string(payload+str(data.get('request_count')), secret_key)
            payload = cls.generate_hash_string(payload+cls.convert_to_metrics_json(data.get('data', [])), secret_key)
            for time_step_data in data.get('historical_data', []):
                payload = cls.generate_hash_string(payload+cls.convert_to_metrics_json(time_step_data), secret_key)
            signature = payload
        else:
            raise ValueError('Invalid Authentication Method')
        return auth_method+signature


    @classmethod
    def generate_hash_string(cls, input_string, secret_key):
        key = cls.load_secret_key_from_hex(secret_key)
        hash = siphash.SipHash_2_4(key, codecs.encode(input_string, 'utf-8')).hash()
        hash_string = '{:x}'.format(hash)
        return hash_string

    @classmethod
    def load_secret_key_from_hex(cls, secret_key):
        try:
            return codecs.decode(secret_key, 'hex')
        except Exception as e:
            raise ValueError('The secret key provided is not correctly formatted, it should be 32 hexadecimal characters. ')