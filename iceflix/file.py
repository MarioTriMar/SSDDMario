#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Ice
import sys

Ice.loadSlice('iceflix/iceflix.ice')
import IceFlix

class FileService(IceFlix.FileService):
    def openFile():
        return 0


class file(Ice.Application):
    def __init__(self):
        self.servant=FileService()
    def run(self, argv):
        proxy1 = self.communicator().stringToProxy(argv[1])
        catalogPrx=IceFlix.MediaCatalogPrx.checkedCast(proxy1)
        if not catalogPrx:
            raise RuntimeError('Invalid proxy')

        broker=self.communicator()
        adapter=broker.createObjectAdapterWithEndpoints("fileAdapter","tcp")
        proxy=adapter.addWithUUID(self.servant)
        filePrx=IceFlix.FileServicePrx.checkedCast(proxy)
        catalogPrx.newMedia("112",filePrx)
        
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 1
sys.exit(file().main(sys.argv))