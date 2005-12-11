#!/usr/bin/python

#
# $Id: wxnanoicq.py,v 1.4 2005/12/11 12:18:26 lightdruid Exp $
#

import sys
sys.path.insert(0, '../..')

import thread
import time
import wx
import isocket
import images

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

class TopFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
            pos=(150, 150), size=(350, 200))

        self.createTopMenuBar()
        self.makeStatusbar()

        icon = self.prepareIcon(images.getLimeWireImage())
        self.SetIcon(icon)

        # ---
        self.config = Config()
        self.config.read('sample.config')

        self.connector = Connector()
        self.connector.setConfig(self.config)
        self.connector.registerProtocol('icq', ICQThreaded())

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

    def OnExit(self, *evts):
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

class NanoApp(wx.App):
    def OnInit(self):
        frame = TopFrame(None, "NanoICQ")
        self.SetTopWindow(frame)
        frame.Show(True)
        return True
        
app = NanoApp(redirect = False)
app.MainLoop()


# ---
