#!/usr/bin/env python
# Title    : tx-rx1.py
# Function : data transmitting and receiving #### now included sockets
# Author   : Andrew Goodney

from gnuradio import gr, blks2, audio
from gnuradio.wxgui import stdgui2, scopesink2
from math import pi
import wx
import base64
import struct
import time
from time import sleep
import sys
import socket

# sockets


host ="127.0.0.1"                              
port = 5006
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

addr=(host,port)


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


from gnuradio import gr, blks2, audio
from gnuradio.wxgui import stdgui2, scopesink2
from math import pi
import wx
import base64
import sys
import gnuradio.gr.gr_threading as _threading
from gnuradio import goodney
from time import sleep

map_8b_6b = {135: 'H', 139: 'L', 141: 'N', 142: 'O', 147: 'T', 149: 'V', 150: 'W', 23: 'X', 153: 'Z', 154: 'a', 27: 'b', 156: 'c', 29: 'd', 30: 'e', 163: 'j', 165: 'l', 166: 'm', 39: 'n', 169: 'p', 170: 'q', 43: 'r', 172: 's', 45: 't', 46: 'u', 177: 'x', 178: 'y', 51: 'z', 180: '0', 53: '1', 54: '2', 184: '4', 57: '5', 58: '6', 60: '8', 195: 'D', 197: 'F', 198: 'G', 201: 'J', 202: 'K', 75: 'P', 204: 'M', 77: '9', 78: '+', 209: 'R', 210: 'S', 83: 'Q', 212: 'U', 86: '3', 216: 'Y', 89: 'A', 90: '7', 92: 'f', 225: 'h', 226: 'i', 99: 'g', 228: 'k', 101: 'E', 102: '/', 232: 'o', 105: 'I', 106: '=', 108: 'v', 113: 'B', 114: 'C', 116: 'w'}

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
    
    print "Received base64 message= %s" % (message64)
    if error == False:
	data = base64.standard_b64decode(message64)
        print "Decoded to: %s" % base64.standard_b64decode(message64)
	print(addr)
        s.sendto(data,addr)
    else:
        s.sendto("Error was detected.",addr) 
    print "Message Callback fired!"
    print "Hit Ctrl-D to exit."

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






class fsk_rx_graph(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)
        
        self.rcvd_pktq = gr.msg_queue()
        
        audio_rate = 8000
         
        #src = gr.wavfile_source("./lptp2pc.wav", False)
        src = audio.source (audio_rate,"plughw:0,0")
	mult = gr.multiply_const_ff(10)   # multiply
	
        fsk_c = gr.hilbert_fc((audio_rate/300)+1)
	

	


        bp_coeff = gr.firdes.band_pass(1,audio_rate,500,3500,100)
        bpf = gr.fir_filter_fff(1,bp_coeff)
        
        quad_demod = gr.quadrature_demod_cf(1.0)
        
        
        
        hpf_coeff = gr.firdes.high_pass(10, audio_rate, 10, 5)
        dc_block = gr.fir_filter_fff (1, hpf_coeff)
        
        mm = gr.clock_recovery_mm_ff(80,0.000625,0.5,0.01,0.05)
        
        slicer = gr.binary_slicer_fb()
        
        sync_corr = gr.correlate_access_code_bb("0100011101111000",0)
        
        #sink = gr.file_sink(gr.sizeof_char, "decoded.bin")
        sink = goodney.sink2(self.rcvd_pktq)
        
        #self.connect(src,speaker)
        self.connect(src,bpf,fsk_c,quad_demod,dc_block,mm,slicer,sync_corr,sink)
      
        self.watcher = _queue_watcher_thread(self.rcvd_pktq, message_callback)
        


class fsk_graph(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)
        audio_rate =8000
        self.src = gr.message_source(gr.sizeof_char, msgq_limit)
    
        src = self.src
        
        b_to_syms = gr.bytes_to_syms()
        
        mult = gr.multiply_const_ff(1000)
    
        add = gr.add_const_ff(2000)
                    
        repeater = gr.repeat(gr.sizeof_float,80)
    
        fsk_f = gr.vco_f(audio_rate, 2*pi,0.5)
    
        speaker = audio.sink(audio_rate, "plughw:0,0");
        dst = gr.wavfile_sink("testing.wav", 1, audio_rate, 16)
        
        self.connect(src,b_to_syms,mult,add,repeater,fsk_f,speaker)
        self.connect(fsk_f,dst)
 













       
def main():
    

    fg=fsk_graph()   
    fg1=fsk_rx_graph()
    fg1.start()		                 
    fg.start()
    try:
        while True:
	    global addr
            message, addr = s.recvfrom(1024)
            print (addr)
	    fg1.stop()
	 
	    
	    msg64 = base64.standard_b64encode(message)
            print "Encoding message= %s to base64= %s" % (message,msg64)
            payload = clock_sync+sync+encode_6b_8b(msg64)+stop_sync
            pkt = struct.pack('%iB' % (len(payload)),*payload)
            msg = gr.message_from_string(pkt)
            fg.src.msgq().insert_tail(msg)
	    
            fg1.wait()
	    print "waiting"
	    time.sleep(5)             # defining some time for data rate
	    print " \nrestarting"
            fg1.start()

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
