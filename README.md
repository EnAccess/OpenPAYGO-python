# OpenPAYGO - Python Lib

This repository contains the Python library for using implementing the different OpenPAYGOToken Suite technologies on your server (for generating tokens and decoding openpaygo metrics payloads) or device (for decoding tokens and making openpaygo metrics payloads).  

<p align="center">
  <img
    alt="Project Status"
    src="https://img.shields.io/badge/Project%20Status-beta-orange"
  >
  <a href="https://github.com/EnAccess/OpenPAYGO-python/blob/main/LICENSE" target="_blank">
    <img
      alt="License"
      src="https://img.shields.io/github/license/EnAccess/openpaygo-python"
    >
  </a>
</p>

## Credits

This open-source project was developped by Solaris Offgrid. Sponsorship for the original OpenPAYGO Token implementation was provided by EnAccess and sponsorphip for OpenPAYGO Metrics was provided by Solaris Offgrid. 


## Table of Contents
  - [Key Features](#key-features)
  - [Installing the library](#installing-the-library)
  - [Getting Started - OpenPAYGO Token](#getting-started---openpaygo-token)
    - [Generating Tokens (Server Side)](#generating-tokens-server-side)
    - [Decoding Tokens (Device Side)](#decoding-tokens-device-side)
  - [Getting Started - OpenPAYGO Metrics](#getting-started---openpaygo-metrics)
    - [Generating a Request (Device Side)](#generating-a-request-device-side)
    - [Handling a Request and Generating a Response (Server Side)](#handling-a-request-and-generating-a-response-server-side)
  - [Changelog](#changelog)
    - [2023-10-09 - v0.3.0](#2023-10-09---v030)
    - [2023-10-03 - v0.2.0](#2023-10-03---v020)

## Key Features
- Implements token generation and decoding with full support for the v2.3 of the [OpenPAYGO Token](https://github.com/EnAccess/OpenPAYGO-Token) specifications. 
- Implements payload authentication (verification + signing) and conversion from simple to condensed payload (and back) with full support of the v1.0-rc1 of the [OpenPAYGO Metrics](https://github.com/openpaygo/metrics) specifications. 

## Installing the library

You can install the library by running `pip install openpaygo` or adding `openpaygo` in your requirements.txt file and running `pip install -r requirements.txt`. 

## Getting Started - OpenPAYGO Token

### Generating Tokens (Server Side)

You can use the `generate_token()` function to generate an OpenPAYGOToken Token. The function takes the following parameters, and they should match the configuration in the hardware of the device: 

- `secret_key` (required): The secret key of the device. Must be passed as an hexadecimal string with 32 characters (e.g. `dac86b1a29ab82edc5fbbc41ec9530f6`). 
- `count` (required): The token count used to make the last token.
- `value` (optional): The value to be passed in the token (typically the number of days of activation). Optional if the `token_type` is Disable PAYG or Counter Sync. The value must be between 0 and 995. 
- `token_type` (optional): Used to set the type of token (default is Add Time). Token types can be found in the `TokenType` class: ADD_TIME, SET_TIME, DISABLE_PAYG, COUNTER_SYNC. 
- `starting_code` (optional): If not provided, it is generated according to the method defined in the standard (SipHash-2-4 of the key, transformed to digit by the same method as the token generation).
- `value_divider` (optional): The dividing factor used for the value. 
- `restricted_digit_set` (optional): If set to `true`, the the restricted digit set will be used (only digits from 1 to 4). 
- `extended_token` (optional): If set to `true` then a larger token will be generated, able to contain values up to 999999. This is for special use cases of each device, such as settings change, and is not set in the standard. 

The function returns the `updated_count` as a number as well as the `token` as a string, in that order. The function will raise a `ValueError` if the key is in the wrong format or the value invalid. 


**Example 1 - Add 7 days:**

```python
from openpaygo import generate_token
from myexampleproject import device_getter

# We get a device with the parameters we need from our database, this will be specific to your project
device = device_getter(serial=1234)

# We get the new token and update the count
device.count, new_token = generate_token(
  secret_key=device.secret_key,
  value=7,
  count=device.count
)

print('Token: '+new_token)
device.save() # We save the new count that we set for the device
```

**Example 2 - Disable PAYG (unlock forever):**

```python
from openpaygo import generate_token, TokenType

...

# We get the new token and update the count
device.count, new_token = generate_token(
  secret_key=device.secret_key,
  token_type=TokenType.DISABLE_PAYG,
  count=device.count
)

print('Token: '+new_token)
device.save() # We save the new count that we set for the device
```


### Decoding Tokens (Device Side)

You can use the `decode_token()` function to generate an OpenPAYGOToken Token. The function takes the following parameters, and they should match the configuration in the hardware of the device: 

- `token` (required): The token that was given by the user, as a string
- `secret_key` (required): The secret key of the device as a string with 32 hexadecimal characters (e.g. `dac86b1a29ab82edc5fbbc41ec9530f6`)
- `count` (required): The token count of the last valid token. When a device is new, this is 1. 
- `used_counts` (optional): An array of recently used token counts, as returned by the function itself after the last valid token was decoded. This allows for handling unordered token entry. 
- `starting_code` (optional): If not provided, it is generated according to the method defined in the standard (SipHash-2-4 of the key, transformed to digit by the same method as the token generation).
- `value_divider` (optional): The dividing factor used for the value. 
- `restricted_digit_set` (optional): If set to `true`, the the restricted digit set will be used (only digits from 1 to 4). 


The function returns the following variable in this order: 
- `value`: The value associated with the token (if the token is ADD_TIME or SET_TIME). 
- `token_type`: The type of the token that was provided. Token types can be found in the `TokenType` class: ADD_TIME, SET_TIME, DISABLE_PAYG, COUNTER_SYNC or ALREADY_USED (if the token is valid but already used), INVALID (if the token was invalid). 
- `updated_count`: The token count of the token, if it was valid. 
- `updated_used_counts`: The updated array of recently used token, if the token was valid. 

The function will raise a `ValueError` if the key is in the wrong format, but will not raise an error if the token is invalid (as it is a common expected behaviour), to check the validity of the token you must check the return `token_type` and proceed accordingly depending on the type of token. 


**Example:**

```python
from openpaygo import decode_token

# We assume the users enters a token and that the device state is saved in my_device_state
...

# We decode the token
value, token_type, updated_count, updated_used_counts = decode_token(
  token=token_input,
  secret_key=my_device_state.secret_key,
  count=my_device_state.count,
  used_counts=my_device_state.used_counts
)

# If the token is valid, we update our count in the device state
if token_type not in [TokenType.ALREADY_USED, TokenType.INVALID]:
  my_device_state.count = updated_count
  my_device_state.used_counts = updated_used_counts

# We perform the appropriate behaviour based on the token data
if token_type == TokenType.ADD_TIME:
  my_device_state.days_remaining += value
  print(f'Added {value} days remaining')
elif token_type == TokenType.SET_TIME:
  my_device_state.days_remaining = value
  print(f'Set to {value} days remaining')
elif token_type == TokenType.DISABLE_PAYG:
  print('Unlocked Device')
  my_device_state.unlocked_forever = True
elif token_type == TokenType.COUNTER_SYNC:
  print('Counter Synced')
elif token_type == TokenType.ALREADY_USED:
  print('Token was already used')
elif token_type == TokenType.INVALID:
  print('Token is invalid')
```


## Getting Started - OpenPAYGO Metrics

### Generating a Request (Device Side)

You can use the `MetricsRequestHandler` object to create a new OpenPAYGO Metrics request from start to finish. It accepts the following initial inputs: 
- `serial_number` (required): The serial number of the device
- `data_format` (optional): The data format, provided as dictionnary matching the data format object specifications. 
- `secret_key` (optional): The secret key provided as a string containing 32 hexadecimal characters (e.g. `dac86b1a29ab82edc5fbbc41ec9530f6`). Required if `auth_method` is defined. 
- `auth_method` (optional): One of the auth method contained in the `AuthMethod` class. 

It provides the following methods:
- `set_timestamp(timestamp)`: Used to set the `timestamp` of the request. 
- `set_request_count(request_count)`: Used to set the `request_count` of the request. 
- `set_data(data)`: Used to set the `data` of the request, should be set in simple format as a dictionnay. 
- `set_historical_data(data)`: Used to set the `historical_data` of the request, should be set in simple format as a dictionnary. The data is assumed to be separated by the `historical_data_interval` unless an explicit timestamp is provided. 
- `get_simple_request_payload()`: Returns the payload in simple format as a string containing JSON and including the authentication signature. 
- `get_condensed_request_payload()`: Returns the payload in condensed format as a string containing JSON and including the authentication signature. It requires `data_format` to be set. The data is automatically condensed from the set data and the data format and the signature is automatically generated. 


**Example - Full Request flow from device side:**

```python
from openpaygo import MetricsRequestHandler, AuthMethod
import requests

# We assume the users enters a token and that the device state is saved in my_device_state
...

metrics_request = MetricsRequestHandler(
      serial_number=my_device_state.serial_number,
      secret_key=my_device_state.secret_key,
      data_format=my_device_state.data_format,
      auth_method=AuthMethod.RECURSIVE_DATA_AUTH
)

metrics_request.set_timestamp(1611583070)
metrics_request.set_data({
  "token_count": 3,
  "tampered": False,
  "firmware_version": "1.2.3"
})
# Here we assume that the data we send is separated by 60 seconds as per the data format
metrics_request.set_historical_data([
  {
      "panel_voltage": 12.31,
      "battery_voltage": 12.32,
      "panel_current": 1.23,
      "battery_current": -1.23,
  },
  {
      "panel_voltage": 12.30,
      "battery_voltage": 12.31,
      "panel_current": 1.22,
      "battery_current": -1.21,
  }
])
payload = metrics_request.get_condensed_request_payload()

# We can now proceed to send the payload to the URL
# It looks something like `{"sn":"aaa111222","df":1234,"ts":1611583070,"d":[3,false,"1.2.3"],"hd":[[12.31,12.32,1.23,-1.23],[12.3,12.31,1.22,-1.21]],"a":"raa5cb1fda302cf94e"}`
response = requests.post('https://<base_url>/dd', data=payload, headers={'Content-Type':'application/json'})
try:
  response.json().get('tkl', [])
  for tokens in tkl:
    # Here we decode the tokens received from the server and apply them (see example above)
    ...
```


### Handling a Request and Generating a Response (Server Side)

You can use the `MetricsResponseHandler` object to process your OpenPAYGO Metrics request from start to finish. It accepts the following initial inputs: 
- `metrics_payload` (required): The OpenPAYGO Metrics payload, as a string containing the JSON payload. 
- `secret_key` (optional): The secret key provided as a string containing 32 hexadecimal characters (e.g. `dac86b1a29ab82edc5fbbc41ec9530f6`)
- `data_format` (optional): The data format, provided as dictionnary matching the data format object specifications. 
- `last_request_count` (optional): The request count of the last valid request (used for avoiding request replay)
- `last_request_timestamp` (optional): The timestamp of the last valid request (used for avoiding request replay)

It provides the following methods:
- `get_device_serial()`: Returns the serial number of the device as a string. 
- `set_device_parameters(secret_key, data_format, last_request_count, last_request_timestamp)`: Used to set the device data required for proper processing of the request in the handler if it was not set initially, which is often the case as the serial number is usually required to fetch that data. It will return `ValueError` if either of the parameters is invalid. 
- `is_auth_valid()`: Returns `true` if the authentication provided is valid or `false` if not. Note that it checks both that the signature is valid and that the `request_count` or `timestamp` are more recent than the one provided in the device parameters. 
- `get_simple_metrics()`: Returns the metrics provided in the simple expanded format. It will also convert relative timestamps into explicit timestamps for easier processing. 
- `get_data_timestamp()`: Returns the timestamp of the data, either the `data_collection_timestamp` if available or the timestamp `timestamp` or the time of the request as fallback. 
- `get_token_count()`: Returns the token count provided in the request (if any). 
- `expects_token_answer()`: Return `true` if the payload requested tokens in the answer. You can set the tokens to be returned by calling `add_tokens_to_answer(token_list)` with `token_list` being a list of token strings. 
- `expects_time_answer()`: Return `true` if the payload requested either relative time or absolute time in the answer. You can set the time to be returned by calling `add_time_to_answer(target_datetime)` with `target_datetime` being a datetime object. The function will automatically provide it in the correct format based on the request.  
- `add_settings_to_answer(settings_dict)`: Will add the provided settings dictionnary to the answer. 
- `add_extra_data_to_answer(extra_data_dict)`: Will add the provided extra data dictionnary to the answer. 
- `add_new_base_url_to_answer(new_base_url)`: Will tell the device to change the base URL to send the data to. 
- `get_answer_payload()`: Will return the answer as a string based on the request and the data added to answer, it will automatically handle the authentication and fomatting. 


**Example - Full Request flow from server side:**

```python
from openpaygo import MetricsResponseHandler
from my_db_service import get_device, get_data_format, store_metric, get_pending_tokens


@app.route('/dd')
def device_data():
  # We load the metrics
  try:
    metrics = MetricsResponseHandler(request.data)
  except ValueError as e:
    return {'error': 'Invalid data format'}, 400
  # We get the serial number and load the device data from our storage
  device = get_device(serial=metrics.get_device_serial())
  # We get the data format if needed from our storage
  data_format = get_data_format(id=metrics.get_data_format_id()) if metrics.get_data_format_id() else None
  # We set the device parameters in the metrics handler
  metrics.set_device_parameters(
    secret_key=device.secret_key,
    data_format=data_format,
    last_request_timestamp=device.last_request_timestamp
  )
  # We check the authentication
  if not metrics.is_auth_valid():
    return {'error': 'Invalid authentication'}, 403
  # We transform the condensed data received from the device in simple data
  simple_data = metrics.get_simple_metrics()
  # We store the metrics in our database
  for metric_name, metric_value in simple_data.get('data'):
    store_metric(name=metric_name, value=metric_value, time=metrics.get_data_timestamp())
  # We store the historical metrics as well
  for time_step in simple_data.get('historical_data'):
    # Here the handler automatically computed the timestamp for each step
    timestamp = timestep.pop('timestamp')
    for metric_name, metric_value in time_step:
      store_metric(name=metric_name, value=metric_value, time=timestamp)
  # We prepare the answer
  if metrics.expects_token_answer():
    metrics.add_tokens_to_answer(get_pending_tokens(device, metrics.get_token_count()))
  elif metrics.expects_time_answer():
    metrics.add_time_to_answer(device.expiration_datetime)
  # We can add extra data
  metrics.add_settings_to_answer({'language': 'fr-FR'})
  # The handler handles the signature, etc.
  return metrics.get_answer_payload(), 200
```


## Changelog

### 2023-10-12 - v0.4.0
- Added convenience functions for accessing token count and data timestamp
- Added automatic verification of last request count or timestamp during auth
- Fixed issues in documentation

### 2023-10-09 - v0.3.0
- Fix token generation issue
- Add support for OpenPAYGO Metrics Request Generation
- Add support for OpenPAYGO Metrics Request Decoding
- Add support for OpenPAYGO Metrics Response Generation

### 2023-10-03 - v0.2.0
- First working version published on PyPI
- Has support for OpenPAYGO Token
- Has working CI for pushing to PyPI
