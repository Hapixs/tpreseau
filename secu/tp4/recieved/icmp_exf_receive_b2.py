from scapy.all import *
import sys
import zlib
import re


def clear():
    os.system('cls' if os.name=='nt' else 'clear')

class TransactionReader(object):

    recievedData = bytes()
    fType = None
    fName = None
    fPath = './'
    tBlocks = 0
    tBlocksRecieved = 0
    enc = None

    headerComplete = False
    headerString = ""

    currentThread: Thread = None

    senderIp = ""

    state = "N/A"

    def end_it_please(self):
        with open(f"{self.fPath}{self.fName}.{self.fType}", "w") as outfile:
            outfile.buffer.write(zlib.decompress(self.recievedData))
            outfile.close()
        self.state = "Complete !"


    def process_it_please(self, packet):
        if (not packet.haslayer(Padding)): return
        padding: str = packet['Padding'].load
        if(not self.headerComplete):
            if(padding==bytes("!header","UTF8")):
                self.headerComplete = True
                self.headerString=str(self.headerString)
                self.fType = re.search(r"ft-([a-zA-Z0-9_\-\/]+)[;]", self.headerString).group(1) or "txt" if "ft-" in self.headerString else ".txt"
                self.fName =  re.search(r"fn-([a-zA-Z0-9_\-\/]+)[;]", self.headerString).group(1) or "latestFile" if "fn-" in self.headerString else "latestFile"
                self.fPath =  re.search(r"fp-([a-zA-Z0-9_\-\/]+)[;]", self.headerString).group(1) or "./" if "fp-" in self.headerString else "./"
                self.tBlocks = re.search(r"tb-([0-9]+)[;]", self.headerString).group(1) or 0 if "tb-" in self.headerString else 0
                self.tBlocks=int(self.tBlocks)+1
                self.state = "Receiving ..."
                return
            self.headerString+=bytes(padding).decode()
            return
        self.recievedData+=padding
        self.tBlocksRecieved+=1

    def __start(self, sender_ip, dest_ip):
        self.state = "Heading ..."
        self.senderIp = sender_ip
        sniff(filter=f"icmp and src host {sender_ip} and dst host {dest_ip}", prn=self.process_it_please, stop_filter=lambda packet: not packet.haslayer(Padding) or packet["Padding"].load==bytes("end transaction", "UTF8"))
        self.state = "Saving ..."
        self.end_it_please()


    def startSniff(self, sender_ip, dest_ip):
        self.currentThread = threading.Thread(target=self.__start(sender_ip, dest_ip))
        self.currentThread.start()
        self.currentThread.join()

transactions: list[TransactionReader] = list()

def process_it_please(packet):
    if (packet.haslayer(Padding)):
        load = packet['Padding'].load
        if(load == bytes("header","UTF8")):
            t = TransactionReader()
            transactions.append(t)
            t.startSniff(packet["IP"].src, packet["IP"].dst)
        
def mainSniff():
    sniff(filter="icmp", prn=process_it_please) 


def update_the_screen_please():
    while True:
        clear()
        print( """ 
         ██▓███   ██▓ ███▄    █   ▄████     ███▄ ▄███▓▓█████ 
        ▓██░  ██▒▓██▒ ██ ▀█   █  ██▒ ▀█▒   ▓██▒▀█▀ ██▒▓█   ▀ 
        ▓██░ ██▓▒▒██▒▓██  ▀█ ██▒▒██░▄▄▄░   ▓██    ▓██░▒███   
        ▒██▄█▓▒ ▒░██░▓██▒  ▐▌██▒░▓█  ██▓   ▒██    ▒██ ▒▓█  ▄ 
        ▒██▒ ░  ░░██░▒██░   ▓██░░▒▓███▀▒   ▒██▒   ░██▒░▒████▒
        ▒▓▒░ ░  ░░▓  ░ ▒░   ▒ ▒  ░▒   ▒    ░ ▒░   ░  ░░░ ▒░ ░
        ░▒ ░      ▒ ░░ ░░   ░ ▒░  ░   ░    ░  ░      ░ ░ ░  ░
        ░░        ▒ ░   ░   ░ ░ ░ ░   ░    ░      ░      ░   
                  ░           ░       ░           ░      ░  ░
        """)

        print(f"Transactions: {len(transactions)}")
        for t in transactions:
            print(f"Transaction: [{t.senderIp}] {t.fPath}{t.fName}.{t.fType} => {t.tBlocksRecieved}/{t.tBlocks} | {t.state}")
        time.sleep(0.1)


screenThread = threading.Thread(target=update_the_screen_please)
mainSniffThread = threading.Thread(target=mainSniff)

screenThread.start()
mainSniffThread.start()

mainSniffThread.join()