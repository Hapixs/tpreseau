from scapy.all import *
from sys import argv
import zlib

def sendSomething(data):
    pingr=IP(dst=ip)/ICMP()/Padding(data)
    print(f"Sending '{data}' in ICMP to {ip}")
    send(pingr)

ip = argv[1]
data = " ".join(argv[2:])

print("Preparing text to be sent...")
print(f"Original size: {sys.getsizeof(data)}")

data_compressed=zlib.compress(data.encode())
print(f"New size compressed: {sys.getsizeof(data_compressed)}")


slicedData = []
while (len(data_compressed) > 0):
    slicedData.append(data_compressed[:4])
    data_compressed=data_compressed[4:]

for d in slicedData:
    sendSomething(d)

sendSomething("hxcEnded")