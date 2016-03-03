#!/usr/bin/env python

import time
import thread
import socket
from SimpleXMLRPCServer import SimpleXMLRPCServer
import Queue

from threading import Lock
from time import sleep




tone="T"
data="d"
tx=Lock()
UDP_IP="127.0.0.1"
UDP_PORT=5006
   
sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP
Tx_buff = Queue.Queue()

Data_Rx_buff = Queue.Queue()
Tone__Rx_buff = Queue.Queue()



def receiver():#(UDP_IP,UDP_PORT):
    while 1:
	
	recvd_packet, addr = sock.recvfrom( 1024 ) # buffer size is 1024 bytes
	print recvd_packet
	if recvd_packet[:4]=="TONE":
	   global tone
	   tone=("Tone Detected")
           Tone_Rx_buff.put(tone)
	else :
	   global data
	   data=recvd_packet  
	   Data_Rx_buff.put(data)    



def transmitter(UDP_IP,UDP_PORT):
    while 1:
	#tx.acquire()
	print "a"
	message=Tx_buff.get()     # TODO  add if empty queue 
	print message
	if message=="2" :
		TX_DUR=0.02
	else :
		TX_DUR=(((((len(message)-1)/4)*4)+16)*8)/100  #  16 = extra encoding bits,  8 = no of bits in a byte,  100 = data rate
	sock.sendto(message ,(UDP_IP, UDP_PORT) )
	time.sleep(TX_DUR) 
	#tx.release()
	




class UnderWaterModem:
   
   def send_data(self,message):
	print message
	message=("1"+message)
	Tx_buff.put(message)
	return ("data sending")
       

   def send_tone(self,message):
	
	message=("2")	
	Tx_buff.put(message)
	return ("tone sending")
	


   def set_configuration(self,message):                     # TODO this block still needs to be worked on

	print (message)
	message=("3"+message)

	#tx.acquire()
	sock.sendto(message ,(UDP_IP, UDP_PORT) )
	return ("tone sending")
	sock.sendto(message ,(UDP_IP, UDP_PORT) )
	#time.sleep(TONE_TX_DUR) 
	#tx.release()

  
   def recv_data(self):
       #need to add empty conditions
       return Data_Rx_buff.get()
   def recv_tone(self):
	#need to add empty conditions
       return Tone_Rx_buff.get()
      

   
if __name__=="__main__":
     sock.sendto(("start") ,(UDP_IP, UDP_PORT) )              # FIXME to start communication with the socket
     thread.start_new_thread(receiver,())   #(UDP_IP, UDP_PORT,)
     thread.start_new_thread(transmitter,(UDP_IP, UDP_PORT,))   
     server = SimpleXMLRPCServer(("localhost", 8000))
     print "Listening on port 8000..."
     server.register_instance(UnderWaterModem())
     server.serve_forever()

   
      
       
     
