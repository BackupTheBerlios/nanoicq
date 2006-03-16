
#
# $Id: UserInfo.py,v 1.2 2006/03/16 13:02:42 lightdruid Exp $
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
        wx.Notebook.__init__(self, parent, id, style = wx.NB_MULTILINE )

class _Pane_auto:
    def __init__(self):
        sz = None
        c = 0
        r = 0

    def _pre(self, items):
        for n in items:
            nn = eval("wx.TextCtrl(self, -1, '', style = wx.NO_BORDER, name = '%s')" % n)

    def _put_item(self, name):
        sz.Add(self.FindWindowByName(name), row = r, col = c + 2)
        self.FindWindowByName(name).SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        if hasattr(b, name):
            self.FindWindowByName(name).SetValue(eval('b.%s' % name))

class Pane_Summary(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        g = self._put_item
        sz = rcs.RowColSizer()

        #for n in ['name', 'first', 'last', 'mail', 'dob', 'gender', 'age']:
        #    nn = eval("wx.TextCtrl(self, -1, '', style = wx.NO_BORDER, name = '%s')" % n)

        #def g(name):
        #    sz.Add(self.FindWindowByName(name), row = r, col = c + 2)
        #    self.FindWindowByName(name).SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        #    if hasattr(b, name):
        #        self.FindWindowByName(name).SetValue(eval('b.%s' % name))

        c = 1
        r = 1
        sz.Add(wx.StaticText(self, -1, 'Nickname:'), row = r, col = c)
        g('name')
        r += 1
        sz.Add(wx.StaticText(self, -1, 'First name:'), row = r, col = c)
        g('first')
        r += 1
        sz.Add(wx.StaticText(self, -1, 'Last name:'), row = r, col = c)
        g('last')
        r += 1
        sz.Add(wx.StaticText(self, -1, 'E-mail:'), row = r, col = c)
        g('mail')
        r += 1
        sz.Add(wx.StaticText(self, -1, 'Date of birth:'), row = r, col = c)
        g('dob')
        r += 1

        c = 4
        r = 1
        sz.Add(wx.StaticText(self, -1, 'Gender:'), row = r, col = c)
        g('gender')
        r += 1
        sz.Add(wx.StaticText(self, -1, 'Age:'), row = r, col = c)
        g('age')
        r += 1

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class WhitePane(wx.Panel):
    def __init__(self, parent, img, b):
        wx.Panel.__init__(self, parent, -1)
        assert isinstance(b, Buddy)
        
        self.SetBackgroundColour(wx.WHITE)

        sz = wx.BoxSizer(wx.HORIZONTAL)

        self.picture = wx.StaticBitmap(self, -1, img)
        sz.Add(self.picture, 0, wx.EXPAND | wx.ALL, 10)

        hz = wx.BoxSizer(wx.VERTICAL)
        self.userName = wx.StaticText(self, -1, b.name)

        f = self.userName.GetFont()
        f.SetWeight(wx.BOLD)
        self.userName.SetFont(f)

        self.text2 = wx.StaticText(self, -1, 'View personal user details')
        hz.Add(self.userName, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)
        hz.Add(self.text2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)
        sz.Add(hz, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)

        self.SetSizer(sz)
        self.SetAutoLayout(True)

class UserInfoPanel(wx.Panel):
    _head = [
        'Summary', 'ICQ', 'Avatar', 'Contact', 'Location', 'Work', 
        'Background', 'Notes'
    ]

    def __init__(self, parent, iconSet, b):
        wx.Panel.__init__(self, parent, -1)

        self.iconSet = iconSet

        sz = wx.BoxSizer(wx.VERTICAL)
        self.nb = TestNB(self, -1)

        for h in self._head:
            try:
                win = eval("Pane_%s(self.nb, b)" % h)
                self.nb.AddPage(win, h)
            except NameError, msg:
                print msg
                raise

        self.wp = WhitePane(self, self.iconSet['main'], b)
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

    def makePanel(self, h, b):
        p = eval("Pane_%s(self.nb, b)" % h)
        #p.win = win
        #
        #def OnCPSize(evt, win=win):
        #    win.SetSize(evt.GetSize())
        #
        #p.Bind(wx.EVT_SIZE, OnCPSize)
        return p


class UserInfoFrame(wx.Frame):
    def __init__(self, parentFrame, ID, iconSet, b, title = 'User info',
            size = (370, 370), pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX):

        wx.Frame.__init__(self, None, ID, size = size, style = style,
            title = title)

        self.iconSet = iconSet
        self.mainIcon = wx.EmptyIcon()
        self.mainIcon.CopyFromBitmap(self.iconSet['main'])
        self.SetIcon(self.mainIcon)

        self.SetTitle('User info: ' + b.name)
        self.panel = UserInfoPanel(self, self.iconSet, b)


def _test():
    class NanoApp(wx.App):
        def OnInit(self):
            connector = None
            iconSetName = 'aox'
            self.iconSet = IconSet()
            self.iconSet.addPath('icons/' + iconSetName)
            self.iconSet.loadIcons()
            self.iconSet.setActiveSet(iconSetName)
            b = Buddy()
            b.name = 'Light Druid'
            frame = UserInfoFrame(None, -1, self.iconSet, b)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
