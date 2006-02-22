
#
# $Id: WinampInfo.py,v 1.2 2006/02/22 16:25:43 lightdruid Exp $
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

if __name__ == '__main__':
    w = WinampInfo()
    print w.getPlayingStatus()
    print w.getCurrentTrackName()
    print w.getTrackInfo()
    print w.dumpList()

# ---
