
#
# $Id: winamp_plugin.py,v 1.2 2006/11/16 14:57:40 lightdruid Exp $
#

import sys
import socket

sys.path.insert(0, '../..')

from Plugin import Plugin, PluginException
from message import *
from icq import log

import winamp

BOOTED = True

try:
    import winamp
except ImportError, exc:
    raise PluginException("Unable to initialize 'winamp' plugin: " + str(exc))
    BOOTED = False


class Winamp(Plugin):
    _trusted_uin = [ "177033621" ]

    _category = "service"
    _domain = "misc"
    _name = "winamp"

    def hasOptions(self):
        return True

    def getName(self):
        return self._name

    def drawOptions(self, parent):
        import wx
        p = wx.Panel(parent, -1)
        wx.StaticText(p, -1, "Winamp plugin settings")
        return p

    def __init__(self, connector):
        Plugin.__init__(self)
        self._connector = connector

    def isLoaded(self):
        return self._loaded

    def onIncomingMessage(self, buddy, message):

        if buddy.uin in self._trusted_uin:
            txt = message.getContents().lower().strip()
            if txt == 'winamp':
                log().log("WINAMP: '%s' is in trusted UINs" % buddy.uin)
                m = messageFactory("icq", buddy.name, buddy.uin, self.formatReport(), Outgoing)
                self.sendMessage(buddy, m)

                # Set 'blocked' flag - do not display message
                message.blocked(True)
        else:
            log().log("WINAMP: '%s' is NOT in trusted UINs" % buddy.uin)

        return message

    def sendMessage(self, buddy = None, message = None):
        self._connector["icq"].sendMessage(message)

    def formatReport(self):
        try:
            w = winamp.winamp()
            if w is None:
                raise Exception("")
        except Exception, e:
            return "It looks like Winamp is not running at this moment: %s" %\
                str(e)

        status = w.getPlayingStatus()
        rc = "Winamp status on '%s': %s\n" % (socket.gethostname(), status)
        rc += "Current track: %s\n" % w.getCurrentTrackName()

        trackInfo = w.getTrackInfo()

        return rc

if __name__ == '__main__':
    w = Winamp(None)
    print w.formatReport()

# ---
