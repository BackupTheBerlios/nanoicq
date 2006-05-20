#!/usr/bin/python

# $Id: User.py,v 1.1 2006/05/20 21:47:54 lightdruid Exp $

from util import *


class User:

    def __init__(self):
        # properties
        self.uid = None
        self.sesId = None
        self.login = None
        self.password = None
        self.groupId = None
        self.groupUserManagementLevel = None
        self.languageId = None
        self.roomManagementLevel = None
        self.userManagementLevel = None
        self.moderationLevel = None
        self.isBlocked = None
        self.lastIP = None
        self.dbOperator = None
        
    def getUserProperties(self, sesId, userId):
        fail()

    def setUserProperty(self, sesId, userId, propName, propValue):
        try:
            getattr(self, propName)
        except AttributeError:
            # property does not belong to class
            pass
        fail()

    def blockUser(self, sesId, userId, reason):
        fail()

    def unBlockUser(self, sesId, userId):
        fail()
 
if __name__ == '__main__':
    u = User()
    u.setUserProperty('', '', 'uidz', 'val')

#---

