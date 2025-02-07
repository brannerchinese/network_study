#!/usr/bin/env python
# count_redirects.py
# David Prager Branner
# 20140704, works

"""Make requests to randomly chosen sites; collect and study HTTP headers."""

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
    # From http://stackoverflow.com/a/8465202/621762
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

def main(nonrandom=None, seconds=2):
    """Choose random or semi-random IPs and store HTTP headers received."""
    if os.path.exists('IPs_tried.txt'):
        with open('IPs_tried.txt', 'r') as f:
            IPs_tried = ast.literal_eval(f.read())
    else:
        IPs_tried = set()
    if os.path.exists('responses_found.txt'):
        with open('responses_found.txt', 'r') as f:
            responses_found = ast.literal_eval(f.read())
    else:
        responses_found = {}
    IP_heads = ['50.17', '50.19', '54.231', '69.53', '72.21', '74.125', 
            '98.137', '98.139', '98.158', '128.59', '192.0', '192.30', 
            '107.170', '190.93']
    count_tried = len(IPs_tried)
    count_found = len(responses_found)
    print('Found in tried-file: {} IPs.'.format(count_tried))
    print('Found in found-file: {} IPs.'.format(count_found))
    while True:
        if (len(IPs_tried) != count_tried and
                (len(IPs_tried) - count_tried) % 250 == 0):
            print('\n{} new IPs tried since last save to disk.'.
                    format(len(IPs_tried) - count_tried))
            write_IPs_to_disk(responses_found, IPs_tried)
            count_tried = len(IPs_tried)
        # Make random IP-address.
        if nonrandom:
            head = R.choice(IP_heads)
            IP_address = 'http://' + head + ('.' +
                    str(R.randint(0, 255)) + '.' + str(R.randint(0, 255)))
        else:
            parts = [R.randint(0, 223), R.randint(0, 255), 
                    R.randint(0, 255), R.randint(0, 255)]
            IP_address = 'http://' + '.'.join([str(i) for i in parts])
            # Eliminate potentially sensitive or uninteresting IPs.
            if (21 <= parts[0] <= 57 or parts[0] in [6, 7, 10, 11, 214, 215]):
                continue
            # Eliminate private IPv4 network ranges: 
            #     192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12.
            if (parts[0:2] == [192, 168] or 
                    parts[0] == '10' or 
                    parts[0] == '172' and 16 <= parts[1] <= 31):
                continue
        if IP_address in IPs_tried:
            continue
        IPs_tried.add(IP_address)
        try:
            with Timeout(seconds):
                headers = H.get_responses(IP_address)
        except KeyboardInterrupt:
            print()
            IPs_tried.discard(IP_address)
            print('Tried {} IPs before quitting.'.format(len(IPs_tried)))
            write_IPs_to_disk(responses_found, IPs_tried)
            sys.exit('KeyboardInterrupt detected; exiting.')
        except Timeout.Timeout:
            print('.', end='')
            sys.stdout.flush()
            continue
        except Exception as e:
            print('\n    {}'.format(e))
            IPs_tried.discard(IP_address)
            continue
        if headers:
            print('\nIP #{}: {}: {} items'.
                    format(len(IPs_tried), IP_address, len(headers)))
            responses_found[IP_address] = headers
            write_IPs_to_disk(responses_found, IPs_tried)
            count_tried = len(IPs_tried)

def write_IPs_to_disk(responses_found, IPs_tried):
    with open('responses_found.txt', 'w') as f:
        f.write(str(responses_found))
        print('Wrote {} IPs-found to disk.'.format(len(responses_found)))
    with open('IPs_tried.txt', 'w') as f:
        f.write(str(IPs_tried))
        print('Wrote {} IPs-tried to disk.'.format(len(IPs_tried)))

def count():
    """Return list_reverseiterator and IPs for all HTTP headers received."""
    if not os.path.exists('responses_found.txt'):
        return
    with open('responses_found.txt', 'r') as f:
        responses_found = ast.literal_eval(f.read())
    x = reversed(sorted(
        [(len(responses_found[i]), i) for i in responses_found]))
    return x, responses_found

def list_headers():
    """Count examples of each header found."""
    if not os.path.exists('responses_found.txt'):
        return
    with open('responses_found.txt', 'r') as f:
        responses_found = ast.literal_eval(f.read())
    x = [k for i in responses_found for j in responses_found[i] for k in j]
    return C.Counter(x)

if __name__ == '__main__':
    main()