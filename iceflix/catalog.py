#!/usr/bin/python3
# -*- coding: utf-8 -*-

#DISABLES ACLARADOS EN EL README
#pylint: disable=C0103
#pylint: disable=C0303
#pylint: disable=C0301
#pylint: disable=W0613
#pylint: disable=E1101

import sys
import threading
import os
import random
import json
import Ice
import IceStorm

Ice.loadSlice('iceflix/iceflix.ice')
import IceFlix


#MÉTODOS AUXILIARES

def save_json(fichero, dic):
    """This method saves the diccionary into the json file"""
    with open(fichero, "w", encoding="utf8") as f:
        json.dump(dic, f)

def read_json(fichero):
    """This method returns the diccionary of a json file"""
    dic={}
    with open(fichero, "r", encoding="utf8") as f:
        dic=json.load(f)
    return dic

def announce_catalog(announcement ,catalog, id_catalog):
    """This method is on charge of the continous announcement"""
    time = threading.Timer(8,announce_catalog,[announcement, catalog, id_catalog])
    announcement.announce(catalog, id_catalog)
    time.start()

def arranque(mediaCatalog, announcement, my_proxy):
    """This method is on charge of the launching"""
    if mediaCatalog.main_services:
        print("A main service has been detected")
        if mediaCatalog.catalog_services:
            print("getAllDeltas has been executed because a catalog has been detected")
            catalogs=list(mediaCatalog.catalog_services.values())
            catalog=IceFlix.MediaCatalogPrx.checkedCast(catalogs[0])
            catalog.getAllDeltas()
        else:
            print("First catalog announced, don't need to update")
        announcement.announce(my_proxy, str(my_proxy.ice_getIdentity().name))
        timer=threading.Timer(8,announce_catalog,[announcement,my_proxy,str(my_proxy.ice_getIdentity().name)])
        timer.start()
    else:
        print("No main service available, program has been aborted")
        os._exit(os.EX_OK)
    
def timer_announce(serviceId, catalog, timers):
    """This method is on charge of deleting dead services"""
    timers[serviceId].cancel() 
    if serviceId in catalog.main_services.keys():
        print("The next main service has been deleted because it's stopped announcing:",serviceId)
        del catalog.main_services[serviceId]
    if serviceId in catalog.file_services.keys():
        print("The next file service has been deleted because it's stopedd announcing:",serviceId)
        del catalog.file_service[serviceId]
    if serviceId in catalog.catalog_services.keys():
        print("The next catalog service has been deleted because it's stopped announcing:",serviceId)
        del catalog.catalog_services[serviceId]
    del timers[serviceId]

def add_tags(media_id, tags, name, medias_tags):
    """This method is on charge of adding tags"""
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
    """This method is on charge of removing tags"""
    for tag in tags:
        if name in medias_tags and media_id in medias_tags[name] and tag in medias_tags[name][media_id]:
            lista_tags=medias_tags[name][media_id]
            index=lista_tags.index(tag)
            del medias_tags[name][media_id][index]
            save_json("iceflix/mediaTags.json", medias_tags)
    print(medias_tags[name])
    
