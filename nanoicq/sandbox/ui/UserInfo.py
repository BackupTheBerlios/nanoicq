
#
# $Id: UserInfo.py,v 1.1 2006/03/16 11:28:48 lightdruid Exp $
#

import sys
import traceback
import string

import wx
import wx.lib.rcsizer as rcs
import wx.lib.mixins.listctrl as listmix

sys.path.insert(0, '../..')
from events import *
from buddy import Buddy
from iconset import IconSet


class TestNB(wx.Notebook):
    def __init__(self, parent, id):
        wx.Notebook.__init__(self, parent, id)


class WhitePane(wx.Panel):
    def __init__(self, parent, img):
        wx.Panel.__init__(self, parent, -1)
        self.SetBackgroundColour(wx.WHITE)

        sz = wx.BoxSizer(wx.HORIZONTAL)

        self.picture = wx.StaticBitmap(self, -1, img)
        sz.Add(self.picture, 0, wx.EXPAND | wx.ALL, 10)

        hz = wx.BoxSizer(wx.VERTICAL)
        self.text1 = wx.StaticText(self, -1, 'abcd')

        f = self.text1.GetFont()
        f.SetWeight(wx.BOLD)
        self.text1.SetFont(f)

        self.text2 = wx.StaticText(self, -1, 'View personal user details')
        hz.Add(self.text1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)
        hz.Add(self.text2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)
        sz.Add(hz, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)

        self.SetSizer(sz)
        self.SetAutoLayout(True)

class UserInfoPanel(wx.Panel):
    _head = [
        'Summary', 'ICQ', 'Avatar', 'Contact', 'Location', 'Work', 
        'Background', 'Notes'
    ]

    def __init__(self, parent, iconSet):
        wx.Panel.__init__(self, parent, -1)

        self.iconSet = iconSet

        sz = wx.BoxSizer(wx.VERTICAL)
        self.nb = TestNB(self, -1)

        for h in self._head:
            win = self.makeColorPanel()
            self.nb.AddPage(win, h)

        self.wp = WhitePane(self, self.iconSet['main'])
        sz.Add(self.wp, 1, wx.EXPAND | wx.ALL, 0)
        sz.Add(wx.StaticLine(self, -1, style = wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 0)
        sz.Add(self.nb, 7, wx.EXPAND | wx.ALL, 7)

        hz = wx.BoxSizer(wx.HORIZONTAL)
        self.updateButton = wx.Button(self, -1, 'Update Now')
        self.okButton = wx.Button(self, -1, 'Ok')
        hz.Add(self.updateButton, 0, wx.ALL, 0)
        hz.Add((1, 1), 1, wx.ALL, 0)
        hz.Add(self.okButton, 0, wx.ALL, 0)
        sz.Add(hz, 1, wx.EXPAND | wx.ALL, 7)

        self.SetSizer(sz)
        self.SetAutoLayout(True)

    def makeColorPanel(self):
        p = wx.Panel(self.nb, -1)
        win = wx.Window(p, -1)
        p.win = win

        def OnCPSize(evt, win=win):
            win.SetSize(evt.GetSize())

        p.Bind(wx.EVT_SIZE, OnCPSize)
        return p


class UserInfoFrame(wx.Frame):
    def __init__(self, parentFrame, ID, iconSet, title = 'User info',
            size = (420, 370), pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX):

        wx.Frame.__init__(self, None, ID, size = size, style = style,
            title = title)

        self.iconSet = iconSet
        self.mainIcon = wx.EmptyIcon()
        self.mainIcon.CopyFromBitmap(self.iconSet['main'])
        self.SetIcon(self.mainIcon)

        self.panel = UserInfoPanel(self, self.iconSet)


def _test():
    class NanoApp(wx.App):
        def OnInit(self):
            connector = None
            iconSetName = 'aox'
            self.iconSet = IconSet()
            self.iconSet.addPath('icons/' + iconSetName)
            self.iconSet.loadIcons()
            self.iconSet.setActiveSet(iconSetName)
            frame = UserInfoFrame(None, -1, self.iconSet)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
