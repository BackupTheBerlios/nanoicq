
#
# $Id: FindUser.py,v 1.1 2006/02/24 12:14:44 lightdruid Exp $
#

import sys
import traceback
import wx
import wx.lib.rcsizer as rcs

sys.path.insert(0, '../..')
from events import *
from buddy import Buddy


class SearchStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(2)
        self.SetStatusWidths([-2, -1])

    def setFileName(self, fn):
        path, fileName = os.path.split(fn)
        self.SetStatusText(fileName, 0)

    def setRowCol(self, row, col):
        self.SetStatusText("%d,%d" % (row,col), 1)

    def setDirty(self, dirty):
        if dirty:
            self.SetStatusText("...", 2)
        else:
            self.SetStatusText(" ", 2)


class FindUserPanel(wx.Panel):
    protocolList = ["ICQ"]

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        #wx.StaticText(self, -1, '45')

        sizer = rcs.RowColSizer()
        r = 0

        protoSizer = rcs.RowColSizer()
        self.protocol = wx.ComboBox(self, -1, self.protocolList[0], size = (110, -1), choices = self.protocolList, style = wx.CB_READONLY)
        protoSizer.Add(wx.StaticText(self, -1, 'Search:'), row = 1, col = 0)
        protoSizer.Add(self.protocol, row = 1, col = 3)
        sizer.Add(protoSizer, row = r, col = 1)
        r += 1

        boxSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.userIDRadio = wx.RadioButton(self, -1, "User ID")
        self.userID = wx.TextCtrl(self, -1, '', size = (155, -1))
        boxSizer1.Add(self.userIDRadio, 0, wx.ALL, 3)
        boxSizer1.Add(self.userID, 0, wx.ALL, 3)
        sizer.Add(boxSizer1, row = r, col = 1)
        r += 1

        boxSizer2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.emailRadio = wx.RadioButton(self, -1, "E-mail address")
        self.email = wx.TextCtrl(self, -1, '', size = (155, -1))
        boxSizer2.Add(self.emailRadio, 0, wx.ALL, 3)
        boxSizer2.Add(self.email, 0, wx.ALL, 3)
        sizer.Add(boxSizer2, row = r, col = 1)
        r += 1

        boxSizer3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.nameRadio = wx.RadioButton(self, -1, "Name")
        self.nick = wx.TextCtrl(self, -1, '', size = (110, -1))
        self.first = wx.TextCtrl(self, -1, '', size = (110, -1))
        self.last = wx.TextCtrl(self, -1, '', size = (110, -1))

        self.nameSizer = rcs.RowColSizer()
        self.nameSizer.Add(wx.StaticText(self, -1, 'Nick:'), row = 1, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nameSizer.Add(self.nick, row = 1, col = 3, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nameSizer.Add(wx.StaticText(self, -1, 'First:'), row = 2, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nameSizer.Add(self.first, row = 2, col = 3, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nameSizer.Add(wx.StaticText(self, -1, 'Last:'), row = 3, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nameSizer.Add(self.last, row = 3, col = 3, flag = wx.ALIGN_CENTER_VERTICAL)

        boxSizer3.Add(self.nameRadio, 0, wx.ALL, 3)
        boxSizer3.Add(self.nameSizer, 0, wx.ALL, 3)
        sizer.Add(boxSizer3, row = r, col = 1)
        r += 1

        boxSizer4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.advancedRadio = wx.RadioButton(self, -1, "Advanced")
        self.advancedButton = wx.ToggleButton(self, -1, 'Advanced >>', size = (155, -1))
        boxSizer4.Add(self.advancedRadio, 0, wx.ALL, 3)
        boxSizer4.Add(self.advancedButton, 0, wx.ALL, 3)
        sizer.Add(boxSizer4, row = r, col = 1)

        r += 2

        searchSizer = wx.BoxSizer(wx.VERTICAL)
        self.searchButton = wx.Button(self, -1, "Search", size = (155, 30))
        searchSizer.Add(self.searchButton, 1, wx.ALL, 8)
        sizer.Add(searchSizer, row = r, col = 1)
        r += 1

        self.setDefaults()

        # ---
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def setDefaults(self):
        self.userIDRadio.SetValue(True)
        self.userID.SetFocus()


class FindUserFrame(wx.Frame):
    def __init__(self, parentFrame, ID,
            size = (650, 465), 
            pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX  | wx.MINIMIZE_BOX):

        wx.Frame.__init__(self, None, ID, size = size, style = style)
        p = FindUserPanel(self)

        self.sb = SearchStatusBar(self)
        self.SetStatusBar(self.sb)

def _test():
    class NanoApp(wx.App):
        def OnInit(self):
            frame = FindUserFrame(None, -1)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
