from scapy.all import *
import sys
import zlib
import re
import multiprocessing


"""
    Bon le 'multithreading' fonctionne, c'est juste scapy qui quand il fait un snif lock ses trucs
    L'idée la c'est rendre tout ca jolie avec rich pour un jolie terminal
    et apres ajouter des args et ensuite opti le code parceque c'est quand même dégueulasse.

"""


def clear():
    os.system('cls' if os.name=='nt' else 'clear')

class TransactionReader(object):

    def __init__(self, senderIp):
        self.recievedData = bytes()
        self.fType = None
        self.fName = None
        self.fPath = './'
        self.tBlocks = 0
        self.tBlocksRecieved = 0
        self.enc = None
        self.headerComplete = False
        self.headerString = ""
        self.senderIp = senderIp
        self.state = "N/A"
        self.percent = 0

    def end_it_please(self):
        self.state = "Saving ..."
        os.makedirs(self.fPath, exist_ok=True)
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
                self.tBlocks=int(self.tBlocks)
                self.state = "Receiving ..."
                return
            self.headerString+=bytes(padding).decode()
            return
        self.recievedData+=padding
        self.tBlocksRecieved+=1
        self.percent = math.floor(self.tBlocksRecieved/self.tBlocks*100)
        

transactions: list[TransactionReader] = list()
transactionmap = {}

def process_it_please(packet):
    if (packet.haslayer(Padding)):
        id = f'{packet["IP"].src}-{packet["IP"].dst}'
        load = packet['Padding'].load
        if(load == bytes("header","UTF8")):
            t = TransactionReader(packet["IP"].src)
            transactions.append(t)
            if (id in transactionmap):
                t.state = "Error ..."
                transactionmap[id].state = "Error ..."
                transactionmap[id].pop(id)
                return
            transactionmap[id] = t
        if (not packet.haslayer(Padding) or packet["Padding"].load==bytes("end transaction", "UTF8")):
            transactionmap[id].end_it_please()
            transactionmap.pop(id)
        else:
            if (id in transactionmap):
             transactionmap[id].process_it_please(packet)
        
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
             print(f"Transaction: [{t.senderIp}] {t.fPath}{t.fName}.{t.fType} => ({t.tBlocksRecieved}/{t.tBlocks}) {t.percent}% | {t.state} ")
         time.sleep(0.1)


screenThread = threading.Thread(target=update_the_screen_please)
mainSniffThread = threading.Thread(target=mainSniff)

screenThread.start()
mainSniffThread.start()

screenThread.join()