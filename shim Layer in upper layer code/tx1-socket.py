#!/usr/bin/env python
# Title    : Transmitter-block.py
# Function : Transmittind tone and data  
# Author   : Niaz Ahmed
#--------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------// import section  //------------------------------------
#--------------------------------------------------------------------------------------------------------------
from gnuradio import gr, blks2, audio
from gnuradio.wxgui import stdgui2, scopesink2
from math import pi
import wx
import base64
import struct
from socket import *
from socket import *
import socket

from gnuradio import gr, blks2, audio
from math import pi
import struct

#---------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------// Fsk-Transmitter code  // ------------------------------
#----------------------------------------------------------------------------------------------------------------
map_6b_8b = {'+': 78, '/': 102, '1': 53, '0': 180, '3': 86, '2': 54, '5': 57, '4': 184, '7': 90, '6': 58, '9': 77, '8': 60, '=': 106, 'A': 89, 'C': 114, 'B': 113, 'E': 101, 'D': 195, 'G': 198, 'F': 197, 'I': 105, 'H': 135, 'K': 202, 'J': 201, 'M': 204, 'L': 139, 'O': 142, 'N': 141, 'Q': 83, 'P': 75, 'S': 210, 'R': 209, 'U': 212, 'T': 147, 'W': 150, 'V': 149, 'Y': 216, 'X': 23, 'Z': 153, 'a': 154, 'c': 156, 'b': 27, 'e': 30, 'd': 29, 'g': 99, 'f': 92, 'i': 226, 'h': 225, 'k': 228, 'j': 163, 'm': 166, 'l': 165, 'o': 232, 'n': 39, 'q': 170, 'p': 169, 's': 172, 'r': 43, 'u': 46, 't': 45, 'w': 116, 'v': 108, 'y': 178, 'x': 177, 'z': 51}
clock_sync = [85,85,85,85]
sync = [71,120]
stop_sync = [85,85,85,85,85,85]
msgq_limit = 4

def encode_6b_8b(b64_in):
    out = []
    for c in b64_in:
        out.append(map_6b_8b[c])
    return out

i=1

class main_graph(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)
        audio_rate =48000
        self.src = gr.message_source(gr.sizeof_char, msgq_limit)
        
 
        src = self.src
        
        b_to_syms = gr.bytes_to_syms()
        
        self.mult = gr.multiply_const_ff(i)
    
        add = gr.add_const_ff(2000)
                    
        repeater = gr.repeat(gr.sizeof_float,480)
    
        fsk_f = gr.vco_f(audio_rate, 2*pi,0.5)

	speaker = audio.sink(audio_rate, "plughw:0,0");
	dst = gr.wavfile_sink("tx.wav", 1, audio_rate, 16)
        self.connect(src,b_to_syms,self.mult,add,repeater,fsk_f,speaker)
	self.connect(fsk_f,dst)



#----------------------------------------------------------------------------------------------------------------
#-------------------------------------------------//  main    //-------------------------------------------------
#--------------------------------------------------------------------------------------------------------------



def main():
    HOST = ''                          # Symbolic name meaning all available interfaces
    PORT = 50098		              # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    print 'Connected by', addr   

    fg = main_graph()
    fg.start()                       # start flow graph
 
    try:
        while True:
	    choice = conn.recv(256)
	    	
            if choice == tone :	
		print ("tone haaha")
		conn.send(" Transmit a 5ms tone : ") 
		#message=conn.recv(256)
		
		conn.send(" tone sent ") 
		fg.mult.set_k(1)	
		pkt = struct.pack('B', 0xff)
                msg = gr.message_from_string(pkt)
                
		fg.src.msgq().insert_tail(msg)
		
		 

               
             
            else :
		print ("data afgadf")
		fg.mult.set_k(1000)	
		conn.send("Enter a message to transmit : ") 
		message=conn.recv(256)
            	msg64 = base64.standard_b64encode(message)
            	print "Encoding message= %s to base64= %s" % (message,msg64)
    		
 	        payload = clock_sync+sync+encode_6b_8b(msg64)+stop_sync
            	pkt = struct.pack('%iB' % (len(payload)),*payload)
    		conn.send(" data sent ") 
            	msg = gr.message_from_string(pkt)
		fg.src.msgq().insert_tail(msg)
		
		
		
		
	   	
    		



    except EOFError:
        print "\nExiting."
        fg.src.msgq().insert_tail(gr.message(1))
        fg.wait()
    
       	
    
   
#-----------------------------------------------------------------------------------------------------------------
#------------------------------------------------//  Main Python Entry    //---------------------------------------
#-------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass        











