
#
# $Id: errordialog.py,v 1.1 2006/08/27 14:09:30 lightdruid Exp $
#

import wx

class ErrorPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        box1 = wx.StaticBox(self, -1)
        self.boxSizer1 = wx.StaticBoxSizer(box1, wx.HORIZONTAL)

        tb = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE | wx.TE_RICH2 | wx.CLIP_CHILDREN | wx.TE_READONLY)
        self.boxSizer1.Add(tb, 1, wx.EXPAND | wx.ALL, 1)

        self.sizer.Add(self.boxSizer1, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.SetAutoLayout(True)

class ErrorDialog(wx.Dialog):
    def __init__(self, parent, message, title):
        wx.Dialog.__init__(self, parent, -1)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        p = ErrorPanel(self)

        self.sizer.Add(p, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.SetAutoLayout(True)


if __name__ == '__main__':
    class A(wx.App):
        def OnInit(self):
            d = ErrorDialog(None, '', '')
            d.ShowModal()
            return True

    w = A(redirect = False)

# ---
