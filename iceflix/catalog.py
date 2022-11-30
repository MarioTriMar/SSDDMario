#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
import json
'''
Threading -> libreria para paralelismo.
Manejo del announce cada 25 segundos
'''
import threading
Ice.loadSlice('iceflix.ice')
import iceflix

"""
getAuthenticator devuelve un proxy casteado
Entonces cuando se hace un removeMedia lo que se quita es solo el fileservice
Cuando me llegue un newService nuevo guardarlo en memeria con nombre=idMedia
Para escribir en un json:
    d= {
        "juan": {"accion: ["peli1", "peli2]}
    }
    with open("tag_db.json", "w") as f:
        json.dump(d,f) //f es fichero
    with open("tag_db.json", "r) as f:
        d = json.load(d)
"""




def save_json(fichero, dic):
    with open(fichero, "w") as f:
        json.dump(dic, f)

def read_json(fichero):
    dic={}
    try:
        with open(fichero, "r") as f:
            dic=json.load(f)
            return dic
    except FileNotFoundError:
        return dic

def add_tags(mediaId, tags, userToken):
    dic={}
    try:
        with open("mediaTags.json", "r") as f:
            dic=json.load(f)
    except FileNotFoundError:
        dic={}
    
    if userToken in dic:
        if mediaId in dic[userToken]:
           dic[userToken][mediaId].append(tags)
        if mediaId not in dic[userToken]:
            dic[userToken][mediaId]=[tags]
    if userToken not in dic:
        dicAux={}
        dicAux[mediaId]=[tags]
        dic[userToken]=dicAux
    save_json("media.json", dic)

def remove_tags(mediaId, tags, userToken):
    dic={}
    try:
        with open("mediaTags.json", "r") as f:
            dic=json.load(f)
    except FileNotFoundError:
        dic={} 
    for tag in tags:
        if tag in dic[userToken][mediaId]:
            listaTags=dic[userToken][mediaId]
            index=listaTags.index(tag)
            del dic[userToken][mediaId][index]
            save_json("media.json", dic)
    

class MediaCatalog(iceflix.MediaCatalog):
    def __init__(self):
        self.mediasFile={}
        self.mediasProvider={}
        """Preguntar por estructuras *"""
        self.mediaInfo = iceflix.MediaInfo()
        self.media = iceflix.Media()
        """Preguntar por como obtener el autenticator"""
        self.principal=None

    def newMedia(self, mediaId, provider, current=None):
        if mediaId not in self.mediasFile:
            self.mediasFile[mediaId] = mediaId
            save_json("mediaFile.json", self.mediasFile)
        if mediaId in self.mediasProvider:
            self.mediasProvider.append(provider)
        if mediaId not in self.mediasProvider:
            self.mediasFile[mediaId]=[provider]
        
        


    def removeMedia(self, mediaId, provider, current=None):
        
        if mediaId in self.mediasProvider:
            if provider in self.mediasProvider[mediaId]:
                listProviders= self.mediasProvider[mediaId]
                index=listProviders.index(provider)
                del self.mediasProvider[mediaId][index]
        else:
            raise iceflix.WrongMediaId()
        """Preguntar si hay que lanzar excepcion"""


    def renameTile(self, mediaId, name, adminToken, current=None):
        authenticator=self.principal.getAuthenticator()
        admin = authenticator.isAdmin(adminToken)
        if admin == False:
            raise iceflix.Unauthorized
        else:
            self.mediasFile[mediaId]=name
            save_json("mediaFile.json", self.mediasFile)
            
    def getTile(self, mediaId, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized == False:
            raise iceflix.Unauthorized
        """TODO"""
    def getTilesByName(self, name, exact, current=None):
        """TODO"""
    def getTilesByTags(self, tags, includeAllTags, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized == False:
            raise iceflix.Unauthorized
        """TODO"""


    def addTags(self, mediaId, tags, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized == False:
            raise iceflix.Unauthorized

        dic=read_json("mediaFile.json")
        if mediaId not in dic:
            raise iceflix.WrongMediaId
        add_tags(mediaId, tags, userToken)



    def removeTags(self, mediaId, tags, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized == False:
            raise iceflix.Unauthorized
        dic=read_json("mediaFile.json")
        if mediaId not in dic:
            raise iceflix.WrongMediaId
        remove_tags(mediaId, tags, userToken)

        

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
        
        
        '''Principal proxy'''
        proxyPrincipal = self.communicator().stringToProxy(argv[1])
        principalPrx = iceflix.MainPrx.checkedCast(proxyPrincipal)
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
    sys.exit(catalog.main(sys.argv))