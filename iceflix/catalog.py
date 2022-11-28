#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
'''
Threading -> libreria para paralelismo.
Manejo del announce cada 25 segundos
'''
import threading
Ice.loadSlice('iceflix.ice')
import iceflix

class MediaInfo(iceflix.MediaInfo):
    def __init__(self, name, tags):
        self.name=name
        self.tags=tags

class MediaCatalog(iceflix.MediaCatalog):
    def __init__(self):
        self.mediasFile={}
        """Preguntar por estructuras *"""
        self.mediaInfo = iceflix.MediaInfo()
        self.media = iceflix.Media()
        """Preguntar por como obtener el autenticator"""
        self.authenticator=None

    def newMedia(self, mediaId, provider, current=None):
        self.mediasFile[mediaId] = provider
    def removeMedia(self, mediaId, provider, current=None):
        if mediaId in self.mediasFile:
            del self.mediasFile[mediaId]
        else:
            raise iceflix.WrongMediaId()
        """Preguntar si hay que lanzar excepcion"""


    def renameTile(self, mediaId, name, adminToken, current=None):
        admin = self.authenticator.isAdmin(adminToken)
        if admin == False:
            raise iceflix.Unauthorized
        else:
            """TODO"""
    def getTile(self, mediaId, userToken, current=None):
        authorized = self.authenticator.isAuthorized(userToken)
        if authorized == False:
            raise iceflix.Unauthorized
        """TODO"""
    def getTilesByName(self, name, exact, current=None):
        """TODO"""
    def getTilesByTags(self, tags, includeAllTags, userToken, current=None):
        authorized = self.authenticator.isAuthorized(userToken)
        if authorized == False:
            raise iceflix.Unauthorized
        """TODO"""
    def addTags(self, mediaId, tags, userToken, current=None):
        authorized = self.authenticator.isAuthorized(userToken)
        if authorized == False:
            raise iceflix.Unauthorized
        """TODO"""
    def removeTags(self, mediaId, tags, userToken, current=None):
        authorized = self.authenticator.isAuthorized(userToken)
        if authorized == False:
            raise iceflix.Unauthorized
        """TODO"""

def announce_catalog(principalPrx ,catalog, idCatalog):
        time = threading.Timer(25,announce_catalog,[catalog, idCatalog])
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
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        """Preguntar si se accede así al diccionario de la clase Mediacatalog"""
        self.servant.mediasFile
        '''Principal proxy'''
        proxyPrincipal = self.communicator().stringToProxy(argv[1])
        principalPrx = iceflix.MainPrx.checkedCast(proxyPrincipal)
        if not principalPrx:
            raise RuntimeError('Invalid proxy')
        principalPrx.newService(proxy, proxy.ice_getIdentity().name)
        """Preguntar si se pasa así el autenticator"""
        self.servant.authenticator=principalPrx.getAuthenticator()
        '''Announce Handler'''
        timer = threading.Timer(25,announce_catalog,[principalPrx,proxy,proxy.ice_getIdentity().name])
        timer.start()

        return 1

if __name__ == '__main__':
    catalog=Catalog()
    sys.exit(catalog.main(sys.argv))