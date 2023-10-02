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
  - [Getting Started - Generating Token](#getting-started---generating-token)


## Installing the library

You can install the library by running `pip install openpaygo` or adding `openpaygo` in your requirements.txt file and running `pip install -r requirements.txt`. 

## Getting Started - Generating Token

You can use the `generate_token()` function to generate an OpenPAYGOToken Token. The function takes the following parameters, and they should match the configuration in the hardware of the device: 

- `secret_key` (required): The secret key of the device
- `value` (required): The value to be passed in the token (typically the number of days of activation)
- `count` (required): The token count used to make the last token. 
- `set_mode` (optional): If set to `true`, the generated token will be a Set Time token, otherwise it is Add Time token. 
- `starting_code` (optional): If not provided, it is generated according to the method defined in the standard (SipHash-2-4 of the key, transformed to digit by the same method as the token generation).
- `value_divider` (optional): The dividing factor used for the value. 
- `restricted_digit_set` (optional): If set to `true`, the the restricted digit set will be used (only digits from 1 to 4). 
- `extended_token` (optional): If set to `true` then a larger token will be generated, able to contain values up to 999999. This is for special use cases of each device, such as settings change, and is not set in the standard. 


The function returns the `token` as a string as well as the `updated_count` as a number. 


**Example:**

```
from openpaygo.token import generate_token
from myexampleproject import device_getter

# We get a device with the parameters we need from our database, this will be specific to your project
device = device_getter(serial=1234)

# We get the new token and update the count
new_token, device.count = generate_token(
  secret_key=device.secret_key,
  value=7,
  count=device.count
)

print('Token: '+new_token)
device.save() # We save the new count that we set for the device
```

## Getting Started - Decoding a Token