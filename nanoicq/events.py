
#
# $Id: events.py,v 1.7 2006/02/24 15:33:45 lightdruid Exp $
#

import wx

nanoEVT_DIALOG_CLOSE = wx.NewEventType()
EVT_DIALOG_CLOSE = wx.PyEventBinder(nanoEVT_DIALOG_CLOSE, 1)

nanoEVT_MESSAGE_PREPARE = wx.NewEventType()
EVT_MESSAGE_PREPARE = wx.PyEventBinder(nanoEVT_MESSAGE_PREPARE, 1)

nanoEVT_SEND_MESSAGE = wx.NewEventType()
EVT_SEND_MESSAGE = wx.PyEventBinder(nanoEVT_SEND_MESSAGE, 1)

nanoEVT_INCOMING_MESSAGE = wx.NewEventType()
EVT_INCOMING_MESSAGE = wx.PyEventBinder(nanoEVT_INCOMING_MESSAGE, 1)

nanoEVT_BUDDY_STATUS_CHANGED = wx.NewEventType()
EVT_BUDDY_STATUS_CHANGED = wx.PyEventBinder(nanoEVT_BUDDY_STATUS_CHANGED, 1)

nanoEVT_MY_STATUS_CHANGED = wx.NewEventType()
EVT_MY_STATUS_CHANGED = wx.PyEventBinder(nanoEVT_MY_STATUS_CHANGED, 1)

nanoEVT_SEARCH_BY_UIN = wx.NewEventType()
EVT_SEARCH_BY_UIN = wx.PyEventBinder(nanoEVT_SEARCH_BY_UIN, 1)

nanoEVT_RESULT_BY_UIN = wx.NewEventType()
EVT_RESULT_BY_UIN = wx.PyEventBinder(nanoEVT_RESULT_BY_UIN, 1)

class NanoEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self._val = None

    def __del__(self):
        wx.PyCommandEvent.__del__(self)

    def setVal(self, val):
        self._val = val

    def getVal(self):
        return self._val


# ---
