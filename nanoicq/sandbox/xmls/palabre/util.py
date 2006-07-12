#!/usr/bin/python

# $Id: util.py,v 1.3 2006/07/12 14:59:56 lightdruid Exp $

import md5, time, random

def fail():
    raise NotImplementedError

def ashex(data, sep = ''):
    out = ''
    for c in data: 
        out += ("%02X" + sep) % ord(c)
    return out

def generateSessionId():
    h = md5.new()
    h.update(str(time.time()))
    h.update(str(random.randrange(int(time.time()))))
    return ashex(h.digest())

def safeClose(c):
    """ Close cursor, safely, quietly """
    try:
        c.close()
    except Exception, exc:
        print str(exc)
        pass


if __name__ == '__main__':
    print generateSessionId()

#---

