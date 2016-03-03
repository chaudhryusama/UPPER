#!/usr/bin/env python
# Client code

import xmlrpclib
import time
from time import sleep
i=0
s = xmlrpclib.ServerProxy("http://localhost:8000/")
while 1:
	
	
	#print s.recv_data()
	msg1="nia"
	 
	print s.send_data(msg1)
	#time.sleep(2) 
#print s.send_tone("tone")
#print "tone sent"

#print s.recv_data()

#s.recv_tone()





