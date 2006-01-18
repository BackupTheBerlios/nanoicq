
#
# $Id: history.py,v 1.6 2006/01/18 16:25:54 lightdruid Exp $
#

import time

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
            else: fmt = '%d.%m %H:%M'
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

    unittest.main()
 
# ---
