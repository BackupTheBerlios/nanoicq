
#
# $Id: messagedialog.py,v 1.1 2006/01/04 12:24:57 lightdruid Exp $
#

import wx

class MySplitter(wx.SplitterWindow):
    def __init__(self, parent, ID):
        wx.SplitterWindow.__init__(self, parent, ID,
                                   style = wx.SP_LIVE_UPDATE
                                   )
class MessageDialog(wx.Dialog):
    def __init__(self, parent, ID, title, size = wx.DefaultSize, 
            pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER):
        wx.Dialog.__init__(self, parent, ID, title, size = size, style = style)

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

#        self._incoming = wx.TextCtrl(self, -1, "If supported by the native control, this is red, and this is a different font.",
#            size=(200, 100), style=wx.TE_MULTILINE|wx.TE_RICH2)

        self.splitter = MySplitter(self, -1)

        frame1 = wx.Panel(self.splitter, style=0)
        frame1sizer = wx.BoxSizer(wx.VERTICAL)
        self._incoming = wx.TextCtrl(frame1, -1, "If supported by the native control, this is red, and this is a different font.",
            style=wx.TE_MULTILINE|wx.TE_RICH2|wx.CLIP_CHILDREN)
        frame1sizer.Add(self._incoming, 1, wx.EXPAND, 1)
        frame1.SetSizer(frame1sizer)
        frame1.SetAutoLayout(True)
        frame1.SetBackgroundColour("pink")
        frame1sizer.Fit(frame1)

        frame2 = wx.Panel(self.splitter, style=0)
        frame2sizer = wx.BoxSizer(wx.VERTICAL)
        self._outgoing = wx.TextCtrl(frame2, -1, "If supported by the native control, this is red, and this is a different font.",
            size=wx.DefaultSize, style=wx.TE_MULTILINE|wx.TE_RICH2)
        frame2sizer.Add(self._outgoing, 1, wx.EXPAND, 1)
        frame2.SetSizer(frame2sizer)
        frame2.SetAutoLayout(True)
        frame2.SetBackgroundColour("sky blue")
        frame2sizer.Fit(frame1)

        self.splitter.SetMinimumPaneSize(20)
        self.splitter.SplitHorizontally(frame1, frame2, -100)

        self._pane = self.splitter

        self.boxSizer2.Add(self._pane, 1, wx.EXPAND)

        box3 = wx.StaticBox(self, -1)
        self.boxSizer3 = wx.StaticBoxSizer(box3, wx.HORIZONTAL)
        self.boxSizer3.Add(wx.Button(self, -1, 'Send'), 0, wx.ALIGN_RIGHT)

        # -- wrap up
        self.sizer.Add(self.boxSizer2, 4, wx.EXPAND)
        self.sizer.Add(self.boxSizer3, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        # ---
        self._userName = ''

        # ---
        self.setUserName('123')
        self.setTitle('123')

    def setTitle(self, title):
        self.SetTitle(title)

    def setUserName(self, userName):
        self._userName = userName
        self._user.SetLabel(userName)

# ---
