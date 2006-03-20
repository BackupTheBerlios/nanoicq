
#
# $Id: UserInfo.py,v 1.10 2006/03/20 14:31:40 lightdruid Exp $
#

import sys
import string

import wx
import wx.lib.rcsizer as rcs
import wx.lib.mixins.listctrl as listmix
import wx.lib.hyperlink as hyperlink

sys.path.insert(0, '../..')
from events import *
from buddy import Buddy
from iconset import IconSet
from utils import *
import codes


def _safe_to_str(v):
    if v is None: v = str(None)
    elif type(v) == type(1): v = str(v)
    return v

def _safe_to_int(v):
    if v is None: v = 0
    return v

_gender = {
    1: 'Female',
    2: 'Male'
}

_NA = '<not specified>'

def _conv_gender(v):
    if v in _gender.keys():
        return _gender[v]
    return _NA

def _conv_country(v):
    try:
        return codes.countries[v]
    except:
        return _NA

def _conv_lang(v):
    print 'LANG:', v
    try:
        return codes.languages[v]
    except:
        return _NA

class TestNB(wx.Notebook):
    def __init__(self, parent, id):
        wx.Notebook.__init__(self, parent, id, style = wx.NB_MULTILINE )

class _Pane_auto:
    _NA = _NA
    def __init__(self):
        pass

    def _pre(self, items):
        for n in items:
            nn = eval("wx.TextCtrl(self, -1, '', style = wx.NO_BORDER | wx.TE_READONLY, name = '%s')" % n)

    def _put_item(self, name, val = None, proc = None):

        self.sz.Add(self.FindWindowByName(name), row = self.r, col = self.c + 2)
        self.FindWindowByName(name).SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))

        if proc is not None:
            print proc, name, val

        if hasattr(self.b, name):
            v = eval('self.b.%s' % name)
            #print name, v
            if v is not None:
                if proc is not None:
                    #print v
                    v = proc(v)
                self.FindWindowByName(name).SetValue(_safe_to_str(v))
        elif val is not None:
            self.FindWindowByName(name).SetValue(val)
        else:
            print 'NOT FOUND', name
            self.FindWindowByName(name).SetValue(self._NA)

        if self.FindWindowByName(name).GetValue() == self._NA:
            self.FindWindowByName(name).SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))

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

        self.b = b

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        #self.homepage_address = wx.TextCtrl(self, -1, '', style = wx.NO_BORDER | wx.TE_READONLY, name = 'homepage_address')
        self.homepage_address = hyperlink.HyperLinkCtrl(self, -1, '', URL = '', name = 'homepage_address')
        self.homepage_address.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        #self.homepage_address.SetValue(self._NA)

        self.past_background = wx.TextCtrl(self, -1, '', style = wx.TE_MULTILINE | wx.TE_READONLY, name = 'past_background')
        self.interests = wx.TextCtrl(self, -1, '', style = wx.TE_MULTILINE | wx.TE_READONLY, name = 'interests')

        sz.Add(wx.StaticText(self, -1, 'Web site:'), 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 7)
        sz.Add(self.homepage_address, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 7)
        sz.Add(wx.StaticText(self, -1, 'Past background:'), 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 7)
        sz.Add(self.past_background, 10, wx.ALL | wx.EXPAND, 7)
        sz.Add(wx.StaticText(self, -1, 'Interests:'), 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 7)
        sz.Add(self.interests, 10, wx.ALL | wx.EXPAND, 7)

        self._set('homepage_address')
        self._set('past_background')
        self._set('interests')

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

    def _set(self, name, proc = None):
        if hasattr(self.b, name):
            v = eval('self.b.%s' % name)
            if v is not None:
                if proc is not None:
                    v = proc(v)
                if isinstance(self.FindWindowByName(name), hyperlink.HyperLinkCtrl):
                    self.FindWindowByName(name).SetLabel(_safe_to_str(v))
                    self.FindWindowByName(name).SetURL(_safe_to_str(v))
                else:
                    self.FindWindowByName(name).SetValue(_safe_to_str(v))

