#!/usr/bin/python3
# -*- coding:utf-8 -*-

import math
import numpy as np
import time
import hmac
import base64
from hashlib import sha256


def HMAC_SHA256(secretKey: str, data: str):
    return hmac.new(secretKey.encode('utf-8'), data.encode('utf-8'), digestmod=sha256).hexdigest().lower()


def CurrentTimeMillis():
    return int(round(time.time() * 1000))
