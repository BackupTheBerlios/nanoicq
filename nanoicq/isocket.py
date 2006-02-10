
#
# $Id: isocket.py,v 1.14 2006/02/10 15:59:20 lightdruid Exp $
#

import socket
import thread
import struct

class ISocket:
    _mutex = thread.allocate_lock()

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

    def read(self):
        try:
            self._mutex.acquire()
            head = self._sock.recv(6, socket.MSG_PEEK)
            self._mutex.release()
        except socket.error:
            self._mutex.release()
            raise

        try:
            pid, ch, seq, length = struct.unpack('!bbhh', head)
        except:
            raise
        
        if pid != 42:
            length = -1
        elif not length:
            pass
        else:
            pass

        buf = ''
        if length == -1:
            return buf

        try:
            self._mutex.acquire()
            buf = self._sock.recv(6 + length)
            self._mutex.release()
        except socket.error:
            self._mutex.release()
            raise

        if len(buf) != length + 6:
            print "Actual packet length differs from header length"

        return buf

def _test():
    s = ISocket('ftp.roedu.net', 21)
    s.connect()

if __name__ == '__main__':
    _test()

# ---
