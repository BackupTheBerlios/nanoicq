
#
# $Id: winamp_plugin.py,v 1.1 2006/10/19 10:17:03 lightdruid Exp $
#

import sys
import socket

sys.path.insert(0, '../..')

from Plugin import Plugin, PluginException
from message import *
from icq import log

import winamp

_loaded = True

try:
    import winamp
except ImportError, exc:
    raise PluginException("Unable to initialize 'winamp' plugin: " + str(exc))
    _loaded = False


class Winamp(Plugin):
    _category = "service"
    _trusted_uin = [ "177033621" ]

    def __init__(self, connector):
        Plugin.__init__(self)
        self._connector = connector

    def isLoaded(self):
        return _loaded

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
