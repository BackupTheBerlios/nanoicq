#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# $Id: wxnanoicq.py,v 1.27 2006/01/11 14:30:36 lightdruid Exp $
#


import sys
import traceback

if sys.platform == 'win32':
    import win32con

sys.path.insert(0, '../..')

import thread
import time
import wx
import isocket
import images
import cPickle
import string

import wx.lib.mixins.listctrl as listmix

from buddy import Buddy
import icq
from icq import log

from StatusBar import *
from config import Config
import guidebug
from logger import log, LogException
from messagedialog import MessageDialog
from persistence import PersistenceMixin
from utils import *
from events import *
from message import Message
from history import History

ID_HELP = wx.NewId()
ID_ABOUT = wx.NewId()
ID_ICQ_LOGIN = wx.NewId()

ID_TEST = wx.NewId()

_topMenu = (
    ("File",
        (
            (wx.ID_EXIT, "E&xit\tAlt-X", "Exit NanoICQ", "self.OnExit"),
            (ID_ICQ_LOGIN, "ICQ login\tF2", "ICQ login", "self.OnIcqLogin"),
            (ID_TEST, "Test\tF4", "test", "self.OnTest"),
        )
    ),
    ("Help",
        (
            (ID_HELP, "Help\tF1", "Help", "self.OnHelp"),
            (ID_ABOUT, "About", "About", "self.OnAbout"),
        )
    ),
)

class ICQThreaded(icq.Protocol):
    def __init__(self, gui, sock = None):
        icq.Protocol.__init__(self, gui, sock)

    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Run(self):
        while self.keepGoing:

            try:
                buf = self.read()
                log().packetin(buf)

                ch, b, c = self.readFLAP(buf)
                snac = self.readSNAC(c)
                print 'going to call proc_%d_%d_%d' % (ch, snac[0], snac[1])
                print 'for this snac: ', snac

                tmp = "proc_%d_%d_%d" % (ch, snac[0], snac[1])
                func = getattr(self, tmp)

                func(snac[5])
            except:
                typ, value, tb = sys.exc_info()
                list = traceback.format_tb(tb, None) + \
                    traceback.format_exception_only(type, value)
                err = "%s %s" % (
                    "".join(list[:-1]),
                    list[-1],
                )
                print 'ERROR: ', err
                guidebug.message(err)
                print 'KEEP RUNNING'

        self.running = False


class Connector:
    _protocols = {}

    def setConfig(self, config):
        self._config = config

    def registerProtocol(self, name, protocol):
        self._protocols[name] = protocol
        self._protocols[name].readConfig(self._config)

    def __getitem__(self, attr):
        return self._protocols[attr]


class UserListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos = wx.DefaultPosition,
            size = wx.DefaultSize, style = 0):

        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self._parent = parent

        self.currentItem = -1
        self.buddies = {}
 
        self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected, self)

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def onItemSelected(self, evt):
        self.currentItem = evt.m_itemIndex

    def onDoubleClick(self, evt):
        userName = self.getColumnText(self.currentItem, 1)
        print "nDoubleClick item %d:%s" % (self.currentItem, userName)
        evt.Skip()

        evt = NanoEvent(nanoEVT_MESSAGE_PREPARE, self.GetId())
        evt.setVal((self.currentItem, userName))
        self._parent.GetEventHandler().ProcessEvent(evt)


class TopFrame(wx.Frame, PersistenceMixin):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
            pos=(150, 150), size=(350, 200))
        PersistenceMixin.__init__(self, "frame.position")

        self.createTopMenuBar()
        self.makeStatusbar()

        icon = self.prepareIcon(images.getLimeWireImage())
        self.SetIcon(icon)

        self.createTopPanel()
        self.restoreGeometry(wx.Point(0, 0), wx.Size(100, 100))

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # ---
        self.config = Config()
        self.config.read('sample.config')

        self.connector = Connector()
        self.connector.setConfig(self.config)
        self.connector.registerProtocol('icq', ICQThreaded(gui = self))

        self.updateStatusBar('Disconnected')

        # ---
        result = wx.GetApp().GetTopWindow().RegisterHotKey(ID_ICQ_LOGIN, wx.MOD_SHIFT, wx.WXK_F9)
        print result

        self._dialogs = []
#        self.OnTest(1)

        self.Bind(EVT_DIALOG_CLOSE, self.dialogClose)
        self.Bind(EVT_MESSAGE_PREPARE, self.onMessagePrepare)
        self.Bind(EVT_SEND_MESSAGE, self.onSendMessage)

        # ---

    def onSendMessage(self, evt):
        print 'GUI got message: ', evt
        ids, message = evt.getVal()