class Pane_Work(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        self.b = b
        self.sz = rcs.RowColSizer()
        sz = self.sz

        self._pre(['work_company', 'work_department', 'work_occupation_code', 'work_address',
            'work_city', 'work_state', 'work_zip', 'work_country', 'work_webpage'])
        g = self._put_item

        self.c = 1
        self.r = 1
        sz.Add(wx.StaticText(self, -1, 'Company:'), row = self.r, col = self.c)
        g('work_company')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Department:'), row = self.r, col = self.c)
        g('work_department')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Position:'), row = self.r, col = self.c)
        g('work_occupation_code')
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Street:'), row = self.r, col = self.c)
        g('work_address')
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
        g('work_country', proc = _conv_country)
        self.r += 1

        sz.Add(wx.StaticText(self, -1, 'Web site:'), row = self.r, col = self.c)
        g('work_webpage')
        self.r += 1

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

    def _set(self, name, proc = None):
        if hasattr(self.b, name):
            v = eval('self.b.%s' % name)
            if v is not None:
                if proc is not None:
                    v = proc(v)
                if isinstance(self.FindWindowByName(name), hyperlink.HyperLinkCtrl):
                    self.FindWindowByName(name).SetLabel(_safe_to_str(v))
                    self.FindWindowByName(name).SetURL(_safe_to_str(v))
                else:
                    self.FindWindowByName(name).SetValue(_safe_to_str(v))

class Pane_Location(wx.Panel, _Pane_auto):
    def __init__(self, parent, b):
        wx.Panel.__init__(self, parent, -1)
        _Pane_auto.__init__(self)

        self.b = b
        self.sz = rcs.RowColSizer()
        sz = self.sz

        self._pre(['street', 'city', 'state', 'zip', 
            'original_from_country_code', 
            'speaking_language_1', 'speaking_language_2', 'speaking_language_3',
            'timezone', 'local_time'])
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
        g('original_from_country_code')
        self.r += 1

        self.c = 4
        self.r = 1
        sz.Add(wx.StaticText(self, -1, 'Languages:'), row = self.r, col = self.c)
        g('speaking_language_1', proc = _conv_lang)
        self.r += 1

        sz.Add(wx.StaticText(self, -1, ''), row = self.r, col = self.c)
        g('speaking_language_2', proc = _conv_lang)
        self.r += 1

        sz.Add(wx.StaticText(self, -1, ''), row = self.r, col = self.c)
        g('speaking_language_3', proc = _conv_lang)
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

        self._pre(['nick', 'first', 'last', 'mail', 'dob', 'gender', 'age'])
        g = self._put_item

        self.c = 1
        self.r = 1
        sz.Add(wx.StaticText(self, -1, 'Nickname:'), row = self.r, col = self.c)
        g('nick')
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

        # Special handling for DOB
        sz.Add(wx.StaticText(self, -1, 'Date of birth:'), row = self.r, col = self.c)
        g('dob')

        dob_text = self._NA
        if hasattr(b, 'birth_day') and hasattr(b, 'birth_month') and hasattr(b, 'birth_year'):
            bd = _safe_to_int(getattr(b, 'birth_day'))
            bm = _safe_to_int(getattr(b, 'birth_month'))
            by = _safe_to_int(getattr(b, 'birth_year'))
            dob_text = "%02d.%02d.%04d" % (bd, bm, by)
            self.FindWindowByName('dob').SetValue(dob_text)
            self.FindWindowByName('dob').SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUTEXT))
        self.r += 1

        self.c = 4
        self.r = 1
        sz.Add(wx.StaticText(self, -1, 'Gender:'), row = self.r, col = self.c)
        g('gender', proc = _conv_gender)
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
        self.userName = wx.StaticText(self, -1, _safe_to_str(b.nick))

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
#class UserInfoFrame(wx.Dialog):
    def __init__(self, parentFrame, ID, iconSet, b, title = 'User info',
            size = (370, 380), pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX):

        wx.Frame.__init__(self, parentFrame, ID, size = size, style = style,
            title = title)
#        wx.Dialog.__init__(self, parentFrame, ID, size = size, style = style,
#            title = title)

        self.iconSet = iconSet
        self.mainIcon = wx.EmptyIcon()
        self.mainIcon.CopyFromBitmap(self.iconSet['main'])
        self.SetIcon(self.mainIcon)

        if b.nick is None:
            title = b.uin
        else:
            title = b.nick
        self.SetTitle('User info: ' + title)
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

            b = restoreFromFile('buddy.dump')
            #b.name = 'Light Druid'

            for v in b.__dict__.keys():
                print v, b.__dict__[v]


            frame = UserInfoFrame(None, -1, self.iconSet, b)
            self.SetTopWindow(frame)
            frame.CentreOnParent()
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
