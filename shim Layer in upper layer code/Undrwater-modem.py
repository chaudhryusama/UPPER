#!/usr/bin/env python
# Title    : undrwater-modem.py
# Function : Underwater Modem capable of transmitting and receiving Data & Tone
# Author   : Niaz Ahmed


#-------------------------------------------------------                Import Section
#-------------------------------------------------------

import socket
from gnuradio import gr, blks2, audio
from gnuradio.wxgui import stdgui2, scopesink2
from math import pi
import wx
import base64
import struct
import time
from time import sleep
import sys
import gnuradio.gr.gr_threading as _threading
from gnuradio import goodney
from gnuradio import tone

#---------------------------------------------------------             Mapping    
#---------------------------------------------------------

map_6b_8b = {'+': 78, '/': 102, '1': 53, '0': 180, '3': 86, '2': 54, '5': 57, '4': 184, '7': 90, '6': 58, '9': 77, '8': 60, '=': 106, 'A': 89, 'C': 114, 'B': 113, 'E': 101, 'D': 195, 'G': 198, 'F': 197, 'I': 105, 'H': 135, 'K': 202, 'J': 201, 'M': 204, 'L': 139, 'O': 142, 'N': 141, 'Q': 83, 'P': 75, 'S': 210, 'R': 209, 'U': 212, 'T': 147, 'W': 150, 'V': 149, 'Y': 216, 'X': 23, 'Z': 153, 'a': 154, 'c': 156, 'b': 27, 'e': 30, 'd': 29, 'g': 99, 'f': 92, 'i': 226, 'h': 225, 'k': 228, 'j': 163, 'm': 166, 'l': 165, 'o': 232, 'n': 39, 'q': 170, 'p': 169, 's': 172, 'r': 43, 'u': 46, 't': 45, 'w': 116, 'v': 108, 'y': 178, 'x': 177, 'z': 51}


map_8b_6b = {135: 'H', 139: 'L', 141: 'N', 142: 'O', 147: 'T', 149: 'V', 150: 'W', 23: 'X', 153: 'Z', 154: 'a', 27: 'b', 156: 'c', 29: 'd', 30: 'e', 163: 'j', 165: 'l', 166: 'm', 39: 'n', 169: 'p', 170: 'q', 43: 'r', 172: 's', 45: 't', 46: 'u', 177: 'x', 178: 'y', 51: 'z', 180: '0', 53: '1', 54: '2', 184: '4', 57: '5', 58: '6', 60: '8', 195: 'D', 197: 'F', 198: 'G', 201: 'J', 202: 'K', 75: 'P', 204: 'M', 77: '9', 78: '+', 209: 'R', 210: 'S', 83: 'Q', 212: 'U', 86: '3', 216: 'Y', 89: 'A', 90: '7', 92: 'f', 225: 'h', 226: 'i', 99: 'g', 228: 'k', 101: 'E', 102: '/', 232: 'o', 105: 'I', 106: '=', 108: 'v', 113: 'B', 114: 'C', 116: 'w'}

#-----------------------------------------------------------          Global Functions
#-----------------------------------------------------------

def encode_6b_8b(b64_in):
    out = []
    for c in b64_in:
        out.append(map_6b_8b[c])
    return out

#-----------------------------------------------------------          Global Variables
#-----------------------------------------------------------

clock_sync = [85,85,85,85]
sync = [71,120]
stop_sync = [85,85,85,85,85,85]
msgq_limit = 4


AUDIO_RATE=48000                                         #samples/sec

#TONE_FREQ=2000                                           #hz
TONE_TX_DUR=20.0/1000.0                                  #in sec
BITS_IN_BYTES=8                                         
#REPEAT_TIME= int((TONE_DUR*AUDIO_RATE)/BITS_IN_BYTES)
TONE_RX_DUR= 10 
TONE_DUR_SAMP= TONE_RX_DUR*AUDIO_RATE/1000 # the tone duration in samples                                          
CENTER_FREQ=2000   
TONE_FREQ=CENTER_FREQ                                    # 	constant to be added to add_const Block for Data frequency
MULTIPLIER=1000                                            #   constant to be multiplied in mult_const Blocs for Data frequency
AMPLITUDE=1                                              #   constant multiplier to set amplitude when required

