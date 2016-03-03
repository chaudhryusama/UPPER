#!/usr/bin/env python
# Title    :Tone-tx-rx-socket.py
# Function : tone transmitting and receiving #### now included sockets
# Author   : niaz

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
from gnuradio import gr, blks2, audio
from gnuradio.wxgui import stdgui2, scopesink2
from math import pi
import wx
import base64
import sys
import gnuradio.gr.gr_threading as _threading
from gnuradio import goodney
from gnuradio import tone
from time import sleep



# sockets


host ="127.0.0.1"                              
port = 5006
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

addr=(host,port)




TONE_FREQ=2000 #hz
AUDIO_RATE=48000 #samples/sec
TONE_DUR= 10#in msec (halved tone duration)
TONE_DUR_SAMP= TONE_DUR*AUDIO_RATE/1000 # the tone duration in samples 

# the following is defined to have a global variable showing how many 
# detections I can do . 	
class myCount:
	i=0
	
	
def message_callback(payload):
    error = False
  
    myCount.i= myCount.i+1
	
    print "Tone-Detection fired! %d\n" % myCount.i
    s.sendto( "Tone-Detection fired! %d\n" % myCount.i,addr) 

    
    #print "Hit Ctrl-D to exit.\n"

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

# Main Graph
class tone_rx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)
        audio_rate = AUDIO_RATE
        self.rcvd_pktq = gr.msg_queue()
         


        src = audio.source (audio_rate,"plughw:0,0")
		
#        mag = gr.complex_to_mag_squared ()
        mag = gr.complex_to_mag ()
		
        dft= gr.goertzel_fc(audio_rate,TONE_DUR_SAMP,TONE_FREQ) 
#        The gr.goertzel_fc constructor takes three arguments--the input sample
#rate, the Goertzel transform length ("points"), and the frequency of the
#bin of interest.  It accepts a stream of floats on its input, and for
#every "point" inputs, outputs a single complex DFT output corresponding
#to the frequency chosen during construction.  The Goertzel block length
#determines the selectivity of the transform (longer is better), but also
#sets the amount of time needed to detect a tone.
# the output from the magnitude block will be 0.5 maximum (not sure why)

        
       
		
                
        sink = tone.sink(self.rcvd_pktq,1)
        raw_wave = gr.wavfile_sink("receive-tone.wav", 1, audio_rate,16)
	
	mult = gr.multiply_const_ff(50)
        
        self.connect(src,dft,mag,sink)
        self.connect(src,raw_wave)
	self.watcher = _queue_watcher_thread(self.rcvd_pktq, message_callback)





########################## transmit part


msgq_limit = 8
TONE_FREQ=2000 #hz
AUDIO_RATE=48000 #samples/sec
TONE_DUR=20.0/1000.0#in sec
BITS_IN_BYTES=8
REPEAT_TIME= int((TONE_DUR*AUDIO_RATE)/BITS_IN_BYTES)

# Main Graph
class tone_tx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)
        audio_rate = AUDIO_RATE
    
        self.src = gr.message_source(gr.sizeof_char, msgq_limit)
    
        src = self.src
        
        b_to_syms = gr.bytes_to_syms()
		
        print " var=%d "% REPEAT_TIME
        
		#we know that there should always be just one byte of code 
        add = gr.add_const_ff(TONE_FREQ)
                    
        repeater = gr.repeat(gr.sizeof_float,REPEAT_TIME)
    
        fsk_f = gr.vco_f(audio_rate, 2*pi,1.0)
    
        speaker = audio.sink(audio_rate,"plughw:0,0");
        dst = gr.wavfile_sink("tone_tx.wav", 1, audio_rate, 16)
        
        self.connect(src,b_to_syms,add,repeater,fsk_f,speaker)
        self.connect(fsk_f,dst)



###################################### main


def main():
    

    fg=tone_tx()   
    fg1=tone_rx()
    fg1.start()		                 
    fg.start()
    try:
        while True:
	    global addr
            message, addr = s.recvfrom(1024)
            print (addr)
	    fg1.stop()
	 
	    
	    pkt = struct.pack('B', 0xff)
    
            msg = gr.message_from_string(pkt)
    
            fg.src.msgq().insert_tail(msg)
	    
            fg1.wait()
	    print "waiting"
	    time.sleep(2)             # defining some time for data rate
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








