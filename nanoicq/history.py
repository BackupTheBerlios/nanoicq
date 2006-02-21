
#
# $Id: history.py,v 1.9 2006/02/21 15:02:10 lightdruid Exp $
#

import time
import cPickle

from buddy import Buddy

class History:
    Incoming = 0
    Outgoing = 1
    _allowed = [Incoming, Outgoing]

    def __init__(self):
        self._d = []

    def __getitem__(self, n):
        return self._d[n]

    def __delitem__(self, n):
        del self._d[n]

    def append(self, direction, v = None):
        if v is None:
            # direction contains tuple(direction, message)
            assert type(direction) == type(())
            assert direction[0] in self._allowed
            self._d.append(direction)
        else:
            assert direction in self._allowed
            self._d.append( (direction, v) )

    def store(self, b):
        assert isinstance(b, Buddy)
        fn = "history.save.%s" % b.uin
        self._store(fn)

    def _store(self, fileName):
        f = open(fileName, 'wb')
        try:
            cPickle.dump(self._d, f)
        finally:
            f.close()

    @staticmethod
    def restore(b):
        assert isinstance(b, Buddy)
        fn = "history.save.%s" % b.uin
        h = History()
        try:
            h._restore(fn)
        except Exception, exc:
            print exc
        return h

    def _restore(self, fileName):
        f = open(fileName, 'rb')
        try:
            self._d = cPickle.load(f)
        finally:
            f.close()

    def dump(self):
        out = []
        for d, v in self._d:
            out.append("%s : %s" % (self._convDir(d), unicode(v)))
        return '\n'.join(out)

    def _convDir(self, d):
        assert d in self._allowed
        if d == self.Incoming:
            return '>>'
        return '<<'

    def format(self, msg, timestamp = False, longdate = False):
        txt = self._convDir(msg.getDirection()) + ' '

        if timestamp:
            if longdate: fmt = '%d.%m.%Y %H:%M:%S'
            else: fmt = '%x %X'
            txt += time.strftime(fmt, time.localtime()) + ' '
        txt += msg.getContents()

        return txt

    def __len__(self):
        return len(self._d)


if __name__ == '__main__':
    import unittest
    class HistoryTest(unittest.TestCase):

        def setUp(self):
            self.h = History()

        def testLen(self):
            assert len(self.h) == 0

        def testAdd(self):
            assert len(self.h) == 0

            item1 = History.Incoming, 'incoming 1'
            item2 = History.Outgoing, 'outgoing 1'

            self.h.append(item1)
            self.h.append(item2)

            d = self.h.dump()
            assert d.split('\n')[0] == '>> : incoming 1'
            assert d.split('\n')[1] == '<< : outgoing 1'

            v1 = self.h[0]
            v2 = self.h[1]

            assert v1 == item1
            assert v2 == item2

            assert len(self.h) == 2

            del self.h[0]
            d = self.h.dump()
            assert d.split('\n')[0] == '<< : outgoing 1'
            assert len(self.h) == 1

        def testPersistance(self):
            b = Buddy()
            b.uin = '123456'

            item1 = History.Incoming, 'incoming 1'
            self.h.append(item1)

            self.h.store(b)
            self.h = None
            del self.h

            self.h = History()
            h2 = History.restore(b)

            d = h2.dump()
            assert d.split('\n')[0] == '>> : incoming 1'

            b.uin = ''
            h3 = History.restore(b)
            d = h3.dump()
            assert len(d) == 0

    unittest.main()
 
# ---
