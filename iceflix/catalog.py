#!/usr/bin/python3
# -*- coding: utf-8 -*-


# pylint: disable=W0613
# pylint: disable=C0103
# pylint: disable=C0116
# pylint: disable=C0115

# pylint: disable=C0301
# pylint: disable=C0303
# pylint: disable=C0413
# pylint: disable=E0401


import sys
import threading
import json
import Ice

Ice.loadSlice('iceflix/iceflix.ice')
import IceFlix



#Threading -> libreria para paralelismo.
#Manejo del announce cada 25 segundos


#MÉTODOS AUXILIARES

def save_json(fichero, dic):
    with open(fichero, "w", encoding="utf8") as f:
        json.dump(dic, f)

def read_json(fichero):
    dic={}
    with open(fichero, "r", encoding="utf8") as f:
        dic=json.load(f)
    return dic

def announce_catalog(principal_prx ,catalog, id_catalog):
    time = threading.Timer(25,announce_catalog,[catalog, id_catalog])
    principal_prx.announce(catalog, id_catalog)
    time.start()


def add_tags(media_id, tags, user_token, medias_tags):
    if user_token in medias_tags:
        if media_id in medias_tags[user_token]:
            for tag in tags:
                if tag not in medias_tags[user_token][media_id]:
                    medias_tags[user_token][media_id].append(tags)
        if media_id not in medias_tags[user_token]:
            medias_tags[user_token][media_id]=tags
    if user_token not in medias_tags:
        dicAux={}
        dicAux[media_id]=tags
        medias_tags[user_token]=dicAux
    save_json("iceflix/mediaTags.json", medias_tags)


def remove_tags(media_id, tags, user_token, medias_tags):
    for tag in tags:
        if user_token in medias_tags and media_id in medias_tags[user_token] and tag in medias_tags[user_token][media_id]:
            lista_tags=medias_tags[user_token][media_id]
            index=lista_tags.index(tag)
            del medias_tags[user_token][media_id][index]
            save_json("iceflix/mediaTags.json", medias_tags)
    
#SIRVIENTE CATALOG

class MediaCatalog(IceFlix.MediaCatalog):
    def __init__(self):
        self.mediasProvider={}
        self.principal=None
        self.mediasName=read_json("iceflix/mediaName.json")
        self.mediasTags=read_json("iceflix/mediaTags.json")


    def newMedia(self, mediaId, provider, current=None):
        if mediaId not in self.mediasName:
            self.mediasName[mediaId]=mediaId
        if mediaId in self.mediasProvider:
            self.mediasProvider[mediaId].append(provider)
        if mediaId not in self.mediasProvider:
            self.mediasProvider[mediaId]=[provider]
        save_json("iceflix/mediaName.json", self.mediasName)
        print(self.mediasName)


    def removeMedia(self, mediaId, provider, current=None):
        if mediaId in self.mediasProvider:
            if provider in self.mediasProvider[mediaId]:
                listProviders= self.mediasProvider[mediaId]
                indexPro=listProviders.index(provider)
                del self.mediasProvider[mediaId][indexPro]


    def renameTile(self, mediaId, name, adminToken, current=None):
        authenticator=self.principal.getAuthenticator()
        admin = authenticator.isAdmin(adminToken)
        if admin is False:
            raise IceFlix.Unauthorized()
        if mediaId in self.mediasName:
            self.mediasName[mediaId]=name
        else:
            raise IceFlix.WrongMediaId()
        save_json("iceflix/mediaName.json", self.mediasName)


    def getTile(self, mediaId, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized is False:
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
        if exact is True:
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
        if authorized is False:
            raise IceFlix.Unauthorized()
        listaMediasTags=[]
        if includeAllTags is False:
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
        if authorized is False:
            raise IceFlix.Unauthorized()
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId()
        add_tags(mediaId, tags, userToken, self.mediasTags)


    def removeTags(self, mediaId, tags, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized is False:
            raise IceFlix.Unauthorized()
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId()
        remove_tags(mediaId, tags, userToken, self.mediasTags)


#CLASE PRINCIPAL

class Catalog(Ice.Application):
    def __init__(self):
        super().__init__()
        self.servant=MediaCatalog()

    def run(self, argv):
        #Catalog proxy
        broker = self.communicator()
        adapter = broker.createObjectAdapterWithEndpoints("catalogAdapter", "tcp")
        proxy=adapter.addWithUUID(self.servant)
        adapter.activate()
        
        
        #Principal proxy
        proxy_principal = self.communicator().propertyToProxy("MainProxy.Proxy")
        
        
        principal_prx = IceFlix.MainPrx.checkedCast(proxy_principal)
        if not principal_prx:
            raise RuntimeError('Invalid proxy')
        principal_prx.newService(proxy, proxy.ice_getIdentity().name)

        self.servant.principal=principal_prx
        #Announce Handler
        timer = threading.Timer(25,announce_catalog,[principal_prx,proxy,proxy.ice_getIdentity().name])
        timer.start()
        
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 1

if __name__ == '__main__':
    catalog=Catalog()
    if len(sys.argv) != 2:
        print("Para lanzar ./catalog.py <config>")
    else:
        sys.exit(catalog.main(sys.argv))
        