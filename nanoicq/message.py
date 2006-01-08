
#
# $Id: message.py,v 1.2 2006/01/08 19:40:19 lightdruid Exp $
#

from utils import *

class Message:
    ICQ_MESSAGE = 0

    def __init__(self, typ, user, content):
        self.MessageTypes = [Message.ICQ_MESSAGE]
        assert typ in self.MessageTypes

        self._typ = typ
        self._user = user
        self._content = content

    def getContents(self): return self._content
    def getUser(self): return self._user

    def __repr__(self):
        return "Class Message (type: %d, dest: %s, content: %s)" %\
            (self._typ, str(self._user), punicode(str(self._content)))


def _test():
    m = Message(Message.ICQ_MESSAGE, '', 'ôûâ')
    print m

if __name__ == '__main__':
    _test()

# ---
