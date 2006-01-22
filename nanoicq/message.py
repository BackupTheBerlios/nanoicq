
#
# $Id: message.py,v 1.9 2006/01/22 22:53:10 lightdruid Exp $
#

from utils import *
from history import History

class Message:
    ICQ_MESSAGE = 0

    def __init__(self, context, user, content, direction):
        self.MessageTypes = [Message.ICQ_MESSAGE]
        assert context in self.MessageTypes
        assert direction in [History.Incoming, History.Outgoing]

        self._context = context
        self._user = user
        self._content = content
        self._direction = direction

    def getContext(self): return self._context
    def getUser(self): return self._user
    def getDirection(self): return self._direction
    def getContents(self): return self._content

    def _decodeDirection(self, d):
        assert d in [History.Incoming, History.Outgoing]
        if d == History.Incoming: return 'incoming'
        return 'outgoing'

    def __repr__(self):
        return "Class Message (type: %d, dest: %s, content: %s, dir: %s)" %\
            (self._context, str(self._user), punicode(str(self._content)), self._decodeDirection(self._direction))

    def __eq__(self, m):
        return self._context == m._context and self._user == m._user \
            and self._content == m._content and self._direction == m._direction

class ICQMessage(Message):

    def __init__(self, user, uin, content, direction):
        Message.__init__(self, Message.ICQ_MESSAGE, user, content, direction)
        assert type(uin) == type('')
        self._uin = uin

    def getUIN(self): return self._uin

    def __repr__(self):
        return "Class ICQMessage (type: %d, dest: %s, uin: %s, content: %s, dir: %s)" %\
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
    m = Message(Message.ICQ_MESSAGE, '', 'aaa', History.Incoming)
    print m
    im = ICQMessage('user', '12345', 'text', History.Incoming)
    print im
    assert im.getContents() == 'text'

    mm = messageFactory("icq", 'user', '12345', 'text', History.Incoming)
    assert mm == im
    assert mm.getDirection() == History.Incoming

    mm2 = messageFactory("icq", 'user', '12345', 'text', History.Outgoing)
    assert mm2 != im
    assert mm2.getDirection() == History.Outgoing

if __name__ == '__main__':
    _test()

# ---
