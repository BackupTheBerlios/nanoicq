
#
# $Id: buddy.py,v 1.5 2006/02/02 12:21:43 lightdruid Exp $
#

from antarctica import Frozen

class Buddy(Frozen):

    def __init__(self):
        self.name = None
        self.email = None
        self.gid = None
        self.uin = None
        self.status = None
        self.firstMessage = 0

    def __repr__(self):
        return "Buddy: name: '%s', gid = '%s', email: '%s', uin: '%s', firstMessage: '%d'" % \
            (self.name, self.gid, self.email, self.uin, self.firstMessage)

if __name__ == '__main__':
    b = Buddy()
    b.name = 'a'
    print b

# ---
