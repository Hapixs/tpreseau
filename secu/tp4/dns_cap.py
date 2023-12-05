from scapy.all import *


def print_it_please(packet):
    print("Requette DNS")
    print('- Source: '+packet['IP'].src)
    print('- Destination: '+packet['IP'].dst)
    print('- Summary: '+packet['DNS'].summary())

sniff(filter="udp and port 53", prn=print_it_please, count=2)