from scapy.all import *
import sys

def print_it_please(packet):
    if (packet["Padding"] != None):
        print("Sniffed ping with data:")
        print(f" - From: {packet['IP'].src}")
        print(f" - To: {packet['IP'].dst}")
        print(f" - Data: {packet['Padding'].load.decode()}")
        print("...Exiting now ")
        sys.exit()

sniff(filter="icmp", prn=print_it_please)