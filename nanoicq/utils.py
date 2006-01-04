
#
# $Id: utils.py,v 1.9 2006/01/04 12:22:36 lightdruid Exp $
#

import string
import cPickle
import time, random

def dtrace(f, name = None):
    '''
    Prints callable function name only
    '''
    if name is None:
        name = f.func_name
    def wrapped(*args, **kwargs):
        print "Calling", name, args, kwargs
        return f(*args, **kwargs)
    wrapped.__doc__ = f.__doc__
    return wrapped

def dtrace2(f, name = None):
    '''
    Prints callable function name and return value as well
    '''
    if name is None:
        name = f.func_name
    def wrapped(*args, **kwargs):
        print "Calling", name, args, kwargs
        result = f(*args, **kwargs)
        print "Called", name, args, kwargs, "returned", repr(result)
        return result
    wrapped.__doc__ = f.__doc__
    return wrapped

def asPrintable(s):
    out = ''
    for c in s:
        if c is not string.printable: c = '.'
        out += c
    return out

def genCookie():
    return ''.join([chr(random.randrange(0, 127)) for i in range(8)])

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

    assert len(genCookie()) == 8

    @dtrace
    def test(a):
        return a
    @dtrace2
    def test2(a):
        return a
    test(1)
    test(2)
    test(3)

    test2(1)
    test2(2)
    test2(3)

# ---
