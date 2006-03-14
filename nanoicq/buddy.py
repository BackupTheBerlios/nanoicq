
#
# $Id: buddy.py,v 1.10 2006/03/14 11:53:05 lightdruid Exp $
#

from antarctica import Frozen

class Buddy:

    def __init__(self):
        self.name = None
        self.email = None
        self.gid = None
        self.ids = None
        self.uin = None
        self.status = 'offline'
        self.firstMessage = 0

    def __repr__ZZZ(self):
        out = []
        for v in self.__dict__:
            out.append("%s: %s" % (v, str(self.__dict__[v])))
        return ',\n'.join(out)

    def __repr__(self):
        return "Buddy: name: '%s', gid = '%s', email: '%s', uin: '%s', firstMessage: '%d'" % \
            (self.name, self.gid, self.email, self.uin, self.firstMessage)

if __name__ == '__main__':
    b = Buddy()
    b.name = 'a'
    print b

# ---
