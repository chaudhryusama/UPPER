#!/usr/bin/env python
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer


class MyFuncs:
  def add(self, x, y):
    return x + y

server = SimpleXMLRPCServer((localhost,8000))
server.register_instance(MyFuncs())
# The server will run until you hit Control-C or the like

