#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Ice
import sys

Ice.loadSlice('iceflix/iceflix.ice')
import IceFlix


class client(Ice.Application):
    def run(self, argv):
        proxy1 = self.communicator().stringToProxy(argv[1])
        catalogPrx=IceFlix.MediaCatalogPrx.checkedCast(proxy1)
        if not catalogPrx:
            raise RuntimeError('Invalid proxy')
        """
        catalogPrx.renameTile("3","spiderman", "awdw")
        
        
        catalogPrx.addTags("31", ["miedo", "accion"], "pepe")
        
        print(catalogPrx.getTile("3","pepe"))
        catalogPrx.removeTags("3", ["miedo"], "pepe")
        """
        
        return 1
sys.exit(client().main(sys.argv))