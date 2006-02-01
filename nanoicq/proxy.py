
#
# $Id: proxy.py,v 1.2 2006/02/01 14:12:24 lightdruid Exp $
#

from isocket import ISocket

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
    def connect(self, host, port, userName = None):
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

def _test():
    p = Socks5Proxy('localhost', 1080)
    p.connect('login.icq.com', '5190')


if __name__ == '__main__':
    _test()

# ---