REPEAT_TIME=480		                                 # REPEAT TIME FOR TONE AND DATA
BP_START=CENTER_FREQ-1500                                # BAND PASS START AND STOP LIMITS
BP_STOP=CENTER_FREQ+1500



#------------------------------------------------------------       SOCKET DEFINITION
#------------------------------------------------------------


host ="127.0.0.1"                              
port = 5006
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

addr=(host,port)















################################################################################################################################################
#################################################        Receiver Part          ################################################################
################################################################################################################################################

#-------------------------------------------------  Call Backs  and Queue Watcher Threads


def message_callback(payload):
    error = False
    message64 = ""
    print "Message Callback fired!"
    print "Message length: ",len(payload)
    for byte in payload:
        try:
            message64 = message64 + map_8b_6b[ord(byte)]
        except KeyError:
            message64 = message64 + '[%i]' % ord(byte)
            error = True
    
    if error == False:
        data = base64.standard_b64decode(message64)
        print "Decoded to: %s" % base64.standard_b64decode(message64)
	s.sendto(data,addr)
    else:
         s.sendto("Error was detected.",addr)           # here lies the problem ---> sendto
    

class _queue_watcher_thread(_threading.Thread):
    def __init__(self, rcvd_pktq, callback):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.rcvd_pktq = rcvd_pktq
        self.callback = callback
        self.keep_running = True
        self.start()


    def run(self):
        while self.keep_running:
            msg = self.rcvd_pktq.delete_head()
            payload = msg.to_string()
            if self.callback:
                self.callback(payload)
	
class myCount:
	i=0
	
	
def message_callback_tone(payload):
    error = False
  
    myCount.i= myCount.i+1	
    s.sendto( "TONE %d\n" % myCount.i,addr) 
    
    

class _queue_watcher_thread_tone(_threading.Thread):
    def __init__(self, rcvd_pktq_tone, callback_tone):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.rcvd_pktq_tone = rcvd_pktq_tone
        self.callback_tone = callback_tone
        self.keep_running = True
        self.start()


    def run(self):
        while self.keep_running:
            msg = self.rcvd_pktq_tone.delete_head()
            payload = msg.to_string()
            if self.callback_tone:
                self.callback_tone(payload)






#------------------------------------------------------ Heir Blocks For Tone and Data


class HierBlock_data(gr.hier_block2):
     def __init__(self):
          gr.hier_block2.__init__(self, "HierBlock_data",
                         gr.io_signature(1, 1, gr.sizeof_float),
                         gr.io_signature(1, 1, 1))
  
          fsk = gr.hilbert_fc((AUDIO_RATE/300)+1)
          bp_coeff = gr.firdes.band_pass(1,AUDIO_RATE,BP_START,BP_STOP,100)
          bpf = gr.fir_filter_fff(1,bp_coeff)
        
          quad_demod = gr.quadrature_demod_cf(1.0)
         
          hpf_coeff = gr.firdes.high_pass(10, AUDIO_RATE, 10, 5)
          dc_block = gr.fir_filter_fff (1, hpf_coeff)
        	
          mm = gr.clock_recovery_mm_ff(REPEAT_TIME,0.000625,0.5,0.01,0.05)
        
          slicer = gr.binary_slicer_fb()
        
          sync_corr = gr.correlate_access_code_bb("0100011101111000",0)
          
        
          self.connect(self,bpf,fsk,quad_demod,dc_block,mm,slicer,sync_corr,self)
         

class HierBlock_tone(gr.hier_block2):
     def __init__(self):
          gr.hier_block2.__init__(self, "HierBlock_tone",
                         gr.io_signature(1, 1, gr.sizeof_float),
                         gr.io_signature(1, 1, 4))

          mag = gr.complex_to_mag ()
		
          dft= gr.goertzel_fc(AUDIO_RATE,TONE_DUR_SAMP,TONE_FREQ) 

          self.connect(self,dft,mag,self)
 
        
 
