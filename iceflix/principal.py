#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Ice
import threading
import sys
import IceStorm
Ice.loadSlice('iceflix/iceflix.ice')
import IceFlix

class Main(IceFlix.Main):
    def getCatalog():
        return 0
    def getAuthenticator(self):
        return 0
    def getFileService(self):
        return 0

class Announcement(IceFlix.Announcement):
    
        
    def announce(self, service, serviceId, current=None):
       print(serviceId)

def announce_catalog(announcement ,main, id_main):
    time = threading.Timer(8,announce_catalog,[announcement, main, id_main])
    announcement.announce(main, id_main)
    time.start()

class file(Ice.Application):
    def __init__(self):
        self.servant=Main()
        self.servantAnnouncement=Announcement()
    def run(self, argv):
        #Catalog proxy
        broker = self.communicator()
        adapter = broker.createObjectAdapterWithEndpoints("mainAdapter", "tcp")
        proxy=adapter.addWithUUID(self.servant)
        proxy_announcement=adapter.addWithUUID(self.servantAnnouncement)
        adapter.activate()
        print(proxy)
        
        proxyTopic=self.communicator().propertyToProxy("IceStormAdmin.TopicManager.Default")
        
        
        topicManager=IceStorm.TopicManagerPrx.checkedCast(proxyTopic)
        print(proxyTopic)
        
        try:
            topic_announcements=topicManager.retrieve("Announcements")  
        except IceStorm.NoSuchTopic:
            topic_announcements=topicManager.create("Announcements")  
        
        topic_announcements.subscribeAndGetPublisher({}, proxy_announcement)
        announcement_proxy=topic_announcements.getPublisher()
        announcement=IceFlix.AnnouncementPrx.uncheckedCast(announcement_proxy)

        timer=threading.Timer(8,announce_catalog,[announcement,proxy,str(proxy.ice_getIdentity().name)])
        timer.start()

        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 1
sys.exit(file().main(sys.argv))