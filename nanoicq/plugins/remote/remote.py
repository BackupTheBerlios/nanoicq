
#
# $Id: remote.py,v 1.2 2006/08/27 13:33:45 lightdruid Exp $
#

import sys
sys.path.insert(0, '../..')
from Plugin import Plugin, PluginException
from message import *
from icq import log

_loaded = True


class Remote(Plugin):
    _trusted_uin = []

    _category = "remote"

    def isLoaded(self):
        return _loaded

    def onIncomingMessage(self, buddy, message):
        return message

    def sendMessage(self, buddy = None, message = None):
        self._connector.sendMessage(message)

    # ---
    def __init__(self):
        Plugin.__init__(self)


def _test():
    r = Remote()
    print r

if __name__ == '__main__':
    _test()

# ---
