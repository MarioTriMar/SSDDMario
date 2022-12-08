#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Ice
import sys

Ice.loadSlice('iceflix/iceflix.ice')
import IceFlix

class Authenticator(IceFlix.Authenticator):
    def whois(self, userToken, current=None):
        return "pepe"


class authenticator(Ice.Application):
    def __init__(self):
        self.servant=Authenticator()
    def run(self, argv):

        broker=self.communicator()
        adapter=broker.createObjectAdapterWithEndpoints("authAdapter","tcp")
        proxy=adapter.addWithUUID(self.servant)
        print(proxy)
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 1
sys.exit(authenticator().main(sys.argv))