#!/usr/bin/env python
# count_redirects.py
# David Prager Branner
# 20140704

import http_responses as R
import time
import sys

while True:
    # make url
    url = 'http://www.example.com'
    try:
        # try url
        x = 1
    except KeyboardInterrupt:
        print()
        sys.exit('KeyboardInterrupt detected; exiting.')
#x = opener.open(url)