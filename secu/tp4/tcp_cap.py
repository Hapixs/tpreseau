from scapy.all import sniff

def print_it_please(packet):
    if(packet["TCP"].flags == 2):
      print('TCP SYN ACK reçu !')
      print('- Adresse IP src : '+packet['IP'].src)
      print('- Adresse IP dest : '+packet['IP'].dst)
      print('- Port TCP src : '+str(packet['TCP'].sport))
      print('- Port TCP dest : '+str(packet['TCP'].dport))

sniff(filter="tcp[0xd]&18=2", prn=print_it_please, count=100)
