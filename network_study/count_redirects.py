#!/usr/bin/env python
# count_redirects.py
# David Prager Branner
# 20140704, works

import sys
import os
import ast
import signal
import time
import random as R
import collections as C
import http_responses as H

class Timeout():
    """Timeout class using SIGALRM signal."""
    class Timeout(Exception):
        pass
 
    def __init__(self, seconds):
        self.seconds = seconds
 
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.seconds)
 
    def __exit__(self, *args):
        signal.alarm(0)
 
    def raise_timeout(self, *args):
        raise Timeout.Timeout()

def main(random=None):
    """Choose random or semi-random domains and store HTTP headers received."""
    if os.path.exists('domains_tried.txt'):
        with open('domains_tried.txt', 'r') as f:
            domains_tried = ast.literal_eval(f.read())
    else:
        domains_tried = set()
    print('Using as domains_tried:\n    {}\n'.format(domains_tried))
    if os.path.exists('domains_found.txt'):
        with open('domains_found.txt', 'r') as f:
            domains_found = ast.literal_eval(f.read())
    else:
        domains_found = {}
    print('Using as domains_found:\n    {}\n'.format(domains_found))
    URL_heads = ['50.17', '50.19', '54.231', '69.53', '72.21', '74.125', 
            '98.137', '98.139', '98.158', '128.59', '192.0', '192.30', 
            '107.170', '190.93']
    while True:
        # Make random URL.
        if random:
            head = R.choice(URL_heads)
            url = 'http://' + head + ('.' +
                    str(R.randint(0, 255)) + '.' + str(R.randint(0, 255)))
        else:
            parts = [R.randint(0, 223), R.randint(0, 255), 
                    R.randint(0, 255), R.randint(0, 255)]
            url = 'http://' + '.'.join([str(i) for i in parts])
            # Eliminate private IPv4 network ranges 192.168, 10, 172.16-31.
            if (parts[0:2] == [192, 168] or 
                    parts[0] == '10' or 
                    parts[0] == '172' and 16 <= parts[1] <= 31):
                continue
            # Eliminate potentially sensitive or uninteresting domains.
            if ((parts[0] in [6, 7, 10, 11, 214, 215] or
                    21 <= parts[0] <= 57) and
                    (parts[1] == 0 and parts[2] == 0 and 0 <= parts[3] <= 8)):
                continue
        if url in domains_tried:
            continue
        domains_tried.add(url)
        try:
            with Timeout(2):
                headers = H.get_responses(url)
        except KeyboardInterrupt:
            print()
            print('Tried {} URLs before quitting.'.format(len(domains_tried)))
            with open('domains_tried.txt', 'w') as f:
                f.write(str(domains_tried))
            sys.exit('KeyboardInterrupt detected; exiting.')
        except Timeout.Timeout:
            print('.', end='')
            sys.stdout.flush()
            continue
        except Exception as e:
            print('\n    {}'.format(e))
            continue
        if headers:
            print('\nURL #{}: {}: {} items'.
                    format(len(domains_tried), url, len(headers)))
            domains_found[url] = headers
    with open('domains_found.txt', 'w') as f:
        f.write(str(domains_found))

def count():
    """Return list_reverseiterator and domains for all HTTP headers received."""
    if not os.path.exists('domains_found.txt'):
        return
    with open('domains_found.txt', 'r') as f:
        domains_found = ast.literal_eval(f.read())
    x = reversed(sorted(
        [(len(domains_found[i]), i) for i in domains_found]))
    return x, domains_found

def list_headers():
    """Count examples of each header found."""
    if not os.path.exists('domains_found.txt'):
        return
    with open('domains_found.txt', 'r') as f:
        domains_found = ast.literal_eval(f.read())
    x = [k for i in domains_found for j in domains_found[i] for k in j]
    return C.Counter(x)

if __name__ == '__main__':
    main()