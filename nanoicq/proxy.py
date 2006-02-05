
#
# $Id: proxy.py,v 1.6 2006/02/05 14:53:03 lightdruid Exp $
#

import sys
sys.path.insert(0, '../..')

import struct
from base64 import b64encode, b64decode

from isocket import ISocket
from utils import *
from logger import log


class Proxy(ISocket):
    def __init__(self, host, port, default_charset = 'cp1251'):
        ISocket.__init__(self, host, port, default_charset)


class HttpsProxy(Proxy):
    def connect(self, host, port, userName = None, password = None):
        raise NotImplementedError("Https4Proxy")


class HttpProxy(HttpsProxy):
    def connect(self, host, port, userName = None, password = None):
        ISocket.connect(self)

        log().log("using CONNECT tunnelling for %s:%d" % (host, port))
        request = "CONNECT %s:%d HTTP/1.1\r\nHost: %s:%d\r\n" %\
            (host, port, host, port)

        if userName is not None:
            r = b64encode("%s:%d" % (userName, password))
            raise 1

        request += "\r\n"
        ISocket.send(self, request)

        response = ISocket.read(self, 1024)
        log().log('HttpProxy got response: ' + response)
        status = response.split()[1]

        if status not in ["200"]:
            log().log('HttpProxy error: ' + response)
            raise Exception(response)

        log().log('HttpProxy connected')
        

class Socks4Proxy(Proxy):
    def connect(self, host, port, userName = None, password = None):
        raise NotImplementedError("Socks4Proxy")


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
            log().log("Bad answer from SOCKS5 proxy: " + ashex(buf))
            raise Exception("Bad answer from SOCKS5 proxy")

        if userName is not None:
            log().log("Authentification...")

            buf = '\x01' + struct.pack('!B', len(userName)) + userName
            buf += struct.pack('!B', len(password)) + password

            ISocket.send(self, buf)

            buf = ISocket.read(self, 2)
            print len(buf)
            if len(buf) != 2 or ord(buf[0]) != 0x01 or ord(buf[1]) != 0x00:
                log().log("Bad answer from SOCKS5 proxy: " + ashex(buf))
                raise Exception("Bad answer from SOCKS5 proxy")

        # Version, CONNECT, reserved, address type: host name
        buf = '\x05\x01\x00\x03'

        # Then actual data
        buf += struct.pack('!B', len(host)) + host
        buf += struct.pack('!H', port)

        ISocket.send(self, buf)

        buf = ISocket.read(self, 100)

        if ord(buf[0]) != 0x05 or ord(buf[1]) != 0x00:
            log().log("Bad answer from SOCKS5 proxy: " + ashex(buf))
            raise Exception("Bad answer from SOCKS5 proxy")

        log().log('Socks5Proxy connected')


def _test():
    # export http_proxy="http://user:passwd@your.proxy.server:port/"
        
#    p = Socks5Proxy('localhost', 1080)
#    p.connect('login.icq.com', 5190, 'andrey', 'andrey')

    p = HttpProxy('localhost', 3128)
    p.connect('login.icq.com', 5190)


if __name__ == '__main__':
    _test()

# ---
