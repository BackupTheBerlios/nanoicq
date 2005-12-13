
#
# $Id: isocket.py,v 1.11 2005/12/13 11:19:51 lightdruid Exp $
#

import socket

class ISocket:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = None

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._sock.connect((self._host, self._port))

    def disconnect(self):
        if self._sock:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock = None

    def send(self, data):
        self._sock.send(data)

    def read(self, bufsize):
        return self._sock.recv(bufsize)

def _test():
    s = ISocket('localhost', 25)

if __name__ == '__main__':
    _test()

# ---