#        print "From %d id and contents are (%s) '%s'" %\
#            (ids, type(message), punicode(str(message)))

        # FIXME: only icq handled
        self.connector['icq'].sendMessage(message)

    def onMessagePrepare(self, evt):
        evt.Skip()
        print 'onMessagePrepare', evt.getVal()

        currentItem, userName = evt.getVal()
        user = self.connector['icq'].getBuddy(userName)

        message = Message(0, '', '')
        self.showMessage(userName, message)

    def dialogClose(self, evt):
        print 'dialog close data:', evt, evt.getVal()
        print 'self._dialogs: ', self._dialogs

    def updateStatusBar(self, msg):
        self.sb.SetStatusText(msg, 0)

    def dispatch(self, *kw, **kws):
        print 'GUI dispatcher: ', kw, kws

        print kw[0][0]

        # Convert all spaces to underscores to get method name
        fn = 'event_' + kw[0][0].replace(' ', '_')
        func = getattr(self, fn, None)
        print 'going to call ' + fn

        #guidebug.message(str(kw[1:][0]))
        func(kw[1:][0])

    def event_New_buddy(self, kw):
        print 'Called event_New_Buddy with '
        print str(kw)

        b = kw['buddy']
        #guidebug.message(str(b))

        try:
            self.addBuddy(b)
        except Exception, v:
            wx.MessageBox(str(v), "Exception Message")

    @dtrace
    def event_Login_done(self, kw):
        self.updateStatusBar('Online')

    @dtrace
    def event_Login(self, kw):
        self.updateStatusBar('Logging in...')

    @dtrace
    def event_Logoff(self, kw):
        self.updateStatusBar('Offline')

    def addBuddy(self, b):
        self.il = wx.ImageList(16, 16)
        self.idx1 = self.il.Add(images.getSmilesBitmap())
        self.topPanel.userList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        index = self.topPanel.userList.InsertImageStringItem(sys.maxint, '', self.idx1)
        self.topPanel.userList.SetStringItem(index, 1, b.name)
        self.topPanel.userList.SetItemData(index, b.gid)

        self.topPanel.userList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.topPanel.userList.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def createTopPanel(self):
        self.topPanel = TopPanel(self)

    def createTopMenuBar(self):
        self.topMenuBar = wx.MenuBar()

        for item in _topMenu:
            menu = wx.Menu()

            header, det = item
            for d in det:
                menu.Append(d[0], d[1], d[2])
                self.Bind(wx.EVT_MENU, eval(d[3]), id = d[0])

            self.topMenuBar.Append(menu, header)

        self.SetMenuBar(self.topMenuBar)

    def prepareIcon(self, img):
        """
        The various platforms have different requirements for the
        icon size...
        """
        if "wxMSW" in wx.PlatformInfo:
            img = img.Scale(16, 16)
        elif "wxGTK" in wx.PlatformInfo:
            img = img.Scale(22, 22)
        # wxMac can be any size upto 128x128, so leave the source img alone....
        icon = wx.IconFromBitmap(img.ConvertToBitmap() )
        return icon

    def makeStatusbar(self):
        self.sb = CustomStatusBar(self)
        self.SetStatusBar(self.sb)

    def OnClose(self, evt):
        evt.Skip()
        self.storeGeometry()
        for d in self._dialogs:
            print 'storing: ', d.GetName()
            d.storeWidgets()

    def OnExit(self, *evts):
        self.storeGeometry()
        self.Close()

    def OnHelp(self, evt):
        print "OnHelp"
        evt.Skip()

    def OnAbout(self, evt):
        print "OnAbout"
        evt.Skip()

    def OnIcqLogin(self, evt):
        self.connector['icq'].connect()
        self.connector['icq'].login()
        self.connector['icq'].Start()

    def OnTest(self, evt):
#        self.connector['icq'].sendMessage1('177033621', 
#            'Msg:' + time.asctime(time.localtime()), autoResponse = True)
        import random
        self.showMessage(str(random.random()))

    def showMessage(self, userName, message):

        h = History()
        d = MessageDialog(self, -1, self.connector["icq"].getBuddy(userName), message, h)
        icon = d.GetParent().prepareIcon(images.getLimeWireImage())
        d.SetIcon(icon)
        d.Show()
        d.SetFocus()

        print 'appending dialog', d.GetId()
        self._dialogs.append(d)
        print self._dialogs

        print 'done'

class TopPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.topPanelSizer = wx.BoxSizer(wx.VERTICAL)

        self.userList = UserListCtrl(self, -1, style = wx.LC_REPORT | wx.BORDER_SIMPLE)

        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = "Status"
        self.userList.InsertColumnInfo(0, info)

#        info.m_format = wx.LIST_FORMAT_RIGHT
        info.m_text = "User"
        self.userList.InsertColumnInfo(1, info)

        self.sampleFill()
        self.userList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.userList.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        # ---
        self.topPanelSizer.Add(self.userList, 1, wx.ALL | wx.EXPAND, 1)
        self.SetSizer(self.topPanelSizer)

    def sampleFill(self):
        musicdata = {
        1 : ("", "a"),
        2 : ("", "b"),
        3 : ("", "c"),
        4 : ("", "d"),
        5 : ("", "e"),
        6 : ("", "f"),
        7 : ("", "g"),
        8 : ("", "h"),
        }

        self.il = wx.ImageList(16, 16)
        self.idx1 = self.il.Add(images.getSmilesBitmap())
        self.userList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        # Here we need to setup a list data

        items = musicdata.items()
        for key, data in items:
            index = self.userList.InsertImageStringItem(sys.maxint, data[0], self.idx1)
            self.userList.SetStringItem(index, 1, data[1])
            b = Buddy()
            b.name = str(key)
            self.userList.buddies[key] = b
            self.userList.SetItemData(index, key)


class NanoApp(wx.App):
    def OnInit(self):
        frame = TopFrame(None, "NanoICQ")
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

app = NanoApp(redirect = False)
app.MainLoop()


# ---
