
#
# $Id: group.py,v 1.13 2006/03/14 15:47:56 lightdruid Exp $
#

from buddy import Buddy
from utils import *

class Group:
    def __init__(self):
        self._g = {}
        self._b = {}

    def add(self, gid, name):
        assert gid not in self._g.keys()
        self._g[gid] = name

    def addBuddy(self, gid, b):
        # add default group if it doesn't exist
        if len(self._g.keys()) == 0:
            self.add(0, 'Global')

        assert gid in self._g.keys()
        b.gid = gid
        self._b[b.name] = b

    def deleteBuddy(self, b):
        print 'Deleting ', b, self._b.keys()
        del self._b[b.name]

    def getBuddies(self, gid = None, status = None):
        if gid is None and status == None:
            return self._b.values()

        if gid is not None:
            assert gid in self._g.keys()
            return [self._b[x] for x in self._b if self._b[x].gid == gid]

        if status is not None:
            return [self._b[x] for x in self._b if self._b[x].status == status]

    def getBuddy(self, name):
        return self._b[name]

    def getBuddyByUin(self, uin):
        for b in self._b.values():
            if b.uin == uin:
                return b
        raise Exception("UIN '%s' not found in buddies list" % uin)

    def __getitem__(self, key):
        return self._g[key]

    def __repr__(self):
        return "Group: groups count: %d, groups = %s, buddies: %s" % \
            (len(self._g), '|'.join(self._g.values()), '|'.join(self._b.keys()))

    def save(self, fileName):
        dump2file(fileName, self)

    @staticmethod
    def load(fileName):
        return restoreFromFile(fileName)


if __name__ == '__main__':
    g = Group()
    g.add(1, '#1')
    g.add(2, '#2')

    b1 = Buddy()
    b1.name = 'b1'

    b2 = Buddy()
    b2.name = 'b2'

    b3 = Buddy()
    b3.name = 'b3'

    g.addBuddy(1, b1)
    g.addBuddy(2, b2)
    g.addBuddy(2, b3)
    print g

    print g.getBuddies()
    print g.getBuddies(1)
    print g.getBuddies(2)

    print '='*50
    g.getBuddy('b2').name = 'aaa'
    print g.getBuddies()

    g.save('groups.dump')
    g2 = Group.load('groups.dump')
    assert len(g.getBuddies()) == len(g2.getBuddies())

# ---
