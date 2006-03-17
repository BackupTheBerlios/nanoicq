
#
# $Id: UserInfo.py,v 1.4 2006/03/17 09:47:54 lightdruid Exp $
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
        pass

    def _pre(self, items):
        for n in items:
            nn = eval("wx.TextCtrl(self, -1, '', style = wx.NO_BORDER | wx.TE_READONLY, name = '%s')" % n)

    def _put_item(self, name, val = None):
        self.sz.Add(self.FindWindowByName(name), row = self.r, col = self.c + 2)
        self.FindWindowByName(name).SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        if hasattr(self.b, name) and eval('self.b.%s' % name) is not None:
            self.FindWindowByName(name).SetValue(eval('self.b.%s' % name))
        elif val is not None:
            self.FindWindowByName(name).SetValue(val)

class Pane_Notes(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        self.notes = wx.TextCtrl(self, -1, '', style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.notes.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))

        self.my_notes = wx.TextCtrl(self, -1, '', style = wx.TE_MULTILINE)

        sz.Add(wx.StaticText(self, -1, 'About:'), 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 7)
        sz.Add(self.notes, 1, wx.ALL | wx.EXPAND, 7)
        sz.Add(wx.StaticText(self, -1, 'My notes:'), 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 7)
        sz.Add(self.my_notes, 1, wx.ALL | wx.EXPAND, 7)

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Pane_Background(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        self.web = wx.TextCtrl(self, -1, '', style = wx.NO_BORDER | wx.TE_READONLY)
        self.web.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        self.web.SetValue('<none>')

        self.past_background = wx.TextCtrl(self, -1, '', style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.interests = wx.TextCtrl(self, -1, '', style = wx.TE_MULTILINE | wx.TE_READONLY)

        sz.Add(wx.StaticText(self, -1, 'Web site:'), 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 7)
        sz.Add(self.web, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 7)
        sz.Add(wx.StaticText(self, -1, 'Past background:'), 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 7)
        sz.Add(self.past_background, 10, wx.ALL | wx.EXPAND, 7)
        sz.Add(wx.StaticText(self, -1, 'Interests:'), 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 7)
        sz.Add(self.interests, 10, wx.ALL | wx.EXPAND, 7)

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Pane_Work(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        self.b = b
        self.sz = rcs.RowColSizer()
        sz = self.sz

        self._pre(['company', 'department', 'position', 'work_street', 
            'work_city', 'work_state', 'work_zip', 'work_country', 'work_web'])
        g = self._put_item

        self.c = 1
        self.r = 1
        sz.Add(wx.StaticText(self, -1, 'Company:'), row = self.r, col = self.c)
        g('company')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Department:'), row = self.r, col = self.c)
        g('department')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Position:'), row = self.r, col = self.c)
        g('position')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Street:'), row = self.r, col = self.c)
        g('work_street')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'City:'), row = self.r, col = self.c)
        g('work_city')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'State:'), row = self.r, col = self.c)
        g('work_state')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Postal code:'), row = self.r, col = self.c)
        g('work_zip')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Country:'), row = self.r, col = self.c)
        g('work_country')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Web site:'), row = self.r, col = self.c)
        g('work_web')
        self.r += 1

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Pane_Location(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        self.b = b
        self.sz = rcs.RowColSizer()
        sz = self.sz

        self._pre(['street', 'city', 'state', 'zip', 'country', 'lang1', 'lang2', 'lang3', 'timezone', 'local_time'])
        g = self._put_item

        self.c = 1
        self.r = 1
        sz.Add(wx.StaticText(self, -1, 'Street:'), row = self.r, col = self.c)
        g('street')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'City:'), row = self.r, col = self.c)
        g('city')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'State:'), row = self.r, col = self.c)
        g('state')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Postal code:'), row = self.r, col = self.c)
        g('zip')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Country:'), row = self.r, col = self.c)
        g('country')
        self.r += 1

        self.c = 4
        self.r = 1
        sz.Add(wx.StaticText(self, -1, 'Languages:'), row = self.r, col = self.c)
        g('lang1')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, ''), row = self.r, col = self.c)
        g('lang2')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, ''), row = self.r, col = self.c)
        g('lang3')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Time zone:'), row = self.r, col = self.c)
        g('timezone')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Local time:'), row = self.r, col = self.c)
        g('local_time')
        self.r += 1

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Pane_Contact(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        self.mails = wx.TextCtrl(self, -1, '', style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.phones = wx.TextCtrl(self, -1, '', style = wx.TE_MULTILINE | wx.TE_READONLY)

        sz.Add(wx.StaticText(self, -1, 'E-mail:'), 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 7)
        sz.Add(self.mails, 1, wx.ALL | wx.EXPAND, 7)
        sz.Add(wx.StaticText(self, -1, 'Phone:'), 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 7)
        sz.Add(self.phones, 1, wx.ALL | wx.EXPAND, 7)

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Pane_Avatar(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        self.sz = wx.StaticBoxSizer(wx.StaticBox(self, -1, ''), wx.VERTICAL)
        sz = self.sz

        img  = wx.NullBitmap
        self.avatar = wx.StaticBitmap(self, -1, img)
        sz.Add(self.avatar, 1, wx.ALL | wx.EXPAND, 1)

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Pane_ICQ(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        self.b = b
        self.sz = rcs.RowColSizer()
        sz = self.sz

        self._pre(['uin', 'external_ip', 'internal_ip', 'port', 
            'protocol_version', 'user_client', 'online_since', 
            'system_up_since', 'idle_since'])
        g = self._put_item

        self.c = 1
        self.r = 1
        sz.Add(wx.StaticText(self, -1, 'UIN:'), row = self.r, col = self.c)
        g('uin')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'External IP:'), row = self.r, col = self.c)
        g('external_ip')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Internal IP:'), row = self.r, col = self.c)
        g('internal_ip')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Port:'), row = self.r, col = self.c)
        g('port')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Protocol Version:'), row = self.r, col = self.c)
        g('protocol_version')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'User Client:'), row = self.r, col = self.c)
        g('user_client')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Online since:'), row = self.r, col = self.c)
        g('online_since')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'System up since:'), row = self.r, col = self.c)
        g('system_up_since')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Idle since:'), row = self.r, col = self.c)
        g('idle_since')
        self.r += 1

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Pane_Summary(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        self.b = b
        self.sz = rcs.RowColSizer()
        sz = self.sz

        self._pre(['name', 'first', 'last', 'mail', 'dob', 'gender', 'age'])
        g = self._put_item

        self.c = 1
        self.r = 1
        sz.Add(wx.StaticText(self, -1, 'Nickname:'), row = self.r, col = self.c)
        g('name')
        self.r += 1
        sz.Add(wx.StaticText(self, -1, 'First name:'), row = self.r, col = self.c)
        g('first')
        self.r += 1
        sz.Add(wx.StaticText(self, -1, 'Last name:'), row = self.r, col = self.c)
        g('last')
        self.r += 1
        sz.Add(wx.StaticText(self, -1, 'E-mail:'), row = self.r, col = self.c)
        g('mail')
        self.r += 1
        sz.Add(wx.StaticText(self, -1, 'Date of birth:'), row = self.r, col = self.c)
        g('dob')
        self.r += 1

        self.c = 4
        self.r = 1
        sz.Add(wx.StaticText(self, -1, 'Gender:'), row = self.r, col = self.c)
        g('gender')
        self.r += 1
        sz.Add(wx.StaticText(self, -1, 'Age:'), row = self.r, col = self.c)
        g('age')
        self.r += 1

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
            size = (370, 380), pos = wx.DefaultPosition,
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
