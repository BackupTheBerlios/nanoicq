
#
# $Id: remote.py,v 1.3 2006/11/16 14:57:40 lightdruid Exp $
#

import sys
sys.path.insert(0, '../..')
from Plugin import Plugin, PluginException
from message import *
from icq import log

BOOTED = True


class Remote(Plugin):
    _trusted_uin = []

    _category = "remote"
    _domain = "misc"
    _name = "remote"

    def drawOptions(self, parent):
        import wx
        p = wx.Panel(parent, -1)
        wx.StaticText(p, -1, "Remote plugin settings")
        return p

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
