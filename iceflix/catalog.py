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
Ice.loadSlice("iceflix.ice")
import IceFlix

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

"""
Tutoría
Cuando me anuncio envio proxy o casteo?
Preguntar por si el removeMedia debe lanzar excepcion
Desarrollar flujo
Preguntar por los parametros del resto de metodos del sirviente
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
    save_json("mediaTags.json", dic)

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
            save_json("mediaTags.json", dic)
    

class MediaCatalog(IceFlix.MediaCatalog):
    def __init__(self):
        self.mediasFile={}
        self.mediasProvider={}
        self.principal=None

    def newMedia(self, mediaId, provider, current=None):
        if mediaId not in self.mediasFile:
            self.mediasFile[mediaId] = mediaId
            dicAux = read_json("mediaFile.json")
            dicAux[mediaId]=mediaId
            save_json("mediaFile.json", dicAux)
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
            raise IceFlix.WrongMediaId()
        """Preguntar si hay que lanzar excepcion"""


    def renameTile(self, mediaId, name, adminToken, current=None):
        authenticator=self.principal.getAuthenticator()
        admin = authenticator.isAdmin(adminToken)
        if admin == False:
            raise IceFlix.Unauthorized
        
        if mediaId in self.mediasFile:
            self.mediasFile[mediaId]=name
            save_json("mediaFile.json", self.mediasFile)
        else:
            raise IceFlix.WrongMediaId()
            
    def getTile(self, mediaId, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized == False:
            raise IceFlix.Unauthorized
        dicName=read_json("mediaFile.json")
        if mediaId not in dicName:
            raise IceFlix.WrongMediaId
        listProviders=self.mediasProvider[mediaId]
        if listProviders:
            provider=listProviders[0]
        else:
            raise IceFlix.TemporaryUnavailable
        
        
        dicTags=read_json("mediaTags.json")
        name=dicName[mediaId]
        tags=dicTags[userToken][mediaId]
        mediaInfo=IceFlix.MediaInfo(name, tags)
        media=IceFlix.Media(mediaId, provider, mediaInfo)
        return media
        
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
            raise IceFlix.Unauthorized

        dic=read_json("mediaFile.json")
        if mediaId not in dic:
            raise IceFlix.WrongMediaId
        add_tags(mediaId, tags, userToken)



    def removeTags(self, mediaId, tags, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized == False:
            raise IceFlix.Unauthorized
        dic=read_json("mediaFile.json")
        if mediaId not in dic:
            raise IceFlix.WrongMediaId
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
        print(proxy)
        
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