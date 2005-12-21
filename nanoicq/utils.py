
#
# $Id: utils.py,v 1.6 2005/12/21 16:08:19 lightdruid Exp $
#
# $Log: utils.py,v $
# Revision 1.6  2005/12/21 16:08:19  lightdruid
# Added SNAC(04,0A)     SRV_MISSED_MESSAGE
#
# Revision 1.5  2005/12/21 14:54:27  lightdruid
# Added Buddy, Group's and Frozen classes
#
# Revision 1.4  2005/12/21 12:08:05  lightdruid
# Added vimrc devel environment
#
# Revision 1.3  2005/12/13 15:25:47  lightdruid
# Trying to figure out why SNAC 13,4 doesn't work
#
# Revision 1.2  2005/11/17 13:28:06  lightdruid
# Id/Log tags added
#
#

import string
import cPickle

def dump2file(fileName, data):
    f = open(fileName, 'wb')
    cPickle.dump(data, f)
    f.close()

def restoreFromFile(fileName):
    f = open(fileName, 'rb')
    d = cPickle.load(f)
    f.close()
    return d

def ashex(data, sep = ''):
    out = ''
    for c in data: 
        out += ("%02X" + sep) % ord(c)
    return out

def fromhex(data):
    out = ''
    for c in data: 
        out += "%02X" % ord(c)
    return out

def asdump(s):
    out = ''
    for c in s: 
        if c not in string.printable: c = '.'
        if c in '\t\n\r\v\f': c = '.'
        out += c
    return out

def coldump(s):
    out = ''
    while s:
        out += "%-48s" % ashex(s[:16], ' ') + "%-16s" % asdump(s[:16]) + '\n'
        s = s[16:]
    return out

def toints(*args):
    if type(args[0]) == tuple:
        args = args[0]
    return map(int, map(None, args))

if __name__ == '__main__':
    a, b, c = '1', '2', '3'
    a, b, c = toints(a, b, c)
    assert a == 1
    assert b == 2
    assert c == 3

    import struct
    a, b = toints(struct.unpack('!2H', '\00\02\00\01'))
    assert a == 2
    assert b == 1

# ---