#------------------------------------------------------------------ RECEIVER FLOW GRAPH

class Rx_graph(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)
        self.rcvd_pktq = gr.msg_queue()
	self.rcvd_pktq_tone = gr.msg_queue()
        
	mult = gr.multiply_const_ff(0.2)		# attenuating signal for tone triggering
	src = audio.source (AUDIO_RATE,"plughw:0,0")
        raw_wave = gr.wavfile_sink("recieve.wav", 1, AUDIO_RATE,16)	
	hierblock1= HierBlock_data()
	hierblock2= HierBlock_tone()
	
	sink = goodney.sink2(self.rcvd_pktq)
	sink2 = tone.sink(self.rcvd_pktq_tone,1)
        
	
        self.connect(src,hierblock1,sink)
        self.connect(src,mult,hierblock2,sink2)

	self.watcher = _queue_watcher_thread(self.rcvd_pktq, message_callback)
        self.watcher = _queue_watcher_thread_tone(self.rcvd_pktq_tone, message_callback_tone)

################################################################################################################################################
#################################################        TRASMITTING PART        ###############################################################
################################################################################################################################################



class Tx_graph(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)
        
        self.src = gr.message_source(gr.sizeof_char, msgq_limit)
        src = self.src
        
        b_to_syms = gr.bytes_to_syms()
        
        self.mult = gr.multiply_const_ff(MULTIPLIER)
    
        add = gr.add_const_ff(CENTER_FREQ)
                    
        repeater = gr.repeat(gr.sizeof_float,REPEAT_TIME)
    
        fsk_f = gr.vco_f(AUDIO_RATE, 2*pi,0.5)

	speaker = audio.sink(AUDIO_RATE, "plughw:0,0");
	
        self.connect(src,b_to_syms,self.mult,add,repeater,fsk_f,speaker)
	


################################################################################################################################################
#################################################       MAIN      ###############################################################
################################################################################################################################################



def main():
    


    fg=Tx_graph()   
    fg1=Rx_graph()
    fg1.start()		                 
    fg.start()
    try:
        while True:
	    global addr
            msg, addr = s.recvfrom(1024)
            
	    
            
            if msg[:1]=='1':
		message=msg[1:len(msg)]
		fg.mult.set_k(MULTIPLIER)	
	        fg1.stop()
	 
	    	print (message)
	        msg64 = base64.standard_b64encode(message)
                print "Encoding message= %s to base64= %s" % (message,msg64)
                payload = clock_sync+sync+encode_6b_8b(msg64)+stop_sync
                pkt = struct.pack('%iB' % (len(payload)),*payload)
                msg = gr.message_from_string(pkt)
                fg.src.msgq().insert_tail(msg)
	        print (msg)
                fg1.wait()
	        time.sleep(1.28)             # defining some time for data rate
	        fg1.start()

		 

               
             
            elif msg[:1]=='2':
		
		
		
		message=msg[1:len(msg)]
		fg.mult.set_k(1)
		print (message)
		fg1.stop()	
		pkt = struct.pack('B', 0xff)
                msg = gr.message_from_string(pkt)
                
		fg.src.msgq().insert_tail(msg)
		fg1.wait()
	        time.sleep(TONE_TX_DUR)             # defining some time for data rate
	        fg1.start()

	    elif msg[:1]=='3':
		global AUDIO_RATE,CENTER_FREQ,TONE_FREQ,BP_START,BP_STOP
		AUDIO_RATE=int(msg[2:4])*1000                                       
		CENTER_FREQ=int(msg[5:7])*1000   
		TONE_FREQ=CENTER_FREQ                                    
		BP_START=CENTER_FREQ-1500                                
		BP_STOP=CENTER_FREQ+1500
		print(AUDIO_RATE,':',CENTER_FREQ)


    except EOFError:
        print "\nExiting."
        fg.src.msgq().insert_tail(gr.message(1))
        fg.wait()






    
    

   

# Main python entry
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass



