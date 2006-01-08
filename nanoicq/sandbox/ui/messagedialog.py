
#
# $Id: messagedialog.py,v 1.6 2006/01/08 19:40:19 lightdruid Exp $
#

import sys
import wx

from persistence import PersistenceMixin

sys.path.insert(0, '../..')
from events import *
from message import Message

class MySplitter(wx.SplitterWindow):
    def __init__(self, parent, ID, name):
        wx.SplitterWindow.__init__(self, parent, ID,
            style = wx.SP_LIVE_UPDATE, name = name)

ID_SPLITTER = 8000
ID_BUTTON_SEND = 8001

class MessageDialog(wx.Dialog, PersistenceMixin):
    def __init__(self, parent, ID, userName, message, size = wx.DefaultSize, 
            pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER):

        wx.Dialog.__init__(self, parent, ID, userName, size = size,
            style = style, name = 'message_dialog_' + userName)

        PersistenceMixin.__init__(self, 'test.save')

        assert isinstance(message, Message)
        self._parent = parent

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        box1 = wx.StaticBox(self, -1)
        self.boxSizer1 = wx.StaticBoxSizer(box1, wx.HORIZONTAL)

        self._user = wx.StaticText(self, -1, '')
        self.boxSizer1.Add(self._user, 0, wx.ALIGN_LEFT)

        self.boxSizer1.Add((60, 20), 0, wx.EXPAND)

        self._status = wx.StaticText(self, -1, 'status')
        self.boxSizer1.Add(self._status, 1, wx.ALIGN_RIGHT)

        self.sizer.Add(self.boxSizer1, 0, wx.EXPAND)

        # 2nd
        box2 = wx.StaticBox(self, -1)
        self.boxSizer2 = wx.StaticBoxSizer(box2, wx.HORIZONTAL)

        self.splitter = MySplitter(self, ID_SPLITTER,
            name = 'splitter_' + userName)

        self.incoming = wx.Panel(self.splitter, style=0)
        self.incomingSizer = wx.BoxSizer(wx.VERTICAL)
        self._incoming = wx.TextCtrl(self.incoming, -1, "",
            style=wx.TE_MULTILINE|wx.TE_RICH2|wx.CLIP_CHILDREN)
        self.incomingSizer.Add(self._incoming, 1, wx.EXPAND, 1)
        self.incoming.SetSizer(self.incomingSizer)
        self.incoming.SetAutoLayout(True)
        self.incoming.SetBackgroundColour("pink")
        self.incomingSizer.Fit(self.incoming)

        self._incoming.SetValue(message.getContents())

        self.outgoing = wx.Panel(self.splitter, style=0)
        self.outgoingSizer = wx.BoxSizer(wx.VERTICAL)
        self._outgoing = wx.TextCtrl(self.outgoing, -1, "",
            size=wx.DefaultSize, style=wx.TE_MULTILINE|wx.TE_RICH2)
        self.outgoingSizer.Add(self._outgoing, 1, wx.EXPAND, 1)
        self.outgoing.SetSizer(self.outgoingSizer)
        self.outgoing.SetAutoLayout(True)
        self.outgoing.SetBackgroundColour("sky blue")
        self.outgoingSizer.Fit(self.incoming)

        self.splitter.SetMinimumPaneSize(20)
        self.splitter.SplitHorizontally(self.incoming, self.outgoing, -100)

        self._pane = self.splitter
        self.outgoing.SetFocus()

        self.boxSizer2.Add(self._pane, 1, wx.EXPAND)

        box3 = wx.StaticBox(self, -1)
        self.boxSizer3 = wx.StaticBoxSizer(box3, wx.HORIZONTAL)
        self.buttonOk = wx.Button(self, ID_BUTTON_SEND, 'Send',
            name = 'buttonOk_' + userName)
        self.boxSizer3.Add(self.buttonOk, 0, wx.ALIGN_RIGHT)

        # -- wrap up
        self.sizer.Add(self.boxSizer2, 4, wx.EXPAND)
        self.sizer.Add(self.boxSizer3, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

        # ---
        # In this case title = username
        self.setUserName(userName)
        self.setTitle(userName)

        try:
            self.restoreObjects([self.GetId(), ID_BUTTON_SEND, ID_SPLITTER],
                name = self._userName)
        except Exception, e:
            print e.__class__, e

        # ---
        self.Bind(wx.EVT_BUTTON, self.onSendMessage, id = ID_BUTTON_SEND)
        self.Bind(wx.EVT_BUTTON, self.onCancel, id = wx.ID_CANCEL)

        self.SetAutoLayout(True)

    def storeWidgets(self):
        self.storeObjects([self, self.buttonOk, self.splitter],
            name = self._userName)

        print 'Sending close event for dialog...', self.GetId()
        evt = NanoEvent(nanoEVT_DIALOG_CLOSE, self.GetId())
        evt.setVal(self.GetId())
        self._parent.GetEventHandler().ProcessEvent(evt)
        print 'Close event sent', self.GetId()

    def onCancel(self, evt):
        print 'onCancel'
        self.storeWidgets()
        evt.Skip()

    def onSendMessage(self, evt):
        print 'onSendMessage()'
        print 'Sending send message event for dialog...', self.GetId()

        message = Message(Message.ICQ_MESSAGE,
            self._userName, self._outgoing.GetValue())

        evt = NanoEvent(nanoEVT_SEND_MESSAGE, self.GetId())
        evt.setVal( (self.GetId(), message) )
        wx.GetApp().GetTopWindow().GetEventHandler().ProcessEvent(evt)
        evt.Skip()

    def setTitle(self, title):
        self.SetTitle(title)

    def setUserName(self, userName):
        self._userName = userName
        self._user.SetLabel(userName)

# ---
