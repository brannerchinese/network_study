#!/usr/bin/env python
# http_responses.py
# David Prager Branner
# 20140704, works.

"""Report headers from all HTTP responses, including interim."""

import io
import http.client
import urllib

class Reporter():
    def __init__(self):
        self.headers = []

reporter = Reporter()

class NewHTTPResponse(http.client.HTTPResponse):
    def _read_status(self):
        s = self.fp.read()
        self.fp = io.BytesIO(s)
        headers = s.decode().split('\r\n\r\n')[0].split('\r\n')
        headers = [i.split(':') for i in headers]
        reporter.headers.append(
                {i[0]: i[1] 
                    if len(i) > 1
                    else '' for i in headers})
        return http.client.HTTPResponse._read_status(self)

class NewHTTPConnection(http.client.HTTPConnection):
    response_class = NewHTTPResponse

class NewHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(NewHTTPConnection, req)

def get_responses(url=None):
    if not url:
        return
    opener = urllib.request.build_opener(NewHTTPHandler)
    try:
        x = opener.open(url)
    except urllib.error.URLError:
        return
    return reporter.headers
