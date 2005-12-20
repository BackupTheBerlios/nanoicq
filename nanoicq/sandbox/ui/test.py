#!/usr/bin/python

#
# Test for 2,19,6
#
# $Id: test.py,v 1.2 2005/12/20 12:16:37 lightdruid Exp $
#
# $Log: test.py,v $
# Revision 1.2  2005/12/20 12:16:37  lightdruid
# 2,19,6 works in test.py
#
#

import sys
sys.path.insert(0, '../..')
from utils import *
import struct

class Log:
    def log(self, s):
        print s

log = Log()

import cPickle
f = open('string.dump', 'rb')
data = cPickle.load(f)
f.close()

print ashex(data)

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
 
    groupID = int(struct.unpack('!H', data[0:2])[0])
    itemID = int(struct.unpack('!H', data[2:4])[0])
    flagType = int(struct.unpack('!H', data[4:6])[0])
    dataLen = int(struct.unpack('!H', data[6:8])[0])
    log.log("groupID: %d, itemID: %d, flagType: %d, dataLen: %d" % \
        (groupID, itemID, flagType, dataLen))
 
    data = data[8 + dataLen:]


# ---   
