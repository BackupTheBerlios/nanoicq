
#
# $Id: message.py,v 1.1 2006/01/05 14:41:38 lightdruid Exp $
#


class Message:
    ICQ_MESSAGE = 0

    def __init__(self, typ, content):
        self.MessageTypes = [Message.ICQ_MESSAGE]
        assert typ in self.MessageTypes

        self._typ = typ
        self._content = content

    def getContents(self): return self._content

    def __repr__(self):
        return "Class Message (type: %d, content: %s)" %\
            (self._typ, str(self._content))


def _test():
    m = Message(Message.ICQ_MESSAGE, 'test')
    print m

if __name__ == '__main__':
    _test()

# ---
