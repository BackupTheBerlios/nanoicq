
#
# $Id: utils.py,v 1.19 2006/03/10 15:22:25 lightdruid Exp $
#

import string
import cPickle
import sys, codecs, time, random
import warnings
import re
import struct
import random

from wx import VERSION

_ver = VERSION
if _ver[0] < 2:
    raise Exception("wxPython is too old, must be 2.6+")
if _ver[0] == 2 and _ver[1] < 6:
    raise Exception("wxPython is too old, must be 2.6+")
if _ver[0] != 2:
    warnings.warn("Untested wxPythonversion, tested with 2.6 only")

if sys.platform == 'win32':
    if sys.getwindowsversion()[0] < 5:
        warnings.warn('Windows prior to XP/2000/2003 are not tested')
    _enc, _dec, _srdr, _swtr = codecs.lookup('cp1251')
else:
    if sys.platform == 'linux2':
        _enc, _dec, _srdr, _swtr = codecs.lookup('utf-8')
    else:
        raise Exception('Codecs are not tuned yet for this platform')

def generateServerId(startID = 0x1000, stopID = 0x7777):
    '''
    Generate ID between startID and stopID
    '''
    return random.randrange(startID, stopID)

def parseAsciiz(data):
    ln = struct.unpack('<H', data[0:2])[0]
    d = data[2:2+ln]
    d = d.replace('\x00', '')
    return (d, data[2+ln:])

def parseWordLE(data):
    v = struct.unpack('<H', data[0:2])[0]
    return (v, data[2:])

def parseByteLE(data):
    v = struct.unpack('<B', data[0])[0]
    return (v, data[1:])

def parseProxyAddress(addr):
    re_proxy = re.compile("(http|https)://(\w+):(\w+)@([^:].*):(\d+)/?")

    m = re_proxy.match(addr)
    if not m:
        raise Exception("Bad proxy address, it must have following format 'http://user:passwd@your.proxy.server:port/'")
    return m.groups()

def punicode(s):
    return unicode(_dec(s)[0])

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
        if c not in string.printable: c = '.'
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

    assert "Light Druid" == asPrintable("Light Druid")

    sample = "http://user:passwd@your.proxy.server:1234/"
    proto, user, passwd, addr, port = parseProxyAddress(sample)
    assert proto == 'http'
    assert user == 'user'
    assert passwd == 'passwd'
    assert addr == 'your.proxy.server'
    assert port == '1234'

# ---
