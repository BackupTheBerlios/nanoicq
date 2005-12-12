#!/usr/bin/python

#
# $Id: wxnanoicq.py,v 1.5 2005/12/12 16:02:24 lightdruid Exp $
#

import sys
sys.path.insert(0, '../..')

import thread
import time
import wx
import isocket
import images
import cPickle

import wx.lib.mixins.listctrl as listmix

from isocket import log

from StatusBar import *
from config import Config

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

class ICQThreaded(isocket.Protocol):
    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Run(self):
        while self.keepGoing:
            buf = self.read()
            log.packetin(buf)

            ch, b, c = self.readFLAP(buf)
            snac = self.readSNAC(c)
            print 'going to call proc_%d_%d_%d' % (ch, snac[0], snac[1])
            print 'for this snac: ', snac

            tmp = "proc_%d_%d_%d" % (ch, snac[0], snac[1])
            func = getattr(self, tmp)

            func(snac[5])

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
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


class PersistenceMixin:
    def __init__(self, fileName):
        self._fileName = fileName

    def storeGeometry(self):
        fp = open(self._fileName, "wb")
        try:
            pos = self.GetPosition()
            size = self.GetSize()
            cPickle.dump((pos, size), fp)
        except:
            fp.close()
            raise

    def restoreGeometry(self, npos = None, nsize = None):
        pos = None
        size = None
        fp = None
        try:
            fp = open(self._fileName, "rb")
            pos, size = cPickle.load(fp)
        except:
            if fp is not None: fp.close()

        if pos is None: pos = npos
        if size is None: size = nsize

        self.SetPosition(pos)
        self.SetSize(size)
        self.forceVisible()
        self.Layout()

    def forceVisible(self):
        ''' If left upper corner is out of the screen, 
        restore win position to 0, 0. 
        '''

        pos = self.GetPosition()

        if pos[0] < 0: pos = wx.Point(0, pos[1])
        if pos[1] < 0: pos = wx.Point(pos[0], 0)

        self.SetPosition(pos)
        self.Layout()

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
        self.connector.registerProtocol('icq', ICQThreaded())

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
        self.storeGeometry()
        evt.Skip()

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
        self.SetMenuBar(None)
        self.Layout()
        self.Refresh()
        time.sleep(1)
        self.createTopMenuBar()
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
        info.m_text = "Artist"
        self.userList.InsertColumnInfo(0, info)

#        info.m_format = wx.LIST_FORMAT_RIGHT
        info.m_text = "Title"
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

        items = musicdata.items()
        for key, data in items:
            index = self.userList.InsertImageStringItem(sys.maxint, data[0], self.idx1)
            self.userList.SetStringItem(index, 1, data[1])
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
