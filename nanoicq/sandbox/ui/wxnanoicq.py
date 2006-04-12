#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# $Id: wxnanoicq.py,v 1.107 2006/04/12 10:57:23 lightdruid Exp $
#

_INTERNAL_VERSION = "$Id: wxnanoicq.py,v 1.107 2006/04/12 10:57:23 lightdruid Exp $"[20:-37]

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
import types

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
from AboutDialog import AboutDialog
from FindUser import FindUserFrame
from Captcha import CaptchaFrame
from Register import RegisterFrame
from UserInfo import UserInfoFrame

# System-dependent handling of TrayIcon is in the TrayIcon.py
# When running on system other than win32, this class is simple
# interface with no functionality

from TrayIcon import TrayIcon

ID_HELP = wx.NewId()
ID_ABOUT = wx.NewId()
ID_ICQ_LOGIN = wx.NewId()
ID_FIND_USER = wx.NewId()
ID_HIDE_OFFLINE = wx.NewId()
ID_NEW_USER = wx.NewId()
ID_DISCONNECT = wx.NewId()

_topMenu = (
    ("File",
        (
            (ID_ICQ_LOGIN, "ICQ login\tF2", "ICQ login", "self.OnIcqLogin", 0),
            (ID_HIDE_OFFLINE, "Hide offline users\tF4", "Hide offline users", "self.onToggleHideOffline", wx.ITEM_CHECK),
            (ID_FIND_USER, "Find/Add Contacts...\tF7", "Find/Add Contacts...", "self.onFindUser", 0),
            (ID_NEW_USER, "Register new UIN...\tCtrl-F12", "Register new UIN...", "self.onNewUser", 0),
            (),
            (ID_DISCONNECT, "Disconnect", "Disconnect", "self.onDisconnect", 0),
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
        self._threadHandle = thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Run(self):
        while self.keepGoing:

            try:
                #if wx.Thread_IsMain():

                try:
                    wx.YieldIfNeeded()
                except:
                    pass

                #wx.YieldIfNeeded()

                buf = self.read()
                log().packetin_col(buf)

                ch, b, c = self.readFLAP(buf)
                snac = self.readSNAC(c)
                print 'going to call proc_%d_%d_%d' % (ch, snac[0], snac[1])
                print 'for this snac: ', unicode(snac)

                flag1, flag2 = snac[2], snac[3]
                tmp = "proc_%d_%d_%d" % (ch, snac[0], snac[1])
                func = getattr(self, tmp)

                func(snac[5], flag2)
            except:
                typ, value, tb = sys.exc_info()
                list = traceback.format_tb(tb, None) + \
                    traceback.format_exception_only(type, value)
                err = "%s %s" % (
                    "".join(list[:-1]),
                    list[-1],
                )
                if self.keepGoing == False:
                    log().log('Disconnected by request')
                else:
                    print 'ERROR: ', err
                    log().log(err)
                    guidebug.message(err)
                    print 'KEEP RUNNING'

        print 'STOPPED'
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
        PersistenceMixin.__init__(self, self, "frame.position")

        # ---
        self._dialogs = []

        self.config = Config()
        self.config.read('sample.config')

        iconSetName = self.config.get('ui', 'iconset')
        self.iconSet = IconSet()
        self.iconSet.addPath('icons/' + iconSetName)
        self.iconSet.loadIcons()
        self.iconSet.setActiveSet(iconSetName)

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
        self.Bind(wx.EVT_ICONIZE, self.onIconfiy)
        self.Bind(EVT_DIALOG_CLOSE, self.dialogClose)
        self.Bind(EVT_MESSAGE_PREPARE, self.onMessagePrepare)
        self.Bind(EVT_SEND_MESSAGE, self.onSendMessage)
        self.Bind(EVT_INCOMING_MESSAGE, self.onIncomingMessage)
        self.Bind(EVT_BUDDY_STATUS_CHANGED, self.onBuddyStatusChanged)
        self.Bind(EVT_MY_STATUS_CHANGED, self.onMyStatusChanged)

        self.Bind(EVT_SEARCH_BY_UIN, self.onSearchByUin)
        self.Bind(EVT_SEARCH_BY_EMAIL, self.onSearchByEmail)
        self.Bind(EVT_SEARCH_BY_NAME, self.onSearchByName)


        self.Bind(wx.EVT_MENU, self.onToggleHideOffline, id = ID_HIDE_OFFLINE)
        self.Bind(wx.EVT_MENU, self.onShowHelp, id = ID_HELP)

        #self.Bind(EVT_GOT_CAPTCHA, self.onGotCaptcha)
        self.Bind(EVT_SEND_CAPTCHA_TEXT, self.onSendCaptchaText)
        self.Bind(EVT_START_REGISTER, self.onStartRegister)
        self.Bind(EVT_ADD_USER_TO_LIST, self.onAddUserToList)
        self.Bind(EVT_USER_DELETE, self.onUserDelete)
        self.Bind(EVT_REQUEST_USER_INFO, self.onRequestUserInfo)
        self.Bind(EVT_GOT_USER_INFO, self.onGotUserInfo)
        self.Bind(EVT_AUTHENTIFICATION_REQUEST, self.onAuthentificationRequest)
        self.Bind(EVT_OFFLINE_MESSAGES, self.onOfflineMessages)

        self._keepAliveTimer = wx.Timer(self)
        if self.config.has_option('icq', 'keep.alive.interval'):
            try:
                timerVal = self.config.getint('icq', 'keep.alive.interval')
                self._keepAliveTimer.Start(timerVal * 1000)
                log().log('Started keep alive timer (%d seconds)' % timerVal)
            except Exception, exc:
                log().log('Unable to start keep alive timer: ' + str(exc))
        self.Bind(wx.EVT_TIMER, self.onKeepAliveTimer)

        #self.Bind(EVT_RESULT_BY_UIN, self.onResultByUin)

        import Plugin
        self._plugins = Plugin.load_plugins('../../plugins', '../plugins',
            connector = self.connector)

        # FIXME:
        self._userInfoRequested = False

        #self.topPanel.userList.sampleFill()
        # ---

    def onOfflineMessages(self, evt):
        mq = evt.getVal()

        for m in mq:
            print '@@@', m
            b = Buddy()
            b.uin = m.getUIN()
            b.name = m.getUIN()

            evt = NanoEvent(nanoEVT_INCOMING_MESSAGE, self.GetId())
            evt.setVal((b, m))
            self.GetEventHandler().AddPendingEvent(evt)

            wx.YieldIfNeeded()

    def onAuthentificationRequest(self, evt):
        b = evt.getVal()
        rc = wx.MessageBox('Got authentification request from ' + b.name + ", allow?",
            'Request', wx.YES_NO)

        self.connector['icq'].sendAuthorizationReply(b, rc == wx.YES)

    def onRequestUserInfo(self, evt):
        print 'onRequestUserInfo'
        b = evt.getVal()

        # FIXME: ugly hack
        print type(b)
        if type(b) in types.StringTypes:
            b = self.connector['icq'].getBuddy(b)

        self.connector['icq'].getFullUserInfo(self.config.get("icq", "uin"), b.uin)
        self._userInfoRequested = True

    def onUserDelete(self, evt):
        name = evt.getVal()
        evt.Skip()
        b = self.connector['icq'].getBuddy(name)

        rc = wx.MessageBox("Delete user %s?" % b.name, "Delete user", wx.YES_NO)
        if rc != wx.YES:
            return

        try:
            self.connector['icq'].deleteBuddy(b)
            self.topPanel.userList.deleteBuddy(b)
        except Exception, exc:
            log().log('Got exception while deleting user: ' + str(exc))
            raise

    def onAddUserToList(self, evt):
        '''
        Add user to user list (after search)
        '''
        print 'onAddUserToList'
        evt.Skip()
        b = evt.getVal()

        try:
            nb = self.connector['icq'].getBuddyByUin(b.uin)
            if nb is not None:
                name = ''
                if b.name is not None and len(b.name) > 0:
                    name = "'%s'" % b.name
                msg = 'User %s with UIN %s already in list' % (name, str(b.uin))
                wx.MessageBox(msg, 'Add user', wx.OK)
        except Exception, exc:
            print exc
            log().log('Adding new user UIN %s to list' % str(b.uin))
            self.connector['icq'].addBuddyAfterSearch(b)

            # Add user to contact list
            self.connector['icq'].addBuddyToList(b)

            # Then start SSI edit strsaction
            self.connector['icq'].sendSSIEditBegin()
            self.connector['icq'].sendSSIAdd(b)
            self.connector['icq'].sendSSIEditEnd()

            rc = wx.MessageBox("Send authorization request to this user?",
                "New user", wx.YES_NO)
            if rc == wx.YES:
                self.connector['icq'].sendAuthorizationRequest(b)

#    def onUnableAddUserToList(self, evt):
#        '''
#        Unable to add user to list (UIN already exists, etc.)
#        '''
#        evt.Skip()

    def onKeepAliveTimer(self, evt):
        evt.Skip()
        try:
            self.connector['icq'].sendKeepAlive()
        except Exception, exc:
            print str(exc)

    def onSendCaptchaText(self, evt):
        evt.Skip()
        print 'MAIN: onSendCaptchaText'

    def onStartRegister(self, evt):
        print 'onStartRegister'
        proto = evt.getVal().lower()
        evt.Skip()

        self.connector[proto].sendHelloServer()

    def onNewUser(self, evt):
        evt.Skip()

        self.registerFrame = RegisterFrame(self, -1, self.connector["icq"], self.iconSet, self.config)
        self.registerFrame.CentreOnParent(wx.BOTH)
        self.registerFrame.Show()

    def onSearchByUin(self, evt):
        print 'onSearchByUin'
        ownerUin = self.config.get("icq", "uin")
        uin = evt.getVal()
        self.connector["icq"].searchByUin(ownerUin, uin)

    def onSearchByEmail(self, evt):
        print 'onSearchByEmail'
        ownerUin = self.config.get("icq", "uin")
        email = evt.getVal()
        self.connector["icq"].searchByEmail(ownerUin, email)

    def onSearchByName(self, evt):
        print 'onSearchByName'
        ownerUin = self.config.get("icq", "uin")
        nick, first, last = evt.getVal()
        self.connector["icq"].searchByName(ownerUin, nick, first, last)

    def onShowHelp(self, evt):
        try:
            import webbrowser
            webbrowser.open("http://nanoicq.berlios.de", 1)
        except:
            from wx.lib.dialogs import ScrolledMessageDialog
            dlg = ScrolledMessageDialog(parent = self, 
                    caption = "Help",
                    msg = """NanoICQ - alternative help (see the http://nanoicq.berlios.de for more elaborate information)                    
                          """)
            dlg.ShowModal()
            dlg.Destroy()

    def onIconfiy(self, evt):
        if self.config.getboolean('ui', 'minimize.to.tray'):
            self.Hide()
        evt.Skip()

    def onMyStatusChanged(self, evt):
        evt.Skip()
        self.connector['icq'].changeStatus(evt.getVal())

    def onToggleHideOffline(self, evt):
        self.hideOffline(evt.Checked())

    def hideOffline(self, flag):
        blist = self.connector['icq'].getBuddies(status = 'offline')
        self.topPanel.userList.onHideOffline(blist, flag)

    def onSendMessage(self, evt):
        log().log('GUI sending message: ' + str(evt))
        b, message = evt.getVal()
        print b, message, type(b), type(message)

        # FIXME: only icq handled
        #b = self.connector['icq'].getBuddyByUin(message.getUIN())
        log().log('User is ' + b.status)

        status = b.status == 'offline'
        self.connector['icq'].sendMessage(message, offline = status)

    def onMessagePrepare(self, evt):
        evt.Skip()
        print 'onMessagePrepare', evt.getVal()

        v = evt.getVal()
        if isinstance(v, Buddy):
            b = v
        else:
            currentItem, userName = v
            b = self.connector['icq'].getBuddy(userName)

        message = None
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
        # Convert all spaces to underscores to get method name
        fn = 'event_' + kw[0][0].replace(' ', '_')
        func = getattr(self, fn, None)
        print 'going to call ' + fn + '()'

        func(kw[1:][0])

    def event_Offline_messages(self, kw):
        q = kw['queue']
        print q

        evt = NanoEvent(nanoEVT_OFFLINE_MESSAGES, self.GetId())
        evt.setVal(q)
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(evt)

    def event_Got_CAPTCHA(self, kw):
        print 'Called event_Got_CAPTCHA'

        img = kw['image']

        evt = NanoEvent(nanoEVT_GOT_CAPTCHA, self.GetId())
        evt.setVal(img)
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(evt)
        if hasattr(self, 'registerFrame'):
            self.registerFrame.GetEventHandler().AddPendingEvent(evt)

    def event_Authentification_request(self, kw):
        b = kw['buddy']

        evt = NanoEvent(nanoEVT_AUTHENTIFICATION_REQUEST, self.GetId())
        evt.setVal(b)
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(evt)

    def event_New_UIN(self, kw):
        print 'Called event_New_UIN'

        uin = kw['uin']

        evt = NanoEvent(nanoEVT_GOT_NEW_UIN, self.GetId())
        evt.setVal(uin)
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(evt)
        if hasattr(self, 'registerFrame'):
            self.registerFrame.GetEventHandler().AddPendingEvent(evt)

    def event_Last_meta(self, kw):
        ''' We got last packet after requesting information about user
        '''
        print 'Called event_Last_meta with '
        print str(kw)

        b = kw['buddy']

        if b is None:
            return

        for v in b.__dict__.keys():
            print v, b.__dict__[v]

        dump2file('buddy.dump', b)

        evt = NanoEvent(nanoEVT_GOT_USER_INFO, self.GetId())
        evt.setVal(b)
        self.GetEventHandler().AddPendingEvent(evt)

    def onGotUserInfo(self, evt):
        #evt.Skip()

        b = evt.getVal()

        if self._userInfoRequested:
            _userInfoFrame = UserInfoFrame(None, -1, self.iconSet, b)
            _userInfoFrame.CentreOnParent(wx.BOTH)
            _userInfoFrame.Show(True)

            self._userInfoRequested = False

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
        TODO: change icon in opened message boxes
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

        for k in self._plugins:
            print 'Applying plugin ' + k
            m = self._plugins[k].onIncomingMessage(b, m)

        if m.blocked():
            log().log('Message is blocked, not needed to display it')
        else:
            self._showMessageDialog(m, b)

    def _showMessageDialog(self, m, b):
        d = self.findDialogForBuddy(b)
        if d is not None:
            if m is not None:
                # Do not try to update dialog when dialog is fresh
                # and there is no message yet
                d.updateMessage(m)
                d.addToHistory(m)
            d.Show(True)
            d.SetFocus()
            d.Raise()
        else:
            self.showMessage(b, m)

    def event_Results(self, kw):
        b = kw['buddy']

        evt = NanoEvent(nanoEVT_RESULT_BY_UIN, self.GetId())
        evt.setVal(b)
        self.fu.GetEventHandler().AddPendingEvent(evt)

    def event_New_buddy(self, kw):
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

    def onDisconnect(self, evt):
        b = restoreFromFile('buddy.dump')
        #b.name = 'Light Druid'

        self.connector['icq'].connect()
        self.connector['icq'].login()
        self.connector['icq'].Start()

        _userInfoFrame = UserInfoFrame(None, -1, self.iconSet, b)
        _userInfoFrame.CentreOnParent(wx.BOTH)
        _userInfoFrame.Show(True)

        #evt.Skip()
        #self.connector['icq'].disconnect()
        #self.connector['icq'].Stop()

    @dtrace
    def event_Disconnected(self, kw):
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

            # We need to explicitly destroy frames because they
            # done't have parents
            d.Destroy()

        self.connector['icq'].saveState()
        self.trayIcon.Destroy()

    def OnExit(self, *evts):
        self.storeGeometry()
        self.Close()

    def OnHelp(self, evt):
        evt.Skip()

    def OnAbout(self, evt):
        evt.Skip()
        ad = AboutDialog(self)
        ad.Show()

    def onFindUser(self, evt):
        self.fu = FindUserFrame(None, -1, self.iconSet)
        self.fu.Show(True)

    def OnIcqLogin(self, evt):
        try:
            self.updateStatusBar('Logging in...')
            self.connector['icq'].connect()
            self.connector['icq'].login()
            self.connector['icq'].Start()
        except Exception, exc:
            self.updateStatusBar('Disconnected')
            wx.MessageBox('Error: ' + str(exc), 'Connect error', wx.OK)

    def showMessage(self, b, message, hide = False):
        print 'showMessage()'
        print "username: '%s'" % b.name
        #print "buddy is '%s'" % (str(self.connector["icq"].getBuddy(userName)))

        #b = self.connector["icq"].getBuddy(userName)
        colorSet = self.connector["icq"].getColorSet()
        d = MessageDialog(self, -1, b, message, colorSet)
        d.SetIcon(self.mainIcon)
        d.addToHistory(message)

        if not hide:
            d.Show()
            d.SetFocus()
            d.Raise()

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

