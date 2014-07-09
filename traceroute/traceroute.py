#!/usr/bin/python
# traceroute.py
# Adapted for Python3 from Leonid Grinberg's version by David Prager Branner.
# See https://github.com/leonidg/Poor-Man-s-traceroute
# 20140709, works.

import socket
import sys
import time
import signal

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

def main(dest_name, port, max_hops, max_time):
    dest_addr = socket.gethostbyname(dest_name)
    hops = trace(dest_addr, port, max_hops, max_time)
    for i, hop in enumerate(hops):
        print('{}\t{}\t{}\t{}'.format(i, hop[0], hop[1], hop[2]))

def create_sockets(ttl):
    ''"Set up receiving and sending sockets.''"
    recv_socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
    send_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname('udp'))
    send_socket.setsockopt(
            socket.SOL_IP, socket.IP_TTL, ttl)
    return recv_socket, send_socket

def trace(dest_addr, port, max_hops, max_time):
    """Return list of hops, each a 3-tuple (name, address, ms elapsed)."""
    hops = []
    IPs = set()
    ttl = 1
    start_time = time.time()
    while True:
        recv_socket, send_socket = create_sockets(ttl)
        recv_socket.bind(('', port))
        send_socket.sendto('', (dest_addr, port)) # orig. dest_name
        curr_addr = None
        curr_name = None
        try:
            with Timeout(max_time/1000):
                _, curr_addr = recv_socket.recvfrom(512) # discard data
                curr_addr = curr_addr[0] # address is given as tuple
                try:
                    curr_name = socket.gethostbyaddr(curr_addr)[0]
                except socket.error:
                    curr_name = curr_addr
        except socket.error:
            pass
        except Timeout.Timeout:
            duration = round((time.time() - start_time) * 1000, 2)
            hops.append(('timeout', 'timeout', duration))
            break
        finally:
            send_socket.close()
            recv_socket.close()
        duration = round((time.time() - start_time) * 1000, 2)
        # Prevent cycles
        if curr_addr in IPs:
            break
        else:
            IPs.add(curr_addr)
        # Account for null results.
        if curr_addr is not None:
            hops.append((curr_name, curr_addr, duration))
        else:
            hops.append(('*', '*', duration))
        ttl += 1
        if curr_addr == dest_addr or ttl > max_hops:
            break
    return hops

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: traceroute.py host\n')
    else:
        sys.exit(main(dest_name=sys.argv[1],
                port=33434,
                max_hops=64,
                max_time=30000))