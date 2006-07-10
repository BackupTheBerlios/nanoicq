#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# $Id: pora.py,v 1.1 2006/07/10 23:29:15 lightdruid Exp $
#

import sys
import traceback

if sys.platform == 'win32':
    import win32con

import wx
import string
import types

from utils import *
from persistence import *
from statusbar import *

from adddatabase import AddDatabaseDialog

ID_ADD_DATABASE = wx.NewId()

ID_HELP = wx.NewId()
ID_ABOUT = wx.NewId()

_topMenu = (
    ("File",
        (
            (ID_ADD_DATABASE, "&Add database", "Add database", "self.onAddDatabase", 0),
            (),
            (wx.ID_EXIT, "E&xit\tAlt-X", "Exit", "self.onExit", 0),
        )
    ),
    ("Help",
        (
            (ID_HELP, "Help\tF1", "Help", "self.onHelp", 0),
            (ID_ABOUT, "About", "About", "self.onAbout", 0),
        )
    ),
)


class TopFrame(wx.Frame, PersistenceMixin):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
            pos=(150, 150), size=(350, 200))
        PersistenceMixin.__init__(self, self, "frame.position")

        self.createTopMenuBar()
        self.createTopPanel()
        self.createStatusbar()
        # ---

    def onAddDatabase(self, evt):
        d = AddDatabaseDialog(self, "")
        d.Show()

    def createTopPanel(self):
        self.topPanel = TopPanel(self)

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

    def createStatusbar(self):
        self.sb = CustomStatusBar(self)
        self.SetStatusBar(self.sb)

    def onClose(self, evt):
        evt.Skip()
        self.storeGeometry()

        for d in self._dialogs:
            d.storeWidgets()

            # We need to explicitly destroy frames because they
            # done't have parents
            d.Destroy()


    def onExit(self, *evts):
        self.storeGeometry()
        self.Close()

    def onHelp(self, evt):
        evt.Skip()

    def onAbout(self, evt):
        evt.Skip()
        ad = AboutDialog(self)
        ad.Show()


class TopPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.topPanelSizer = wx.BoxSizer(wx.VERTICAL)

        # ---
        self.SetSizer(self.topPanelSizer)


def main(args = []):
    class PoraApp(wx.App):
        def OnInit(self):
            frame = TopFrame(None, "pora")
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    wx.InitAllImageHandlers()
    app = PoraApp(redirect = False)
    app.MainLoop()

if __name__ == '__main__':
    main(sys.argv[1:])

# ---

