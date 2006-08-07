#!/usr/bin/python

# $Id: util.py,v 1.5 2006/08/07 09:50:32 lightdruid Exp $

import md5, time, random


# We use these to send userjoin/userleave notifications
EV_LEAVE = 0
EV_JOIN = 1

class InnerException(Exception):
    def __init__(self, errno, msg):
        Exception.__init__(self, msg)
        self.msg = msg
        self.errno = errno

    def __str__(self):
        return "'%s' error='%d'" % (self.msg, self.errno)

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

