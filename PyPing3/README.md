# Python3 ICMP Ping (Core Libs)

Pings host or ip address. Returns: 'host', 'ip', 'size', 'ttl', 'sent', 'recieved', 'lost', 'min_ms', 'max_ms', 'average_ms'

```
>>> p = PyPing3( ping_count=4, timeout=4, verbose=True, cached_stdout=False )
>>> res = p.ping('google.com')
```

```
Pinging google.com [172.217.18.14] with 25 bytes of data:
1: Reply from google.com, bytes=25 ttl=57 time=94ms
2: Reply from google.com, bytes=25 ttl=57 time=92ms
3: Reply from google.com, bytes=25 ttl=57 time=94ms
Packets: Sent=3, Received=3, Lost=0 (0.0% loss)
Timing: Min=92ms, Max=94ms, Average=93ms
```

```
>>> print( res )

{'min_ms': 94, 'ip': '172.217.18.14', 'host': 'google.com', 'size': 25, 'recieved': 3, 'average_ms': 93, 'sent': 3, 'lost': 0, 'ttl': 57, 'max_ms': 94}
```
