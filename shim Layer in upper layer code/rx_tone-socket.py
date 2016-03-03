#!/usr/bin/env python
# Title    : tx_tone.py
# Function : listen and detect tones 
# Author   : Affan Syed 

from gnuradio import gr, blks2, audio
from math import pi
import sys
import gnuradio.gr.gr_threading as _threading
from gnuradio import tone
from time import sleep
import socket

TONE_FREQ=3000 #hz
AUDIO_RATE=48000 #samples/sec
TONE_DUR= 10#in msec (halved tone duration)
TONE_DUR_SAMP= TONE_DUR*AUDIO_RATE/1000 # the tone duration in samples 



HOST = "localhost"      # The remote host 
PORT = 5000             # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))



# the following is defined to have a global variable showing how many 
# detections I can do . 	
class myCount:
	i=0
	
	
def message_callback(payload):
    error = False
  
    myCount.i= myCount.i+1
	
    s.send( "Tone-Detection fired! %d\n" % myCount.i )

    
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
class tone_graph(gr.top_block):

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
        self.connect(src,mult,raw_wave)
	self.watcher = _queue_watcher_thread(self.rcvd_pktq, message_callback)

def main():

    fg = tone_graph()
    fg.start()
        
    try:
        print "Hit Ctrl-D to exit NOW."
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
