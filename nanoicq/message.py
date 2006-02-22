
#
# $Id: message.py,v 1.12 2006/02/22 16:13:56 lightdruid Exp $
#

import time

from utils import *
from HistoryDirection import Incoming, Outgoing

class Message:
    ICQ_MESSAGE = "icq"

    def __init__(self, context, user, content, direction, timeStamp = None):
        self.MessageTypes = [Message.ICQ_MESSAGE]
        assert context in self.MessageTypes
        assert direction in [Incoming, Outgoing]

        self._context = context
        self._user = user
        self._content = content
        self._direction = direction
        if timeStamp is None:
            self._timeStamp = time.localtime()
        else:
            self._timeStamp = timeStamp
        
    def getContext(self): return self._context
    def getUser(self): return self._user
    def getDirection(self): return self._direction
    def getContents(self): return self._content
    def getTimeStamp(self): return self._timeStamp

    def _decodeDirection(self, d):
        assert d in [Incoming, Outgoing]
        if d == Incoming: return 'incoming'
        return 'outgoing'

    def __repr__(self):
        return "Class Message (type: %s, dest: %s, content: %s, dir: %s)" %\
            (self._context, str(self._user), punicode(str(self._content)), self._decodeDirection(self._direction))

    def __eq__(self, m):
        return self._context == m._context and self._user == m._user \
            and self._content == m._content and self._direction == m._direction

class ICQMessage(Message):

    def __init__(self, user, uin, content, direction, timeStamp = None):
        Message.__init__(self, Message.ICQ_MESSAGE, user, content, direction, timeStamp)
        assert type(uin) == type('')
        self._uin = uin

    def getUIN(self): return self._uin

    def __repr__(self):
        return "Class ICQMessage (type: %s, dest: %s, uin: %s, content: %s, dir: %s)" %\
            (self._context, str(self._user), self._uin, punicode(str(self._content)), self._decodeDirection(self._direction))

    def __eq__(self, m):
        return self._uin == m._uin and Message.__eq__(self, m)

def messageFactory(context, *kw, **kws):
    if type(context) == type(Message.ICQ_MESSAGE):
        assert context in [Message.ICQ_MESSAGE]
        if context == Message.ICQ_MESSAGE:
            return ICQMessage(*kw, **kws)
    if type(context) == type(''):
        if context == "icq":
            return ICQMessage(*kw, **kws)

    raise Exception("Unknown messaeg type: " + str(context))

def _test():
    m = Message(Message.ICQ_MESSAGE, '', 'aaa', Incoming)
    print m
    im = ICQMessage('user', '12345', 'text', Incoming)
    print im
    assert im.getContents() == 'text'

    mm = messageFactory("icq", 'user', '12345', 'text', Incoming)
    assert mm == im
    assert mm.getDirection() == Incoming

    mm2 = messageFactory("icq", 'user', '12345', 'text', Outgoing)
    assert mm2 != im
    assert mm2.getDirection() == Outgoing

if __name__ == '__main__':
    _test()

# ---
