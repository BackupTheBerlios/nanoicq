
#
# $Id: history.py,v 1.2 2006/01/09 16:52:34 lightdruid Exp $
#

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
        for d, v in self._d:
            print "%s : %s" % (self._convDir(d), unicode(v))

    def _convDir(self, d):
        assert d in [self.Incoming, self.Outgoing]
        if d == self.Incoming:
            return '>>'
        else:
             return '<<'

    def __len__(self):
        return len(self._d)

def _test():
    h = History()
    assert len(h) == 0
    item1 = History.Incoming, 'incoming 1'
    item2 = History.Outgoing, 'outgoing 1'
    h.append(item1)
    h.append(item2)
    h.dump()

    v1 = h[0]
    v2 = h[1]

    assert v1 == item1
    assert v2 == item2

    assert len(h) == 2

    del h[0]
    h.dump()
    assert len(h) == 1

if __name__ == '__main__':
    _test()

# ---
