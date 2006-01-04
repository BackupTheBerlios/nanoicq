
#
# $Id: events.py,v 1.1 2006/01/04 15:10:10 lightdruid Exp $
#

import wx

nanoEVT_DIALOG_CLOSE = wx.NewEventType()
EVT_DIALOG_CLOSE = wx.PyEventBinder(nanoEVT_DIALOG_CLOSE, 1)

class NanoEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self._val = None

    def __del__(self):
        print '__del__'
        wx.PyCommandEvent.__del__(self)

    def setVal(self, val):
        self._val = val

    def getVal(self):
        return self._val


# ---
