
#
# $Id: events.py,v 1.20 2006/08/27 11:45:48 lightdruid Exp $
#

import wx

nanoEVT_AUTHORIZATION_GRANTED = wx.NewEventType()
EVT_AUTHORIZATION_GRANTED = wx.PyEventBinder(nanoEVT_AUTHORIZATION_GRANTED, 1)

nanoEVT_ADD_USER_TO_LIST_BY_NAME = wx.NewEventType()
EVT_ADD_USER_TO_LIST_BY_NAME = wx.PyEventBinder(nanoEVT_ADD_USER_TO_LIST_BY_NAME, 1)

nanoEVT_OFFLINE_MESSAGES = wx.NewEventType()
EVT_OFFLINE_MESSAGES = wx.PyEventBinder(nanoEVT_OFFLINE_MESSAGES, 1)

nanoEVT_AUTHENTIFICATION_REQUEST = wx.NewEventType()
EVT_AUTHENTIFICATION_REQUEST = wx.PyEventBinder(nanoEVT_AUTHENTIFICATION_REQUEST, 1)

nanoEVT_GOT_USER_INFO = wx.NewEventType()
EVT_GOT_USER_INFO = wx.PyEventBinder(nanoEVT_GOT_USER_INFO, 1)

nanoEVT_REQUEST_USER_INFO = wx.NewEventType()
EVT_REQUEST_USER_INFO = wx.PyEventBinder(nanoEVT_REQUEST_USER_INFO, 1)

nanoEVT_USER_DELETE = wx.NewEventType()
EVT_USER_DELETE = wx.PyEventBinder(nanoEVT_USER_DELETE, 1)

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
