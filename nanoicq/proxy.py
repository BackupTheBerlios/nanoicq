
#
# $Id: proxy.py,v 1.1 2006/02/01 13:36:45 lightdruid Exp $
#


class Proxy:
    pass


class HttpsProxy(Proxy):
    pass


class HttpProxy(HttpsProxy):
    pass


class Socks4Proxy(Proxy):
    pass


class Socks5Proxy(Proxy):
    pass


def _test():
    p = Proxy()


if __name__ == '__main__':
    _test()

# ---
