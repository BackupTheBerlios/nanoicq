
#
# $Id: group.py,v 1.5 2006/01/23 16:53:43 lightdruid Exp $
#

from buddy import Buddy

class Group:
    def __init__(self):
        self._g = {}
        self._b = {}

    def add(self, gid, name):
        assert gid not in self._g.keys()
        self._g[gid] = name

    def addBuddy(self, gid, b):
        assert gid in self._g.keys()
        b.gid = gid
        self._b[b.name] = b

    def getBuddies(self, gid = None):
        if gid is None: return self._b.values()
        assert gid in self._g.keys()
        return [self._b[x] for x in self._b if self._b[x].gid == gid]

    def getBuddy(self, name):
        print 'Group.getBuddy() -> ', self._b.keys()
        print 'Group.getBuddy() -> ', self._b
        return self._b[name]

    def getBuddyByUin(self, uin):
        print self._b.keys()
        for b in self._b.values():
            print b.uin
            if b.uin == uin:
                return b
        raise Exception("UIN '%s' not found in buddies list" % uin)

    def __getitem__(self, key):
        return self._g[key]

    def __repr__(self):
        return "Group: groups count: %d, groups = %s, buddies: %s" % \
            (len(self._g), '|'.join(self._g.values()), '|'.join(self._b.keys()))

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

# ---
