
#
# $Id: isocket.py,v 1.15 2006/02/11 00:31:15 lightdruid Exp $
#

import socket
import thread
import struct
import time

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

        length += 6
        lnbuf = len(buf)

        if lnbuf != length:
            print "Actual packet length (%d) differs from header length (%d)" %\
                (lnbuf, length)

            if length > lnbuf:
                gap = length - lnbuf
                print 'Trying to recover and read %d bytes...' % gap

                try:
                    self._mutex.acquire()
                    buf2 = self._sock.recv(gap)
                    self._mutex.release()
                    buf += buf2
                except socket.error, err:
                    self._mutex.release()
                    print 'Unable to recover:' + str(err)
            else:
                print 'Unable to recover'

        return buf

def _test():
    s = ISocket('ftp.roedu.net', 21)
    s.connect()

if __name__ == '__main__':
    _test()

# ---
