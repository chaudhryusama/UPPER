#!/usr/bin/env python
#
# IMPORTANT: READ BEFORE DOWNLOADING, COPYING OR USING. By
# downloading, copying or using the script you agree to
# this license. If you do not agree to this license, do not #download,
# install or use the script.
#
# Copyright (c) 2011-2014 SysNet Research lab, NUCES-Islamabad
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the
# distribution.
# - Neither the name of the copyright holder nor the names of
# its contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
# @author Niaz Ahmed <niaz.ahmed@sysnet.edu.pk>
# @author Andrew Goodney <goodney@usc.edu>
# @author Ch. Muhammad Usama <chaudhry.usama@sysnet.edu.pk>
#



from gnuradio import gr, blks2, audio
from gnuradio.wxgui import stdgui2, scopesink2
from math import pi
import wx
import base64
import struct
import time
from time import sleep

map_6b_8b = {'+': 78, '/': 102, '1': 53, '0': 180, '3': 86, '2': 54, '5': 57, '4': 184, '7': 90, '6': 58, '9': 77, '8': 60, '=': 106, 'A': 89, 'C': 114, 'B': 113, 'E': 101, 'D': 195, 'G': 198, 'F': 197, 'I': 105, 'H': 135, 'K': 202, 'J': 201, 'M': 204, 'L': 139, 'O': 142, 'N': 141, 'Q': 83, 'P': 75, 'S': 210, 'R': 209, 'U': 212, 'T': 147, 'W': 150, 'V': 149, 'Y': 216, 'X': 23, 'Z': 153, 'a': 154, 'c': 156, 'b': 27, 'e': 30, 'd': 29, 'g': 99, 'f': 92, 'i': 226, 'h': 225, 'k': 228, 'j': 163, 'm': 166, 'l': 165, 'o': 232, 'n': 39, 'q': 170, 'p': 169, 's': 172, 'r': 43, 'u': 46, 't': 45, 'w': 116, 'v': 108, 'y': 178, 'x': 177, 'z': 51}
clock_sync = [85,85,85,85]
test_bit = [83]
sync = [71,120]
stop_sync = [85,85,85,85,85,85]
msgq_limit = 1

CentreFreq=17000
DataRate=100
RepeatTime=480
AudioRate=48000   # orignally 48k here




def encode_6b_8b(b64_in):
    out = []
    for c in b64_in:
        out.append(map_6b_8b[c])
    return out
    
# Main Graph
class fsk_graph(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)
        audio_rate =48000 # audio rate changed
	
        self.src = gr.message_source(gr.sizeof_char, msgq_limit)
    
        src = self.src
        
        b_to_syms = gr.bytes_to_syms()
        
        mult = gr.multiply_const_ff(1000)
	
    
        add = gr.add_const_ff(CentreFreq)
                    
        repeater = gr.repeat(gr.sizeof_float,RepeatTime)
    
        fsk_f = gr.vco_f(audio_rate, 2*pi,0.5)   # Sensitivity is rad/sec/volt ( e.g 2*pi*f/sec = 1Khz) and here f = volts (input amplitude of VCO)
    	attenuator = gr.multiply_const_ff(0.05)   # multiply
        speaker = audio.sink(audio_rate, "plughw:0,0");
        dst = gr.wavfile_sink("tx-signal.wav",1, audio_rate, 16)
        
        self.connect(src,b_to_syms,mult,add,repeater,fsk_f,attenuator,speaker)
        self.connect(fsk_f,dst)
        
def main():


    global CentreFreq,DataRate,RepeatTime
    datarate = int(raw_input("Enter datarate with which we want to transmit  ")) 
    centrefreq = int(raw_input("Enter centre frequency with which we want to transmit  "))
    packts= int(raw_input("Enter no. of packets to transmit ")) 
    CentreFreq=centrefreq
    DataRate=datarate
    RepeatTime=AudioRate/DataRate
    print RepeatTime
    
    
    fg = fsk_graph()
    
    fg.start()                       # start flow graph'
    
    try:
	i=0

        while i<=packts:

            #message = raw_input("Enter a message to transmit (Ctrl-D to exit): ") 
            message=str(i)
	    msg64 = base64.standard_b64encode(message)
            print "Encoding message= %s to base64= %s" % (message,msg64)
	    
	    print i
    	    i=i + 1
            payload = clock_sync+sync+encode_6b_8b(msg64)+stop_sync
	  
            pkt = struct.pack('%iB' % (len(payload)),*payload)
            
            msg = gr.message_from_string(pkt)
    	    
            fg.src.msgq().insert_tail(msg)
	    Tx_Dur=((((((len(msg64)-1.0)/4.0)*4.0)+16.0)*8.0)/DataRate)
	    print Tx_Dur
	    time.sleep(Tx_Dur)
	
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
