## Network Study

Tools for play with HTTP requests and responses.

 1. Programs
   2. `http_responses.py`: report headers from all HTTP responses, including interim responses before `HTTP/1.1 200 OK` is returned. Call as `http_responses.get_responses(url)`. Returns a list of dictionaries, each dictionary containing key-value pairs that embrace one header.
   2. `count_redirects.py`: generate random URLs (with some sensitive ranges omitted) and call `http_responses.py` to collect their HTTP responses. Calling as `count_redirects.py.main(nonrandom=None)` generates random URLs; if argument `nonrandom` is set to `True`, then a series of "IP_heads" — the first two bytes of four-byte IP-addresses (e.g., '98.139') are used, and the last two bytes are supplied randomly. The headers received are stored as a dictionary in `IPs_found.txt`; the list of IP addresses tried — most of which, in practice, time out, are saved to `IPs_tried.txt`.

     This program also supplies a function `list_headers()` that counts the number of examples of each header saved to `IPs_found.txt` and reports them in order from most- to least-common.

[end]
