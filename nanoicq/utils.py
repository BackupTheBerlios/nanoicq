
#
# $Id: utils.py,v 1.7 2005/12/21 16:09:31 lightdruid Exp $
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
