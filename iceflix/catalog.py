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
import IceStorm

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
    time = threading.Timer(8,announce_catalog,[principal_prx, catalog, id_catalog])
    principal_prx.announce(catalog, id_catalog)
    time.start()


def add_tags(media_id, tags, name, medias_tags):
    if name in medias_tags:
        if media_id in medias_tags[name]:
            for tag in tags:
                if tag not in medias_tags[name][media_id]:
                    medias_tags[name][media_id].append(tags)
        if media_id not in medias_tags[name]:
            medias_tags[name][media_id]=tags
    if name not in medias_tags:
        dicAux={}
        dicAux[media_id]=tags
        medias_tags[name]=dicAux
    save_json("iceflix/mediaTags.json", medias_tags)


def remove_tags(media_id, tags, name, medias_tags):
    for tag in tags:
        if name in medias_tags and media_id in medias_tags[name] and tag in medias_tags[name][media_id]:
            lista_tags=medias_tags[name][media_id]
            index=lista_tags.index(tag)
            del medias_tags[name][media_id][index]
            save_json("iceflix/mediaTags.json", medias_tags)
    
#SIRVIENTE CATALOG

class MediaCatalog(IceFlix.MediaCatalog):
    def __init__(self):
        self.mediasProvider={}
        self.principal=None
        self.catalogUpdates=None
        self.serviceId=None
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
            raise IceFlix.WrongMediaId(mediaId)
        save_json("iceflix/mediaName.json", self.mediasName)


    def getTile(self, mediaId, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized is False:
            raise IceFlix.Unauthorized()
        name=authenticator.whois(userToken)
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId(mediaId)
        if mediaId not in self.mediasProvider:
            raise IceFlix.TemporaryUnavailable()
        listProviders=self.mediasProvider[mediaId]
        if listProviders:
            provider=listProviders[0]
        else:
            provider=None
        if name not in self.mediasTags or mediaId not in self.mediasTags[name]:
            raise IceFlix.WrongMediaId(mediaId)
        name=self.mediasName[mediaId]
        tags=self.mediasTags[name][mediaId]

        mediaInfo=IceFlix.MediaInfo()
        media=IceFlix.Media()

        mediaInfo.name=name
        mediaInfo.tags=tags

        media.mediaId=mediaId
        media.provider=provider
        media.info=mediaInfo

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
        name=authenticator.whois(userToken)
        listaMediasTags=[]
        if includeAllTags is False:
            if name in self.mediasTags:
                listaMediasUser=self.mediasTags[name].keys()
                for tag in tags:
                    for media in listaMediasUser:
                        if tag in self.mediasTags[name][media] and media not in listaMediasTags:
                            listaMediasTags.append(media)
        else:
            if name in self.mediasTags:
                listaMediasUser=self.mediasTags[name].keys()
                for media in listaMediasUser:
                    listaTagsMedia=self.mediasTags[name][media]
                    if(all(x in listaTagsMedia for x in tags)):
                        listaMediasTags.append(media)
        return listaMediasTags


    def addTags(self, mediaId, tags, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized is False:
            raise IceFlix.Unauthorized()
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId(mediaId)
        name=authenticator.whois(userToken)
        add_tags(mediaId, tags, name, self.mediasTags)


    def removeTags(self, mediaId, tags, userToken, current=None):
        authenticator=self.principal.getAuthenticator()
        authorized = authenticator.isAuthorized(userToken)
        if authorized is False:
            raise IceFlix.Unauthorized() 
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId(mediaId)
        name=authenticator.whois(userToken)
        remove_tags(mediaId, tags, name, self.mediasTags)


class Announcement(IceFlix.Announcement):
    def __init__(self):
        self.announcement=None
    def announce(service, serviceId, current=None):
        """TODO"""

class FileAvailabilityAnnounce(IceFlix.FileAvailabilityAnnounce):
    def announceFiles(mediaIds, serviceId, current=None):
        """TODO"""

class CatalogUpdate(IceFlix.CatalogUpdate):
    def renameTile(mediaId, newName, serviceId, current=None):
        """TODO"""
    def addTags(mediaId, user, tags, serviceId, current=None):
        """TODO"""
    def removeTags(mediaId, user, tags, current=None):
        """TODO"""
#CLASE PRINCIPAL

class Catalog(Ice.Application):
    def __init__(self):
        super().__init__()
        self.servant=MediaCatalog()
        self.servantFileAvailability=FileAvailabilityAnnounce()
        self.servantCatalogUpdates=CatalogUpdate()
        self.servantAnnouncement=Announcement()
    def run(self, argv):
        
        broker = self.communicator()
        adapter = broker.createObjectAdapterWithEndpoints("catalogAdapter", "tcp")
        my_proxy=adapter.addWithUUID(self.servant)
        proxy_file_availability=adapter.addWithUUID(self.servantFileAvailability)
        proxy_catalog_updates=adapter.addWithUUID(self.servantCatalogUpdates)
        proxy_announcement=adapter.addWithUUID(self.servantAnnouncement)
        adapter.activate()
        
        proxyTopic=self.communicator().stringToProxy("IceStormAdmin.TopicManager.Default")
        topicManager=IceStorm.TopicManagerPrx.checkedCast(proxyTopic)
        try:
            topic_announcements=topicManager.retrieve("Announcements")  
        except IceStorm.NoSuchTopic:
            topic_announcements=topicManager.create("Announcements")  
        
        try:
            topic_catalogUpdates=topicManager.retrieve("CatalogUpdates")  
        except IceStorm.NoSuchTopic:
            topic_catalogUpdates=topicManager.create("CatalogUpdate")  
        
        try:
            topic_fileAvailability=topicManager.retrieve("FileAvailabilityAnnounce")  
        except IceStorm.NoSuchTopic:
            topic_fileAvailability=topicManager.create("FileAvailabilityAnnounce")  
        
        topic_announcements.subscribeAndGetPublisher({}, proxy_announcement)
        topic_catalogUpdates.subscribeAndGetPublisher({}, proxy_catalog_updates)
        topic_fileAvailability.subscribeAndGetPublisher({}, proxy_file_availability)

        announcement_proxy=topic_announcements.getPublisher()
        announcement=IceFlix.AnnouncementPrx.uncheckedCast(announcement_proxy)

        catalogUpdates_proxy=topic_catalogUpdates.getPublisher()
        catalogUpdate=IceFlix.CatalogUpdatePrx.uncheckedCast(catalogUpdates_proxy)

        self.servant.serviceId=str(my_proxy.ice_getIdentity().name)
        self.servant.catalogUpdates=catalogUpdate
        self.servantAnnouncement.announcement=announcement
        timer=threading.Timer(8,announce_catalog,[announcement,my_proxy,str(my_proxy.ice_getIdentity().name)])
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
        