#SIRVIENTE CATALOG
class MediaCatalog(IceFlix.MediaCatalog):
    """Class MediaCatalog"""
    def __init__(self):
        self.main_services={}
        self.catalog_services={}
        self.file_services={}

        self.mediasProvider={}
        
        self.catalogUpdates=None
        self.serviceId=None
        self.mediasName=read_json("iceflix/mediaName.json")
        self.mediasTags=read_json("iceflix/mediaTags.json")

    def renameTile(self, mediaId, name, adminToken, current=None):
        """renameTile MediaCatalog"""
        print("renameTile operation has been executed")
        main_service=random.choice(list(self.main_services.values()))
        main_service=IceFlix.MainPrx.checkedCast(main_service)
        authenticator=main_service.getAuthenticator()
        admin=authenticator.isAdmin(adminToken)
        if admin is False:
            raise IceFlix.Unauthorized()
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId(mediaId)
        self.catalogUpdates.renameTile(mediaId, name, self.serviceId)
        print(self.mediasName)

    def getTile(self, mediaId, userToken, current=None):
        """getTile MediaCatalog"""
        print("getTile has been executed")
        main_service=random.choice(list(self.main_services.values()))
        main_service=IceFlix.MainPrx.checkedCast(main_service)
        authenticator=main_service.getAuthenticator()
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
        mediaInfo=IceFlix.MediaInfo()
        media=IceFlix.Media()
        if name not in self.mediasTags or mediaId not in self.mediasTags[name]:
            mediaInfo.tags=None
        else:
            mediaInfo.tags=self.mediasTags[name][mediaId]
        mediaName=self.mediasName[mediaId]
        
        mediaInfo.name=mediaName

        media.mediaId=mediaId
        media.provider=provider
        media.info=mediaInfo

        return media

    def getTilesByName(self, name, exact, current=None):
        """getTilesByName MediaCatalog"""
        print("getTilesByName has been executed")
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
        """getTilesByTags MediaCatalog"""
        print("getTilesByTags has been executed")
        main_service=random.choice(list(self.main_services.values()))
        main_service=IceFlix.MainPrx.checkedCast(main_service)
        authenticator=main_service.getAuthenticator()
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
        """addTags MediaCatalog"""
        print("addTags operation has been executed")
        main_service=random.choice(list(self.main_services.values()))
        main_service=IceFlix.MainPrx.checkedCast(main_service)
        authenticator=main_service.getAuthenticator()

        authorized = authenticator.isAuthorized(userToken)
        if authorized is False:
            raise IceFlix.Unauthorized()
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId(mediaId)
        name=authenticator.whois(userToken)
        self.catalogUpdates.addTags(mediaId, name, tags, self.serviceId)
        print(self.mediasTags)
        
    def removeTags(self, mediaId, tags, userToken, current=None):
        """addTags MediaCatalog"""
        print("removeTags operation has been executed")
        main_service=random.choice(list(self.main_services.values()))
        main_service=IceFlix.MainPrx.checkedCast(main_service)
        authenticator=main_service.getAuthenticator()

        authorized = authenticator.isAuthorized(userToken)
        if authorized is False:
            raise IceFlix.Unauthorized()
        if mediaId not in self.mediasName:
            raise IceFlix.WrongMediaId(mediaId)
        name=authenticator.whois(userToken)
        self.catalogUpdates.removeTags(mediaId, name, tags, self.serviceId)
    def getAllDeltas(self, current=None):
        """getAllDeltas MediaCatalog"""
        print("renameTile Delta operation has been executed from a catalog needed to be update")
        for media in self.mediasName.keys():
            self.catalogUpdates.renameTile(media, self.mediasName[media], self.serviceId)
        print("addTags Delta operation has been executed from a catalog needed to be update")
        for user in self.mediasTags.keys():
            for media in self.mediasTags[user].keys():
                self.catalogUpdates.addTags(media, user, self.mediasTags[user][media], self.serviceId)



# SIRVIENTE ANNOUNCEMENT
class Announcement(IceFlix.Announcement):
    """Class Announcement"""
    def __init__(self):
        self.catalog=None
        self.main_timers={}
        self.catalog_timers={}
        self.file_timers={}
    def announce(self, service, serviceId, current=None):
        """announce Announcement"""
        if serviceId in self.catalog.main_services.keys():
            print("A main service has been reannounce:",serviceId)
            self.main_timers[serviceId].cancel()
            self.main_timers[serviceId]=threading.Timer(12, timer_announce, [serviceId, self.catalog, self.main_timers])
            self.main_timers[serviceId].start()
            return  
        if serviceId in self.catalog.catalog_services.keys():
            if serviceId!=self.catalog.serviceId:
               print("A catalog service has been reannounce:",serviceId)
            self.catalog_timers[serviceId].cancel()
            self.catalog_timers[serviceId]=threading.Timer(12, timer_announce, [serviceId, self.catalog, self.catalog_timers])
            self.catalog_timers[serviceId].start()
            return 
        if serviceId in self.catalog.file_services.keys():
            print("A file service has been reannounce:",serviceId)
            self.file_timers[serviceId].cancel()
            self.file_timers[serviceId]=threading.Timer(12, timer_announce, [serviceId, self.catalog, self.file_timers])
            self.file_timers[serviceId].start()
            return
        if service.ice_isA('::IceFlix::Main'):
            print("New main service has been announced:", serviceId)
            self.catalog.main_services[serviceId]=IceFlix.MainPrx.uncheckedCast(service)
            self.main_timers[serviceId]=threading.Timer(12, timer_announce, [serviceId, self.catalog, self.main_timers])
            self.main_timers[serviceId].start()
        if service.ice_isA('::IceFlix::MediaCatalog'):
            if serviceId!=self.catalog.serviceId:
                print("New catalog service has been announced:",serviceId)
            self.catalog.catalog_services[serviceId]=IceFlix.MediaCatalogPrx.uncheckedCast(service)
            self.catalog_timers[serviceId]=threading.Timer(12, timer_announce, [serviceId, self.catalog, self.catalog_timers])
            self.catalog_timers[serviceId].start()
        if service.ice_isA('::IceFlix::FileService'):
            print("New file service has been announced:",serviceId)
            self.catalog.file_services[serviceId]=IceFlix.FileServicePrx.uncheckedCast(service)
            self.file_timers[serviceId]=threading.Timer(12, timer_announce, [serviceId, self.catalog, self.file_timers])
            self.file_timers[serviceId].start()



