
#
# $Id: proxy.py,v 1.3 2006/02/01 22:07:00 lightdruid Exp $
#

import struct

from isocket import ISocket
from utils import *

class Proxy(ISocket):
    def __init__(self, host, port, default_charset = 'cp1251'):
        ISocket.__init__(self, host, port, default_charset)

class HttpsProxy(Proxy):
    pass


class HttpProxy(HttpsProxy):
    pass


class Socks4Proxy(Proxy):
    pass


class Socks5Proxy(Proxy):
    def connect(self, host, port, userName = None, password = None):
        ISocket.connect(self)

        buf = chr(0x05)
        if userName is not None:
            buf += chr(0x02) # two methods
            buf += chr(0x00) # no authentication
            buf += chr(0x02) # username/password authentication
        else:
            buf += chr(0x01)
            buf += chr(0x00)

        ISocket.send(self, buf)

        buf = ISocket.read(self, 2)
        if ord(buf[0]) != 0x05 or ord(buf[1]) == 0xff:
            raise Exception("Bad answer from SOCKS5 proxy")

        if userName is not None:
            buf = '\x01' + struct.pack('!B', len(userName)) + userName
            buf += struct.pack('!B', len(password)) + password

            ISocket.send(self, buf)

            buf = ISocket.read(self, 2)
            print len(buf)
            if len(buf) != 2 or ord(buf[0]) != 0x01 or ord(buf[1]) != 0x00:
                raise Exception("Bad answer from SOCKS5 proxy")

        # Version, CONNECT, reserved, address type: host name
        buf = '\x05\x01\x00\x03'

        # Then actual data
        buf += struct.pack('!B', len(host)) + host
        buf += struct.pack('!H', port)

        ISocket.send(self, buf)

        buf = ISocket.read(self, 100)

        if ord(buf[0]) != 0x05 or ord(buf[1]) != 0x00:
            raise Exception("Bad answer from SOCKS5 proxy")

        print 'Socks5Proxy connect() is done'


def _test():
    p = Socks5Proxy('localhost', 1080)
#    p.connect('login.icq.com', 5190, 'andrey', 'andrey')
    p.connect('login.icq.com', 5190)


if __name__ == '__main__':
    _test()

# ---
