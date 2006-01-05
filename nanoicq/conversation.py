
#
# $Id: conversation.py,v 1.1 2006/01/05 14:41:38 lightdruid Exp $
#

from buddy import Buddy
from message import Message

[CONV_UNKNOWN, CONV_IM, CONV_CHAT, CONV_MISC] = range(4)


class History:
    def __init__(self):
        self._d = []

    def __getitem__(self, n):
        return self._d[n]

    def __delitem__(self, n):
        del self._d[n]

    def append(self, v):
        self._d.append(v)


class Conversation:
    def __init__(self, buddy, message):
        assert isinstance(buddy, Buddy)
        assert isinstance(message, Message)
        self._buddy = buddy
        self._message = message

    def getBuddy(self): return self._buddy

    def getMessage(self): return self._message


def _test():
    b = Buddy()
    m = Message()
    h = History()
    h.append(2)
    assert h[0] == 2
    c = Conversation(b, m)
    assert c.getBuddy() == b
    assert c.getMessage() == m
    

if __name__ == '__main__':
    _test()

# ---
