
#
# $Id: message.py,v 1.5 2006/01/16 07:57:53 lightdruid Exp $
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

    def __eq__(self, m):
        return self._typ == m._typ and self._user == m._user and self._content == m._content

class ICQMessage(Message):

    def __init__(self, user, uin, content):
        Message.__init__(self, Message.ICQ_MESSAGE, user, content)
        assert type(uin) == type('')
        self._uin = uin

    def getUIN(self): return self._uin

    def __repr__(self):
        return "Class ICQMessage (type: %d, dest: %s, uin: %s, content: %s)" %\
            (self._typ, str(self._user), self._uin, punicode(str(self._content)))

    def __eq__(self, m):
        return self._uin == m._uin and Message.__eq__(self, m)

def messageFactory(typ, *kw, **kws):
    if type(typ) == type(Message.ICQ_MESSAGE):
        assert typ in [Message.ICQ_MESSAGE]
        if typ == Message.ICQ_MESSAGE:
            return ICQMessage(*kw, **kws)
    if type(typ) == type(''):
        if typ == "icq":
            return ICQMessage(*kw, **kws)

    raise Exception("Unknown messaeg type: " + str(typ))

def _test():
    m = Message(Message.ICQ_MESSAGE, '', 'aaa')
    print m
    im = ICQMessage('user', '12345', 'text')
    print im
    assert im.getContents() == 'text'

    mm = messageFactory("icq", 'user', '12345', 'text')
    assert mm == im

if __name__ == '__main__':
    _test()

# ---