#SIRVIENTE FILEAVAILABILITY
class FileAvailabilityAnnounce(IceFlix.FileAvailabilityAnnounce):
    """Class FileAvilabilityAnnounce"""
    def __init__(self):
        self.catalog=None
    def announceFiles(self, mediaIds, serviceId, current=None):
        """announceFiles FileAvailabilityAnnounce"""
        print("Medias from a file service has been received")
        print("IDS:",mediaIds)
        if serviceId in self.catalog.file_services.keys():
            for media in mediaIds:
                if media not in self.catalog.mediasName:
                    self.catalog.mediasName[media]=media
                if media in self.catalog.mediasProvider:
                    self.catalog.mediasProvider[media].append(self.catalog.file_services[serviceId])
                if media not in self.catalog.mediasProvider:
                    self.catalog.mediasProvider[media]=[self.catalog.file_services[serviceId]]
            save_json("iceflix/mediaName.json", self.catalog.mediasName)


#SIRVIENTE CATALOGUPDATE
class CatalogUpdate(IceFlix.CatalogUpdate):
    """Class CatalogUpdate"""
    def __init__(self):
        self.catalog=None
    def renameTile(self, mediaId, newName, serviceId, current=None):
        """renameTile CatalogUpdate"""
        if serviceId in self.catalog.catalog_services.keys():
            self.catalog.mediasName[mediaId]=newName
            if mediaId not in self.catalog.mediasProvider.keys():
                self.catalog.mediasProvider[mediaId]=None
        save_json("iceflix/mediaName.json", self.catalog.mediasName)
        if serviceId!=self.catalog.serviceId:
            print("Catalog Update renameTile")
            print(self.catalog.mediasName)
    def addTags(self, mediaId, user, tags, serviceId, current=None):
        """addTags CatalogUpdate"""
        if serviceId in self.catalog.catalog_services.keys():
            if mediaId not in self.catalog.mediasName.keys():
                self.catalog.mediasName[mediaId]=mediaId
            if mediaId not in self.catalog.mediasProvider.keys():
                self.catalog.mediasProvider[mediaId]=None
            add_tags(mediaId, tags, user, self.catalog.mediasTags)
        if serviceId!=self.catalog.serviceId:
            print("Catalog Update addTags")
            print(self.catalog.mediasTags)
    def removeTags(self, mediaId, user, tags, serviceId, current=None):
        """removeTags CatalogUpdate"""
        print("Catalog Update removeTags")
        if serviceId in self.catalog.catalog_services.keys():
            if mediaId not in self.catalog.mediasName.keys():
                self.catalog.mediasName[mediaId]=mediaId
            if mediaId not in self.catalog.mediasProvider.keys():
                self.catalog.mediasProvider[mediaId]=None
            remove_tags(mediaId, tags, user, self.catalog.mediasTags)

#CLASE PRINCIPAL
class Catalog(Ice.Application):
    """Class Catalog(main)"""
    def __init__(self):
        super().__init__()
        self.servant=MediaCatalog()
        self.servantFileAvailability=FileAvailabilityAnnounce()
        self.servantCatalogUpdates=CatalogUpdate()
        self.servantAnnouncement=Announcement()
    def run(self, args):
        broker = self.communicator()
        adapter = broker.createObjectAdapterWithEndpoints("catalogAdapter", "tcp")
        my_proxy=adapter.addWithUUID(self.servant)
        proxy_file_availability=adapter.addWithUUID(self.servantFileAvailability)
        proxy_catalog_updates=adapter.addWithUUID(self.servantCatalogUpdates)
        proxy_announcement=adapter.addWithUUID(self.servantAnnouncement)
        adapter.activate()
        
        proxyTopic=self.communicator().propertyToProxy("IceStormAdmin.TopicManager.Default")
        topicManager=IceStorm.TopicManagerPrx.checkedCast(proxyTopic)
        
        try:
            topic_announcements=topicManager.retrieve("Announcements")  
        except IceStorm.NoSuchTopic:
            topic_announcements=topicManager.create("Announcements")  
        
        try:
            topic_catalogUpdates=topicManager.retrieve("CatalogUpdates")  
        except IceStorm.NoSuchTopic:
            topic_catalogUpdates=topicManager.create("CatalogUpdates")  
        
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
        self.servantCatalogUpdates.catalog=self.servant
        self.servantAnnouncement.catalog=self.servant
        self.servantFileAvailability.catalog=self.servant
        self.servant.catalogUpdates=catalogUpdate

        timer_announcement=threading.Timer(12, arranque, [self.servant, announcement, my_proxy])
        timer_announcement.start()
        
        
        self.shutdownOnInterrupt()
       
        broker.waitForShutdown()
        topic_announcements.unsubscribe(proxy_announcement)
        topic_catalogUpdates.unsubscribe(proxy_catalog_updates)
        topic_fileAvailability.unsubscribe(proxy_file_availability)
        return 1



if __name__ == '__main__':
    catalog=Catalog()
    if len(sys.argv) != 2:
        print("Para lanzar ./catalog.py <config>")
    else:
        sys.exit(catalog.main(sys.argv))
        