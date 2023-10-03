# OpenPAYGOToken - Python Lib

This repository contains the Python library for using implementing the different OpenPAYGOToken Suite technologies on your server (for generating tokens and decoding openpaygo metrics payloads) or device (for decoding tokens and making openpaygo metrics payloads).  

<p align="center">
  <img
    alt="Project Status"
    src="https://img.shields.io/badge/Project%20Status-beta-orange"
  >
  <a href="https://github.com/openpaygo/metrics/blob/main/LICENSE" target="_blank">
    <img
      alt="License"
      src="https://img.shields.io/github/license/openpaygo/openpaygo-python"
    >
  </a>
</p>

This open-source project was sponsored by: 
- Solaris Offgrid
- EnAccess

## Table of Contents

  - [Installing the library](#installing-the-library)
  - [Getting Started - Generating Tokens](#getting-started---generating-tokens)
  - [Getting Started - Decoding a Token](#getting-started---decoding-a-token)


## Installing the library

You can install the library by running `pip install openpaygo` or adding `openpaygo` in your requirements.txt file and running `pip install -r requirements.txt`. 

## Getting Started - Generating Tokens

You can use the `generate_token()` function to generate an OpenPAYGOToken Token. The function takes the following parameters, and they should match the configuration in the hardware of the device: 

- `secret_key` (required): The secret key of the device. Must be passed as an hexadecimal string (with 32 characters). 
- `count` (required): The token count used to make the last token.
- `value` (optional): The value to be passed in the token (typically the number of days of activation). Optional if the `token_type` is Disable PAYG or Counter Sync. The value must be between 0 and 995. 
- `token_type` (optional): Used to set the type of token (default is Add Time). Token types can be found in the `TokenType` class: ADD_TIME, SET_TIME, DISABLE_PAYG, COUNTER_SYNC. 
- `starting_code` (optional): If not provided, it is generated according to the method defined in the standard (SipHash-2-4 of the key, transformed to digit by the same method as the token generation).
- `value_divider` (optional): The dividing factor used for the value. 
- `restricted_digit_set` (optional): If set to `true`, the the restricted digit set will be used (only digits from 1 to 4). 
- `extended_token` (optional): If set to `true` then a larger token will be generated, able to contain values up to 999999. This is for special use cases of each device, such as settings change, and is not set in the standard. 

The function returns the `updated_count` as a number as well as the `token` as a string, in that order. The function will raise a `ValueError` if the key is in the wrong format or the value invalid. 


**Example 1 - Add 7 days:**

```
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

```
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


## Getting Started - Decoding a Token

You can use the `decode_token()` function to generate an OpenPAYGOToken Token. The function takes the following parameters, and they should match the configuration in the hardware of the device: 

- `token` (required): The token that was given by the user
- `secret_key` (required): The secret key of the device
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

```
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
  my_device_state.unlocked_forever = True
elif token_type == TokenType.COUNTER_SYNC:
  print('Counter Synced')
elif token_type == TokenType.ALREADY_USED:
  print('Token was already used')
elif token_type == TokenType.INVALID:
  print('Token is invalid')
```


## Changelog

### 2023-10-03 - v0.1.7
- First working version published on PyPI
- Setup CI for pushing to PyPI