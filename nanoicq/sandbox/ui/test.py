#!/usr/bin/python

#
# Test for 2,19,6
#
# $Id: test.py,v 1.5 2005/12/21 12:08:05 lightdruid Exp $
#
# $Log: test.py,v $
# Revision 1.5  2005/12/21 12:08:05  lightdruid
# Added vimrc devel environment
#
# Revision 1.4  2005/12/20 14:35:40  lightdruid
# working on 2,19,6
#
# Revision 1.3  2005/12/20 12:19:46  lightdruid
# a little fix for 2,19,6 in test.py
#
# Revision 1.2  2005/12/20 12:16:37  lightdruid
# 2,19,6 works in test.py
#
#

import sys
sys.path.insert(0, '../..')
from utils import *
from icq import *

import struct

class Log:
    def log(self, s):
        print s

log = Log()

import cPickle
f = open('string.dump', 'rb')
data = cPickle.load(f)
f.close()

# bad - 0000060001000200030000040000000000000001000600C800020001000000005
#       0000040000000000000001000600C800020001000000005F8D0004000500CA0001040

#data = '\00' + data

print ashex(data)
print len(ashex(data))
print coldump(data)

def test1():

    ver = int(struct.unpack('!B', data[0:1])[0])
    assert ver == 0

    nitems = int(struct.unpack('!H', data[1:3])[0])
    print coldump(data[1:3])
    log.log("Items number: %d" % nitems)

    data = data[3:]

    for ii in range(0, nitems):
        print '*' * 10, "Parsing SSI data..."
        print coldump(data)

        itemLen = int(struct.unpack('>H', data[0:2])[0])
        data = data[2:]
        name = data[:itemLen]
        log.log("Length: %d, '%s'" % (itemLen, name))

        data = data[itemLen:]
     
        groupID = int(struct.unpack('!H', data[0:2])[0])
        itemID = int(struct.unpack('!H', data[2:4])[0])
        flagType = int(struct.unpack('!H', data[4:6])[0])
        dataLen = int(struct.unpack('!H', data[6:8])[0])
        log.log("groupID: %d, itemID: %d, flagType: %d (%s), dataLen: %d" % \
            (groupID, itemID, flagType, explainSSIItemType(flagType), dataLen))

        tlvs = readTLVs(data[8 : 8 + dataLen])
        print tlvs
     
        data = data[8 + dataLen:]

def cbRequestSSI(itemdata):

    itemdata = itemdata[3:]

    while len(itemdata)>4:
        nameLength = struct.unpack('!H', itemdata[:2])[0]
        print 'nameLength', nameLength
        name = itemdata[2:2+nameLength]
        groupID, buddyID, itemType, restLength = \
            struct.unpack('!4H', itemdata[2+nameLength:10+nameLength])
        tlvs = readTLVs(itemdata[10+nameLength:10+nameLength+restLength])
        itemdata = itemdata[10+nameLength+restLength:]
        if itemType == 0: # buddies
            print 'Adding user ID', buddyID, name, tlvs
        elif itemType == 1: # group
            print 'Adding group: ', name, tlvs
        elif itemType == 2: # permit
            permit.append(name)
        elif itemType == 3: # deny
            deny.append(name)
        elif itemType == 4: # permit deny info
            if not tlvs.has_key(0xcb):
                continue # this happens with ICQ
            permitMode = {1:'permitall',2:'denyall',3:'permitsome',4:'denysome',5:'permitbuddies'}[ord(tlvs[0xca])]
            visibility = {'\xff\xff\xff\xff':'all','\x00\x00\x00\x04':'notaim'}[tlvs[0xcb]]
        elif itemType == 5: # unknown (perhaps idle data)?
            pass
        else:
            log.log('%s %s %s %s %s' % (name, groupID, buddyID, itemType, tlvs))
    timestamp = struct.unpack('!L',itemdata)[0]
    if not timestamp: # we've got more packets coming
        # which means add some deferred stuff
        d = defer.Deferred()
        self.requestCallbacks[snac[4]] = d
        d.addCallback(self._cbRequestSSI, (revision, groups, permit, deny, permitMode, visibility))
        return d

cbRequestSSI(data)

# ---   
