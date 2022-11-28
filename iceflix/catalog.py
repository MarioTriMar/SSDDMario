#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
'''
Threading libreria para paralelismo.
Manejo del announce cada 25 segundos
'''
import threading
Ice.loadSlice('iceflix.ice')
import iceflix

class MediaCatalog(iceflix.MediaCatalog):
    def __init__(self):
        self.mediasFile={}
    def newMedia(self, mediaId, provider, current=None):
        self.mediasFile[mediaId] = provider
    def removeMedia(self, mediaId, provider, current=None):
        if mediaId in self.mediasFile:
            del self.mediasFile[mediaId]
        else:
            raise iceflix.WrongMediaId()
        """Preguntar si hay que lanzar excepcion"""
    def renameTile(self, mediaId, name, adminToken, current=None):
        """TODO"""
    def getTile(self, mediaId, userToken, current=None):
        """TODO"""
    def getTilesByName(self, name, exact, current=None):
        """TODO"""
    def getTilesByTags(self, tags, includeAllTags, userToken, current=None):
        """TODO"""
    def addTags(self, mediaId, tags, userToken, current=None):
        """TODO"""
    def removeTags(self, mediaId, tags, userToken, current=None):
        """TODO"""

def announceCatalog(principalPrx ,catalog, idCatalog):
        time = threading.Timer(25,announceCatalog,[catalog, idCatalog])
        principalPrx.announce(catalog, idCatalog)
        time.start()

class Catalog(Ice.Application):
    def __init__(self):
        super().__init__()
        self.servant=MediaCatalog()

    

    def run(self, argv):
        '''Catalog proxy'''
        broker = self.communicator()
        adapter = broker.createObjectAdapterWithEndpoints("catalogAdapter", "tcp")
        proxy=adapter.addWithUUID(self.servant)
        adapter.activate()
        """Preguntar si se accede así al diccionario de la clase Mediacatalog"""
        self.servant.mediasFile
        '''Principal proxy'''
        proxyPrincipal = self.communicator().stringToProxy(argv[1])
        principalPrx = iceflix.MainPrx.checkedCast(proxyPrincipal)
        if not principalPrx:
            raise RuntimeError('Invalid proxy')
        principalPrx.newService(proxy, proxy.ice_getIdentity().name)
        
        '''Announce Handler'''
        timer = threading.Timer(25,announceCatalog,[principalPrx,proxy,proxy.ice_getIdentity().name])
        timer.start()

        return 1

if __name__ == '__main__':
    catalog=Catalog()
    sys.exit(catalog.main(sys.argv))