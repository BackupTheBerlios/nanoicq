
#
# $Id: isocket.py,v 1.17 2006/08/25 10:10:30 lightdruid Exp $
#

import socket
import thread
import struct
import time


def _fake_log(s):
    print 'FAKE LOG:', s


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

        # How many times to try to recover and read number of bytes
        # specified in header
        max_attempts = 5 

        # And how long we should wait for next portion in seconds
        sleep_timout = 0.1

        lnbuf = len(buf)

        if lnbuf != length:
            _fake_log("Actual packet length (%d) differs from header length (%d)" %\
                (lnbuf, length))

            attempt = 1
            while True:
                lnbuf = len(buf)

                if length > lnbuf:
                    gap = length - lnbuf
                    _fake_log('Trying to recover and read %d bytes...' % gap)

                    try:
                        self._mutex.acquire()
                        buf2 = self._sock.recv(gap)
                        self._mutex.release()

                        buf += buf2

                        _fake_log('Got %d bytes in %d attempt' % (len(buf2), attempt))

                        if len(buf) != length:

                            if attempt > max_attempts:
                                _fake_log('Unable to recover after %d attempts' % max_attempts)
                                break

                            _fake_log('Even after retrying len(buf) = %d bytes' % (len(buf)))
                            time.sleep(sleep_timout)
                        else:
                            _fake_log('Recover complete')
                            break

                    except socket.error, err:
                        self._mutex.release()
                        _fake_log('Unable to recover:' + str(err))
                else:
                    _fake_log('Unable to recover after %d attempts' % max_attempts)
                    if attempt > max_attempts:
                        break

                attempt += 1

        return buf

def _test():
    s = ISocket('ftp.roedu.net', 21)
    s.connect()

if __name__ == '__main__':
    _test()

# ---
