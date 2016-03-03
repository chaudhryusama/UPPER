#!/usr/bin/env python
# Title    : fsk_receive.py
# Function : online receiving of packets
# Author   : Andrew Goodney

# 14k and 16k

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


#--------------------------------------   global variables------------------------
audio_rate=48000
filename=[]
filename2=[]
RepeatTime=960
BandPass=1500
BandStop=1800
Range=1.0
CentreFrequency=14
Specification='without preamp'
DataRate=100
#f2=open('/home/sysnet/Desktop/gnuradio-sir/final-codes/tone-data/results/recvd-pattern.txt','a')
#---------------------------------------------------------------------------------
class Count:
	total=0
	successful=0
	error=0



def message_callback(payload):
    error = False
    message64 = ""
    Count.total= Count.total+1
    print Count.total
    #print "Message Callback fired!"
    #print "Message length: ",len(payload)
    for byte in payload:
        try:
            message64 = message64 + map_8b_6b[ord(byte)]
        except KeyError:
            message64 = message64 + '[%i]' % ord(byte)
            error = True
    
    #print "Received base64 message= %s" % (message64)
    if error == False:
        print "Decoded to: %s" % base64.standard_b64decode(message64)
	Count.successful= Count.successful+1
    else:
	Count.error=Count.error+1
        print "Error was detected.",Count.error
    #print "Message Callback fired!"
    #print "Hit Ctrl-D to exit."

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
	    #ok, payload = packet_utils.unmake_packet(msg.to_string(), int(msg.arg1()))  # pasted from pkt.py
	    payload = msg.to_string()
	    #print payload
	    if self.callback:
	          self.callback(payload)
		
    


# Main Graph
class fsk_graph(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)
        
        self.rcvd_pktq = gr.msg_queue()
        audio_rate = 48000
         
        #src = gr.wavfile_source("./c", False)
        src = audio.source (audio_rate,"plughw:0,0")
	mult = gr.multiply_const_ff(10)   # multiply
	raw_wave = gr.wavfile_sink(filename, 1, audio_rate,16)
	raw_wave1 = gr.wavfile_sink(filename2, 1, audio_rate,16)
        #raw_wave2 = gr.wavfile_sink("raw1.wav", 1, audio_rate,16)
        fsk_c = gr.hilbert_fc((audio_rate/300)+1)
	

	


        bp_coeff = gr.firdes.band_pass(1,audio_rate,BandPass,BandStop,100)
	#bp_coeff = gr.firdes.band_pass(1,audio_rate,,17500,100)
        bpf = gr.fir_filter_fff(1,bp_coeff)
        
        quad_demod = gr.quadrature_demod_cf(1)#originally 1
        
        #speaker = audio.sink(audio_rate, "plughw:0,0");
        
        hpf_coeff = gr.firdes.high_pass(10, audio_rate, 10, 5)
        #dc_block = gr.fir_filter_fff (1, hpf_coeff)
        dc_block = gr.add_const_ff(-2.225)
        mm = gr.clock_recovery_mm_ff(RepeatTime,0.000625,0.5,0.01,0.1)
        
        slicer = gr.binary_slicer_fb()
        
        sync_corr = gr.correlate_access_code_bb("0100011101111000",0)
        
        file_sink = gr.file_sink(1, "decoded-bits.dat")
        sink = goodney.sink2(self.rcvd_pktq)
        #sink = gr.framer_sink_1(self.rcvd_pktq)
        self.connect(bpf,raw_wave1)
	self.connect(src,raw_wave)
        self.connect(src,bpf,fsk_c,quad_demod,dc_block,mm,slicer,sync_corr,sink)
        #self.connect(src,bpf,mm,fsk_c,quad_demod,dc_block,slicer,file_sink)
        #self.connect(bpf,raw_wave2)
	
        self.watcher = _queue_watcher_thread(self.rcvd_pktq, message_callback)
        
def main():
    
	
   # f2=open('/home/sysnet/Desktop/gnuradio-sir/final-codes/tone-data/results/recvd-pattern.txt','a')
    length=float(raw_input("enter length for the experiment in meters: "))
    datarate=int(raw_input("enter datarate for the experiment in bps: "))
    CentreFrequency=int(raw_input("enter the centre frequency used for experiments "))
    Specification=raw_input("enter any modification used in experiments ")
    global filename,filename2, RepeatTime, BandPass, BandStop,DataRate, Range
    
    BandPass= CentreFrequency-1500
    BandStop= CentreFrequency+1500
    DataRate=datarate
    Range=length
    RepeatTime=audio_rate/DataRate
    print RepeatTime
    filename = '{0}-{1}-{2}'.format(Range,CentreFrequency,Specification) 
    filename2= '{0}-bps'.format(filename)
   
    #TX_DUR=(((((len(message)-1)/4)*4)+16)*8)/DataRate

    fg = fsk_graph()

    fg.start()                       # start flow graph

    try:
        print "Hit Ctrl-D to exit."
        while True:
            raw_input("")
    except EOFError:
        print "\nExiting."
	f.close()
	#f2.close()
        #fg.wait()

# Main python entry
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
	f=open('packets-recvd.txt','a')
	
	WritenData='\n {0}\t \t   {1}\t \t   {2}\t \t   {3}\t \t   {4}\t \t	{5}'.format(Count.total,Count.successful,Count.error,Range,DataRate,filename)	
	
	f.write(WritenData)
	f.close()
	#f2.close()
        pass
