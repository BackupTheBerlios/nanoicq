
#
# $Id: buddy.py,v 1.2 2005/12/27 13:48:17 lightdruid Exp $
#

from antarctica import Frozen

class Buddy(Frozen):

    def __init__(self):
        self.name = None
        self.email = None
        self.firstMessage = 0
        self.gid = None

    def __repr__(self):
        return "Buddy: name: '%s', gid = '%s', email: '%s', firstMessage: '%d'" % \
            (self.name, self.gid, self.email, self.firstMessage)

if __name__ == '__main__':
    b = Buddy()
    b.name = 'a'
    print b

# ---
