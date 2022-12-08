#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Ice
import sys

Ice.loadSlice('iceflix/iceflix.ice')
import IceFlix

class Main(IceFlix.Main):
    def getCatalog():
        return 0
    def newService(self, service, serviceId, current=None):
        print("newService")
        print (service)
    def announce(self, service, serviceId, current=None):
        print("announce")
        print(service)
    def getAuthenticator(self):
        return 0
    def getFileService(self):
        return 0

class file(Ice.Application):
    def __init__(self):
        self.servant=Main()
    def run(self, argv):
        #Catalog proxy
        broker = self.communicator()
        adapter = broker.createObjectAdapterWithEndpoints("mainAdapter", "tcp")
        proxy=adapter.addWithUUID(self.servant)
        adapter.activate()
        print(proxy)
        

       
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 1
sys.exit(file().main(sys.argv))