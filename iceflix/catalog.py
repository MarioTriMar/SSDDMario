#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
import json
import threading
Ice.loadSlice("iceflix.ice")
import IceFlix


'''
Threading -> libreria para paralelismo.
Manejo del announce cada 25 segundos
'''

"""MÉTODOS AUXILIARES"""

def save_json(fichero, dic):
    with open(fichero, "w") as f:
        json.dump(dic, f)


def read_json(fichero):
    dic={}
    
    with open(fichero, "r") as f:
        dic=json.load(f)
    return dic
    

def announce_catalog(principalPrx ,catalog, idCatalog):
        time = threading.Timer(25,announce_catalog,[catalog, idCatalog])
        principalPrx.announce(catalog, idCatalog)
        time.start()


def add_tags(mediaId, tags, userToken, mediasTags):
    if userToken in mediasTags:
        if mediaId in mediasTags[userToken]:
            for tag in tags:
                if tag not in mediasTags[userToken][mediaId]:
                    mediasTags[userToken][mediaId].append(tags)
        if mediaId not in mediasTags[userToken]:
            mediasTags[userToken][mediaId]=tags
    if userToken not in mediasTags:
        dicAux={}
        dicAux[mediaId]=tags
        mediasTags[userToken]=dicAux
    save_json("mediaTags.json", mediasTags)


def remove_tags(mediaId, tags, userToken, mediasTags):
    for tag in tags:
        if userToken in mediasTags and mediaId in mediasTags[userToken] and tag in mediasTags[userToken][mediaId]:
            listaTags=mediasTags[userToken][mediaId]
            index=listaTags.index(tag)
            del mediasTags[userToken][mediaId][index]
            save_json("mediaTags.json", mediasTags)
    

"""SIRVIENTE CATALOG"""

class MediaCatalog(IceFlix.MediaCatalog):
    def __init__(self):
        self.mediasFile={}
        self.mediasProvider={}
        self.principal=None
        self.mediasName=read_json("mediaName.json")
        self.mediasTags=read_json("mediaTags.json")


    def newMedia(self, mediaId, provider, current=None):
        if mediaId not in self.mediasName:
            self.mediasName[mediaId]=mediaId
        if mediaId in self.mediasProvider:
            self.mediasProvider.append(provider)
        if mediaId not in self.mediasProvider:
            self.mediasProvider[mediaId]=[provider]
        save_json("mediaName.json", self.mediasName)


    def removeMedia(self, mediaId, provider, current=None):
        if mediaId in self.mediasProvider:
            if provider in self.mediasProvider[mediaId]:
                listProviders= self.mediasProvider[mediaId]
                indexPro=listProviders.index(provider)
                del self.mediasProvider[mediaId][indexPro]


    def renameTile(self, mediaId, name, adminToken, current=None):
        authenticator=self.principal.getAuthenticator()
        admin = authenticator.isAdmin(adminToken)
        if admin == False:
            raise IceFlix.Unauthorized()
        if mediaId in self.mediasName:
            self.mediasName[mediaId]=name
        else:
            raise IceFlix.WrongMediaId()
        save_json("mediaName.json", self.mediasName)


    def getTile(self, mediaId, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized == False:
            raise IceFlix.Unauthorized()
        
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId()
        if mediaId not in self.mediasProvider:
            raise IceFlix.TemporaryUnavailable()
        listProviders=self.mediasProvider[mediaId]
        if listProviders:
            provider=listProviders[0]
        else:
            raise IceFlix.TemporaryUnavailable()
        if mediaId not in self.mediasTags[userToken]:
            raise IceFlix.WrongMediaId()
        name=self.mediasName[mediaId]
        tags=self.mediasTags[userToken][mediaId]
        mediaInfo=IceFlix.MediaInfo(name, tags)
        media=IceFlix.Media(mediaId, provider, mediaInfo)
        return media


    def getTilesByName(self, name, exact, current=None):
        medias=self.mediasName.keys()
        listaMedias=[]
        if exact==True:
            for media in medias:
                if name==self.mediasName[media]:
                    listaMedias.append(media)
        else:
            for media in medias:
                if name in self.mediasName[media]:
                    listaMedias.append(media)
        return listaMedias


    def getTilesByTags(self, tags, includeAllTags, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized == False:
            raise IceFlix.Unauthorized()
        listaMediasTags=[]
        if includeAllTags==False:
            if userToken in self.mediasTags:
                listaMediasUser=self.mediasTags[userToken].keys()
                for tag in tags:
                    for media in listaMediasUser:
                        if tag in self.mediasTags[userToken][media] and media not in listaMediasTags:
                            listaMediasTags.append(media)
        else:
            if userToken in self.mediasTags:
                listaMediasUser=self.mediasTags[userToken].keys()
                for media in listaMediasUser:
                    listaTagsMedia=self.mediasTags[userToken][media]
                    if(all(x in listaTagsMedia for x in tags)):
                        listaMediasTags.append(media)
        return listaMediasTags


    def addTags(self, mediaId, tags, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized == False:
            raise IceFlix.Unauthorized()
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId()
        add_tags(mediaId, tags, userToken, self.mediasTags)


    def removeTags(self, mediaId, tags, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized == False:
            raise IceFlix.Unauthorized()
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId()
        remove_tags(mediaId, tags, userToken, self.mediasTags)


"""CLASE PRINCIPAL"""

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
        print(proxy)
        
        '''Principal proxy'''
        proxyPrincipal = self.communicator().stringToProxy(argv[1])
        principalPrx = IceFlix.MainPrx.checkedCast(proxyPrincipal)
        if not principalPrx:
            raise RuntimeError('Invalid proxy')
        principalPrx.newService(proxy, proxy.ice_getIdentity().name)

        self.servant.principal=principalPrx
        '''Announce Handler'''
        timer = threading.Timer(25,announce_catalog,[principalPrx,proxy,proxy.ice_getIdentity().name])
        timer.start()

        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 1

if __name__ == '__main__':
    catalog=Catalog()
    if sys.argv != 2:
        print("Para lanzar ./catalog.py <mainProxy>")
    else:
        sys.exit(catalog.main(sys.argv))