#!/usr/bin/python

# $Id: Group.py,v 1.1 2006/05/20 21:47:54 lightdruid Exp $

from util import *

DefaultModerationLevel = 0

class Group:

    def __init__(self):
        # Properties
        self.groupId = None
        self.groupName = None
        self.moderationLevel = None

    def groopLookUp(self, sesId, groupId, groupName = None):
        fail()

    def listGroups(self, sesId):
        fail()

    def createGroup(self, sesId, groupName, moderationLevel = DefaultModerationLevel):
        fail()

    def getGroupProperties(self, sesId, groupId):
        fail()

    # FIXME: signature differs from the one mentioned in diagram
    def setGroupProperties(self, sesId, groupId, groupName, moderationLevel):
        fail()

    # FIXME: returns something strange
    def listMembers(self, sesId, groupId):
        fail()

if __name__ == '__main__':
    g = Group()
    g.groopLookUp('', '')

#---

