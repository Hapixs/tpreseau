from scapy.all import *


ans = sr1(
    IP(dst="8.8.8.8")/
    UDP(dport=53)/
    DNS(rd=1,qd=DNSQR(qname="ynov.com")))

print(ans)