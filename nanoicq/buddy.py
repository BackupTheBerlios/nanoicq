
#
# $Id: buddy.py,v 1.1 2005/12/21 14:54:26 lightdruid Exp $
#

from antarctica import Frozen

class Buddy(Frozen):

    def __init__(self):
        self.name = None
        self.email = None
        self.firstMessage = 0

    def __repr__(self):
        return "Buddy: name: '%s', email: '%s', firstMessage: '%d'" % \
            (self.name, self.email, self.firstMessage)

if __name__ == '__main__':
    b = Buddy()
    b.name = 'a'
    print b

# ---
