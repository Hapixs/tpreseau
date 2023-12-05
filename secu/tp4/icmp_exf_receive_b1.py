from scapy.all import *
import sys
import zlib


class Data:
    mydata = bytes()

def print_it_please(packet):
    if (packet["Padding"] != None):
        load = packet['Padding'].load
        if(load == bytes("hxcEnded","UTF8")):
            print("\n"*2)
            print("Ended transaction.")
            print("Final data: ")
            print(zlib.decompress(Data.mydata).decode())
            sys.exit()
        Data.mydata+=load
        print("Sniffed ping with data:")
        print(f" - From: {packet['IP'].src}")
        print(f" - To: {packet['IP'].dst}")
        print(f" - Data: {load}")
        

sniff(filter="icmp", prn=print_it_please)