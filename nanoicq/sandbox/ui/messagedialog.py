
#
# $Id: messagedialog.py,v 1.9 2006/01/17 15:14:00 lightdruid Exp $
#

import sys
import wx

from persistence import PersistenceMixin

sys.path.insert(0, '../..')
from events import *
from message import Message, messageFactory
from history import History
from buddy import Buddy

class MySplitter(wx.SplitterWindow):
    def __init__(self, parent, ID, name):
        wx.SplitterWindow.__init__(self, parent, ID,
            style = wx.SP_LIVE_UPDATE, name = name)

ID_SPLITTER = 8000
ID_BUTTON_SEND = 8001

class MessageDialog(wx.Dialog, PersistenceMixin):
    def __init__(self, parent, ID, user, message, history, size = wx.DefaultSize, 
            pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.DIALOG_NO_PARENT):

        wx.Dialog.__init__(self, parent, ID, user.name, size = size,
            style = style, name = 'message_dialog_' + user.name)

        PersistenceMixin.__init__(self, 'test.save')

        assert isinstance(user, Buddy)
        self._user = user
        userName = self._user.name

        assert isinstance(message, Message)
        self._parent = parent

        assert isinstance(history, History)
        self._history = history

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        box1 = wx.StaticBox(self, -1)
        self.boxSizer1 = wx.StaticBoxSizer(box1, wx.HORIZONTAL)

        self._userText = wx.StaticText(self, -1, '')
        self.boxSizer1.Add(self._userText, 0, wx.ALIGN_LEFT)

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

    def getBuddy(self):
        ''' Return buddy assigned to this conversation
        '''
        return self._user

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

        self._history.append(History.Outgoing, self._outgoing.GetValue())

        message = messageFactory("icq",
            self._user.name, self._user.uin, self._outgoing.GetValue())

        evt = NanoEvent(nanoEVT_SEND_MESSAGE, self.GetId())
        evt.setVal( (self.GetId(), message) )
        wx.GetApp().GetTopWindow().GetEventHandler().ProcessEvent(evt)
        evt.Skip()

        # Update UI
        txt = self._history.format(History.Outgoing, message, timestamp = True) + '\n'

        self._incoming.AppendText(txt)
        self._outgoing.Clear()

        self._incoming.Update()
        self._outgoing.Update()

    def setTitle(self, title):
        self.SetTitle(title)

    def setUserName(self, userName):
        self._userName = userName
        self._userText.SetLabel(userName)

# ---
