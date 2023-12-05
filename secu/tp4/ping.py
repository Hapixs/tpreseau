from scapy.all import *
ping = ICMP(type=8)
packet = IP(src="192.168.1.67", dst="192.168.1.1")
frame = Ether(src="e4:70:b8:77:79:be", dst="7c:c1:77:5e:1e:70")
final_frame = frame/packet/ping
answers, unanswered_packets = srp(final_frame, timeout=10)
print(f"Pong reçu : {answers[0]}")
