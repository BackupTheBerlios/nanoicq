
#
# $Id: isocket.py,v 1.13 2006/02/01 14:12:24 lightdruid Exp $
#

import socket

class ISocket:
    def __init__(self, host, port, default_charset = 'cp1251'):
        self._host = host
        self._port = port
        self._sock = None

        # Charset to use if plain messsage contains non-ASCII characters
        self._default_charset = default_charset

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._sock.connect((self._host, self._port))

    def disconnect(self):
        if self._sock:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock = None

    def send(self, data):
        try:
            self._sock.send(data)
        except UnicodeEncodeError, msg:
            self._sock.send(data.encode(self._default_charset))

    def read(self, bufsize):
        return self._sock.recv(bufsize)

def _test():
    s = ISocket('ftp.roedu.net', 21)
    s.connect()

if __name__ == '__main__':
    _test()

# ---
