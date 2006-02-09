#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# $Id: wxnanoicq.py,v 1.54 2006/02/09 13:20:36 lightdruid Exp $
#

_INTERNAL_VERSION = "$Id: wxnanoicq.py,v 1.54 2006/02/09 13:20:36 lightdruid Exp $"[20:-37]

import sys
import traceback

if sys.platform == 'win32':
    import win32con

sys.path.insert(0, '../..')

import thread
import time
import wx
import cPickle
import string

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
from userlistctrl import UserListCtrl
from iconset import *

# System-dependent handling of TrayIcon is in the TrayIcon.py
# When running on system other than win32, this class is simple
# interface with no functionality
from TrayIcon import TrayIcon

ID_HELP = wx.NewId()
ID_ABOUT = wx.NewId()
ID_ICQ_LOGIN = wx.NewId()

ID_HIDE_OFFLINE = wx.NewId()

_topMenu = (
    ("File",
        (
            (ID_ICQ_LOGIN, "ICQ login\tF2", "ICQ login", "self.OnIcqLogin", 0),
            (ID_HIDE_OFFLINE, "Hide offline users\tF4", "Hide offline users", "self.onHideOffline", wx.ITEM_CHECK),
            (),
            (wx.ID_EXIT, "E&xit\tAlt-X", "Exit NanoICQ", "self.OnExit", 0),
        )
    ),
    ("Help",
        (
            (ID_HELP, "Help\tF1", "Help", "self.OnHelp", 0),
            (ID_ABOUT, "About", "About", "self.OnAbout", 0),
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
                wx.Yield()
                buf = self.read()
                log().packetin_col(buf)

                ch, b, c = self.readFLAP(buf)
                snac = self.readSNAC(c)
                print 'going to call proc_%d_%d_%d' % (ch, snac[0], snac[1])
                print 'for this snac: ', unicode(snac)

                if snac[0] == 3 and snac[1] == 11:
                    #print "Buffer (bub): " + coldump(buf)
                    #print "Buffer (b): " + coldump(b)
                    #print "Data (c): " + coldump(c)
                    pass

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


class TopFrame(wx.Frame, PersistenceMixin):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
            pos=(150, 150), size=(350, 200))
        PersistenceMixin.__init__(self, "frame.position")

        # ---
        self._dialogs = []

        self.config = Config()
        self.config.read('sample.config')

        self.iconSet = IconSet()
        self.iconSet.addPath('icons/aox')
        self.iconSet.loadIcons()
        self.iconSet.setActiveSet('aox')

        #---
        self.createTopMenuBar()
        self.makeStatusbar()
        self.createTopPanel()

        # Setup default position and size, later it will be restored,
        # if position save were found
        self.restoreGeometry(wx.Point(0, 0), wx.Size(100, 100))

        self.mainIcon = wx.EmptyIcon()
        self.mainIcon.CopyFromBitmap(self.iconSet['main'])
        self.SetIcon(self.mainIcon)

        self.trayIcon = TrayIcon(self, self.mainIcon, self.iconSet)

        self.connector = Connector()
        self.connector.setConfig(self.config)
        self.connector.registerProtocol('icq', ICQThreaded(gui = self))

        self.updateStatusBar('Disconnected')

        # Events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(EVT_DIALOG_CLOSE, self.dialogClose)
        self.Bind(EVT_MESSAGE_PREPARE, self.onMessagePrepare)
        self.Bind(EVT_SEND_MESSAGE, self.onSendMessage)
        self.Bind(EVT_INCOMING_MESSAGE, self.onIncomingMessage)
        self.Bind(EVT_BUDDY_STATUS_CHANGED, self.onBuddyStatusChanged)

        self.Bind(wx.EVT_MENU, self.onToggleHideOffline, id = ID_HIDE_OFFLINE)

        # ---

    def onToggleHideOffline(self, evt):
        self.hideOffline(evt.Checked())

    def onSendMessage(self, evt):
        log().log('GUI sending message: ' + str(evt))
        ids, message = evt.getVal()

        # FIXME: only icq handled
        self.connector['icq'].sendMessage(message, offline = True)

    def onMessagePrepare(self, evt):
        evt.Skip()
        print 'onMessagePrepare', evt.getVal()

        currentItem, userName = evt.getVal()
        b = self.connector['icq'].getBuddy(userName)

        message = None
        #self.showMessage(userName, message)

        self._showMessageDialog(message, b)


    def dialogClose(self, evt):
        pass

    def updateStatusBar(self, msg):
        self.sb.SetStatusText(msg, 0)

    def findDialogForBuddy(self, b):
        assert isinstance(b, Buddy)
        for d in self._dialogs:
            if d.getBuddy().uin == b.uin:
                log().log('Found dialog for buddy %s' % b.name)
                return d
        log().log('Dialog for buddy %s not found' % b.name)
        return None

    def dispatch(self, *kw, **kws):
        print 'GUI dispatcher: ', kw, kws

        print kw[0][0]

        # Convert all spaces to underscores to get method name
        fn = 'event_' + kw[0][0].replace(' ', '_')
        func = getattr(self, fn, None)
        print 'going to call ' + fn + '()'

        func(kw[1:][0])

    def event_Incoming_message(self, kw):
        print 'Called event_Incoming_message with '
        print str(kw)

        b = kw['buddy']
        m = kw['message']

        evt = NanoEvent(nanoEVT_INCOMING_MESSAGE, self.GetId())
        evt.setVal((b, m))

        # Spent 4h to figure out why dialog hangs after message passing,
        # we should use AddPendingEvent() instead of ProcessEvent()
        # was: self.GetEventHandler().ProcessEvent(evt)

        self.GetEventHandler().AddPendingEvent(evt)

    def onBuddyStatusChanged(self, evt):
        '''
        Buddy status is changed, let's change his icon in user list
        TODO: change ison in opened message boxes
        '''
        b = evt.getVal()
        self.topPanel.userList.changeStatus(b)
        d = self.findDialogForBuddy(b)
        if d is not None:
            d.setStatus(b.status)
        evt.Skip()

    def onIncomingMessage(self, evt):
        print 'onIncomingMessage()'

        b, m = evt.getVal()
        evt.Skip()

        self._showMessageDialog(m, b)

    def _showMessageDialog(self, m, b):
        d = self.findDialogForBuddy(b)
        if d is not None:
            if m is not None:
                # Do not try to update dialog when dialog is fresh
                # and there is no message yet
                d.updateMessage(m)
            d.Show(True)
            d.SetFocus()
        else:
            self.showMessage(b.name, m)


    def event_New_buddy(self, kw):
        print 'Called event_New_Buddy with '
        print str(kw)

        b = kw['buddy']
        try:
            self.addBuddy(b)
        except:
            typ, value, tb = sys.exc_info()
            list = traceback.format_tb(tb, None) + \
                traceback.format_exception_only(type, value)
            err = "%s %s" % (
                "".join(list[:-1]),
                list[-1],
            )
            print 'ERROR: ', err

            wx.MessageBox(err, "Exception Message")

    @dtrace
    def event_Login_done(self, kw):
        self.updateStatusBar('Online')
        self.trayIcon.setToolTip('ICQ online')

    @dtrace
    def event_Login(self, kw):
        self.updateStatusBar('Logging in...')

    @dtrace
    def event_Logoff(self, kw):
        self.updateStatusBar('Offline')
        self.trayIcon.setToolTip('ICQ offline')

    @dtrace
    def event_Buddy_status_changed(self, kw):
        evt = NanoEvent(nanoEVT_BUDDY_STATUS_CHANGED, self.GetId())
        evt.setVal(kw['buddy'])
        self.GetEventHandler().AddPendingEvent(evt)

    def addBuddy(self, b):
        self.topPanel.userList.addBuddy(b)

    def createTopPanel(self):
        self.topPanel = TopPanel(self, self.iconSet)

    def createTopMenuBar(self):
        self.topMenuBar = wx.MenuBar()

        for item in _topMenu:
            menu = wx.Menu()

            header, det = item
            for d in det:
                if len(d) == 0:
                    menu.AppendSeparator() 
                else:
                    menu.Append(d[0], d[1], d[2], d[4])
                    self.Bind(wx.EVT_MENU, eval(d[3]), id = d[0])

            self.topMenuBar.Append(menu, header)

        self.SetMenuBar(self.topMenuBar)

    def makeStatusbar(self):
        self.sb = CustomStatusBar(self)
        self.SetStatusBar(self.sb)

    def OnClose(self, evt):
        evt.Skip()
        self.storeGeometry()
        for d in self._dialogs:
            d.storeWidgets()
        self.trayIcon.Destroy()

    def OnExit(self, *evts):
        self.storeGeometry()
        self.Close()

    def OnHelp(self, evt):
        evt.Skip()

    def OnAbout(self, evt):
        evt.Skip()

    def OnIcqLogin(self, evt):
        self.connector['icq'].connect()
        self.connector['icq'].login()
        self.connector['icq'].Start()

    def onHideOffline(self, evt):
        #self.topPanel.userList.onHideOffline(self.connector['icq'].getBuddies(status = 'offline'))
        evt.Skip()

    def hideOffline(self, flag):
        self.topPanel.userList.onHideOffline(self.connector['icq'].getBuddies(status = 'offline'), flag)

    def showMessage(self, userName, message, hide = False):
        print 'showMessage()'
        print "username: '%s'" % userName
        print "buddy is '%s'" % (str(self.connector["icq"].getBuddy(userName)))

        h = History()
        b = self.connector["icq"].getBuddy(userName)
        colorSet = self.connector["icq"].getColorSet()
        d = MessageDialog(self, -1, b, message, h, colorSet)
        d.SetIcon(self.mainIcon)

        if not hide:
            d.Show()
            d.SetFocus()

        self._dialogs.append(d)
        print self._dialogs

class TopPanel(wx.Panel):
    def __init__(self, parent, iconSet):
        wx.Panel.__init__(self, parent, -1)
        self.topPanelSizer = wx.BoxSizer(wx.VERTICAL)

        self.userList = UserListCtrl(self, -1, iconSet)

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

def main(args = []):
    class NanoApp(wx.App):
        def OnInit(self):
            frame = TopFrame(None, "NanoICQ")
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    wx.InitAllImageHandlers()
    app = NanoApp(redirect = False)
    app.MainLoop()

if __name__ == '__main__':
    main(sys.argv[1:])

# ---

