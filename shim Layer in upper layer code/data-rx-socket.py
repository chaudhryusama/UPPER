#!/usr/bin/env python
# Title    : fsk_receive.py
# Function : online receiving of packets
# Author   : Andrew Goodney

from gnuradio import gr, blks2, audio
from gnuradio.wxgui import stdgui2, scopesink2
from math import pi
import wx
import base64
import sys
import gnuradio.gr.gr_threading as _threading
from gnuradio import goodney
from time import sleep
import socket

map_8b_6b = {135: 'H', 139: 'L', 141: 'N', 142: 'O', 147: 'T', 149: 'V', 150: 'W', 23: 'X', 153: 'Z', 154: 'a', 27: 'b', 156: 'c', 29: 'd', 30: 'e', 163: 'j', 165: 'l', 166: 'm', 39: 'n', 169: 'p', 170: 'q', 43: 'r', 172: 's', 45: 't', 46: 'u', 177: 'x', 178: 'y', 51: 'z', 180: '0', 53: '1', 54: '2', 184: '4', 57: '5', 58: '6', 60: '8', 195: 'D', 197: 'F', 198: 'G', 201: 'J', 202: 'K', 75: 'P', 204: 'M', 77: '9', 78: '+', 209: 'R', 210: 'S', 83: 'Q', 212: 'U', 86: '3', 216: 'Y', 89: 'A', 90: '7', 92: 'f', 225: 'h', 226: 'i', 99: 'g', 228: 'k', 101: 'E', 102: '/', 232: 'o', 105: 'I', 106: '=', 108: 'v', 113: 'B', 114: 'C', 116: 'w'}

HOST = "localhost"      # The remote host 
PORT = 5000             # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

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
	s.send(data)
	
    else:
        print "Error was detected."
	s.send("Error was detected")
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
	    #payload = ' i am doing this time right i guess : '
            if self.callback:
                self.callback(payload)

# Main Graph
class fsk_graph(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)
        
        self.rcvd_pktq = gr.msg_queue()
        
        audio_rate = 8000
         
        #src = gr.wavfile_source("./lptp2pc.wav", False)
        src = audio.source (audio_rate,"plughw:0,0")
	mult = gr.multiply_const_ff(10)   # multiply
	
        fsk_c = gr.hilbert_fc((audio_rate/300)+1)
	

	chk = gr.wavfile_sink("testing.wav", 1, audio_rate, 16)
        


        bp_coeff = gr.firdes.band_pass(1,audio_rate,500,3500,100)
        bpf = gr.fir_filter_fff(1,bp_coeff)
        
        quad_demod = gr.quadrature_demod_cf(1.0)
        
        #speaker = audio.sink(audio_rate, "plughw:0,0");
        
        hpf_coeff = gr.firdes.high_pass(10, audio_rate, 10, 5)
        dc_block = gr.fir_filter_fff (1, hpf_coeff)
        
        mm = gr.clock_recovery_mm_ff(80,0.000625,0.5,0.01,0.05)
        
        slicer = gr.binary_slicer_fb()
        
        sync_corr = gr.correlate_access_code_bb("0100011101111000",0)
        
        #sink = gr.file_sink(gr.sizeof_char, "decoded.bin")
        sink = goodney.sink2(self.rcvd_pktq)
        
        #self.connect(src,chk)
        self.connect(src,bpf,fsk_c,quad_demod,dc_block,mm,slicer,sync_corr,sink)
        #self.connect(src,bpf,fsk_c,quad_demod,dc_block,mm,slicer,file_sink)
       
	
        self.watcher = _queue_watcher_thread(self.rcvd_pktq, message_callback)
        
def main():
	
    
       
    fg = fsk_graph()
    fg.start()          
    

    
    try:
        print "Hit Ctrl-D to exit."
        while True:
            raw_input("")
    except EOFError:
        print "\nExiting."
        #fg.wait()

# Main python entry
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
