from scapy.all import *
from sys import argv

ip = argv[1]
data = argv[2]

pingr=IP(dst=ip)/ICMP()/Padding(data+"k"*10000)
print(f"Sending {data} in ICMP to {ip}")
send(pingr)