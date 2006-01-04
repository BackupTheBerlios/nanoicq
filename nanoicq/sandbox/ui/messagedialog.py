
#
# $Id: messagedialog.py,v 1.4 2006/01/04 16:38:30 lightdruid Exp $
#

import sys
import wx

from persistence import PersistenceMixin

sys.path.insert(0, '../..')
from events import *

class MySplitter(wx.SplitterWindow):
    def __init__(self, parent, ID, name):
        wx.SplitterWindow.__init__(self, parent, ID,
            style = wx.SP_LIVE_UPDATE, name = name)

ID_SPLITTER = 8000

class MessageDialog(wx.Dialog, PersistenceMixin):
    def __init__(self, parent, ID, userName, message = '', size = wx.DefaultSize, 
            pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER):

        wx.Dialog.__init__(self, parent, ID, userName, size = size,
            style = style, name = 'message_dialog_' + userName)

        PersistenceMixin.__init__(self, 'test.save')

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

        self._incoming.SetValue(message)

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
        self.buttonOk = wx.Button(self, wx.ID_OK, 'Send',
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
            self.restoreObjects([self.GetId(), wx.ID_OK, ID_SPLITTER],
                name = self._userName)
        except Exception, e:
            print e.__class__, e

        # ---
        self.Bind(wx.EVT_BUTTON, self.OnOk, id = wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id = wx.ID_CANCEL)

        self.SetAutoLayout(True)

    def storeWidgets(self):
        self.storeObjects([self, self.buttonOk, self.splitter],
            name = self._userName)

        evt = NanoEvent(nanoEVT_DIALOG_CLOSE, self.GetId())
        evt.setVal(self.GetId())
        self._parent.GetEventHandler().ProcessEvent(evt)

    def OnCancel(self, evt):
        print 'OnCancel'
        self.storeWidgets()
        evt.Skip()

    def OnOk(self, evt):
        print 'OnOk'
        self.storeWidgets()
        evt.Skip()

    def setTitle(self, title):
        self.SetTitle(title)

    def setUserName(self, userName):
        self._userName = userName
        self._user.SetLabel(userName)

# ---
