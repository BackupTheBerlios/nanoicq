
#
# $Id: persistence.py,v 1.1 2005/12/29 13:12:24 lightdruid Exp $
#

import wx
import cPickle

class PersistenceMixin:
    def __init__(self, fileName):
        self._fileName = fileName

    def storeGeometry(self):
        fp = open(self._fileName, "wb")
        try:
            pos = self.GetPosition()
            size = self.GetSize()
            cPickle.dump((pos, size), fp)
        except:
            fp.close()
            raise

    def restoreGeometry(self, npos = None, nsize = None):
        pos = None
        size = None
        fp = None
        try:
            fp = open(self._fileName, "rb")
            pos, size = cPickle.load(fp)
        except:
            if fp is not None: fp.close()

        if pos is None: pos = npos
        if size is None: size = nsize

        self.SetPosition(pos)
        self.SetSize(size)
        self.forceVisible()
        self.Layout()

    def forceVisible(self):
        pos = self.GetPosition()

        if pos[0] < 0: pos = wx.Point(0, pos[1])
        if pos[1] < 0: pos = wx.Point(pos[0], 0)

        dsize = wx.GetDisplaySize()
        if pos[0] >= dsize[0]: pos = wx.Point(0, pos[1])
        if pos[1] >= dsize[1]: pos = wx.Point(pos[0], 0)

        self.SetPosition(pos)
        self.Layout()

# ---
