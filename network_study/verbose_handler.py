#!/usr/bin/env python
# Rhodes and Goerzen, Foundations of Python Network Programming - Chapter 9
# verbose_handler.py
# HTTP request handler for urllib that prints requests and responses.
# Converted to Python3 by David Branner, 20140703, works.

"""Report HTTP request and response.

Use in interpreter as

    import urllib
    from verbose_handler import VerboseHTTPHandler as VH
    opener = urllib.request.build_opener(VH)
    url = '' # some URL, using HTTP; not HTTPS, which requires
                        http.client.HTTPSConnection()
    opener.open(url)
"""

import io, http.client, urllib

class VerboseHTTPResponse(http.client.HTTPResponse):
    def _read_status(self):
        s = self.fp.read()
        print('-' * 20, 'Response', '-' * 20)
        print(s.decode().split('\r\n\r\n')[0])
        self.fp = io.BytesIO(s)
        return http.client.HTTPResponse._read_status(self)

class VerboseHTTPConnection(http.client.HTTPConnection):
    response_class = VerboseHTTPResponse
    def send(self, s):
        print('-' * 50)
        print(s.decode().strip())
        http.client.HTTPConnection.send(self, s)

class VerboseHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(VerboseHTTPConnection, req)