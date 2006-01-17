
#
# $Id: WinampInfo.py,v 1.1 2006/01/17 12:21:41 lightdruid Exp $
#

import winamp

class WinampInfo:
    def __init__(self):
        self._w = None

    def load(self):
        self._w = winamp.winamp()

    def isLoaded(self):
        return self._w != None

    def getPlayingStatus(self):
        if not self.isLoaded():
            try:
                self.load()
            except:
                return 'not loaded'
        return self._w.getPlayingStatus()

    def __getattr__(self, a):
        return getattr(self._w, a)


#w = WinampInfo()
#print w.getPlayingStatus()
#print w.getCurrentTrackName()
#print w.getTrackInfo()
#print w.dumpList()

# ---
