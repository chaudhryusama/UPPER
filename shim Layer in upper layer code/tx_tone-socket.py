#!/usr/bin/env python
# Title    : tx_tone.py
# Function :transmit a tone on user input
# Author   : Affan Syed

from gnuradio import gr, blks2, audio
from math import pi
import struct
import socket

msgq_limit = 8
TONE_FREQ=3000 #hz
AUDIO_RATE=48000 #samples/sec
TONE_DUR=20.0/1000.0#in sec
BITS_IN_BYTES=8
REPEAT_TIME= int((TONE_DUR*AUDIO_RATE)/BITS_IN_BYTES)

# Main Graph
class tone_graph(gr.top_block):

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
       
        
def main():
    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = 5009	              # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    print 'Connected by', addr   
    fg = tone_graph()
    
    fg.start()                       # start flow graph
    
    try:
        while True:
            message = raw_input(" transmit a 5ms tone (Ctrl-D to exit): ") 
			
			#make a one byte packet to indicate the tone transmission.
            pkt = struct.pack('B', 0xff)
    
            msg = gr.message_from_string(pkt)
    
            fg.src.msgq().insert_tail(msg)
	    conn.send("received")		
 
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
