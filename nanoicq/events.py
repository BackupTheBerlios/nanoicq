
#
# $Id: events.py,v 1.13 2006/03/06 21:42:06 lightdruid Exp $
#

import wx

nanoEVT_GOT_NEW_UIN = wx.NewEventType()
EVT_GOT_NEW_UIN = wx.PyEventBinder(nanoEVT_GOT_NEW_UIN, 1)

nanoEVT_START_REGISTER = wx.NewEventType()
EVT_START_REGISTER = wx.PyEventBinder(nanoEVT_START_REGISTER, 1)

nanoEVT_GOT_CAPTCHA = wx.NewEventType()
EVT_GOT_CAPTCHA = wx.PyEventBinder(nanoEVT_GOT_CAPTCHA, 1)

nanoEVT_SEND_CAPTCHA_TEXT = wx.NewEventType()
EVT_SEND_CAPTCHA_TEXT = wx.PyEventBinder(nanoEVT_SEND_CAPTCHA_TEXT, 1)

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

nanoEVT_SEARCH_BY_EMAIL = wx.NewEventType()
EVT_SEARCH_BY_EMAIL = wx.PyEventBinder(nanoEVT_SEARCH_BY_EMAIL, 1)

nanoEVT_SEARCH_BY_NAME = wx.NewEventType()
EVT_SEARCH_BY_NAME = wx.PyEventBinder(nanoEVT_SEARCH_BY_NAME, 1)

nanoEVT_RESULT_BY_UIN = wx.NewEventType()
EVT_RESULT_BY_UIN = wx.PyEventBinder(nanoEVT_RESULT_BY_UIN, 1)

# Add user to list after search (FindUser.py)
nanoEVT_ADD_USER_TO_LIST = wx.NewEventType()
EVT_ADD_USER_TO_LIST = wx.PyEventBinder(nanoEVT_ADD_USER_TO_LIST, 1)

# Unable to add user to list after search (user with this UIN already in list, etc.)
nanoEVT_UNABLE_ADD_USER_TO_LIST = wx.NewEventType()
EVT_UNABLE_ADD_USER_TO_LIST = wx.PyEventBinder(nanoEVT_UNABLE_ADD_USER_TO_LIST, 1)

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
