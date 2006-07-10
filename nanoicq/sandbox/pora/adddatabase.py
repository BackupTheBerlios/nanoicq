#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# $Id: adddatabase.py,v 1.1 2006/07/10 23:29:15 lightdruid Exp $
#

import sys
import traceback

import wx
import wx.lib.rcsizer as rcs
import string
import types

from utils import *
from persistence import *

class AddDatabaseDialog(wx.Dialog, PersistenceMixin):

    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, -1, title,
            pos=(150, 150), size=(550, 400), style = wx.DD_DEFAULT_STYLE | wx.RESIZE_BORDER)
        PersistenceMixin.__init__(self, self, "adddialog.position")

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.cbDataBaseName = wx.ComboBox(
            self, -1, style = wx.CB_DROPDOWN)

        self.sizer.Add(wx.StaticText(self, -1, "Please enter database name"), 0, wx.ALL | wx.EXPAND, 5)
        self.sizer.Add(self.cbDataBaseName, 0, wx.ALL | wx.EXPAND, 5)

        box1 = wx.StaticBox(self, -1, "Database")
        self.bsizer1 = wx.StaticBoxSizer(box1, wx.VERTICAL)
        box2 = wx.StaticBox(self, -1, "Operating system")
        self.bsizer2 = wx.StaticBoxSizer(box2, wx.VERTICAL)

        self.createLeftPane(self.bsizer1)
        self.createRightPane(self.bsizer2)

        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer.Add(self.bsizer1, 1, wx.ALL, 5)
        self.hsizer.Add(self.bsizer2, 1, wx.ALL, 5)

        self.sizer.Add(self.hsizer, 1, wx.ALL | wx.EXPAND, 5)

        #self.sizer.Add(wx.StaticLine(self, -1, style = wx.LI_HORIZONTAL), 0, wx.ALL | wx.EXPAND | wx.ALIGN_TOP, 0)
        self.sizer.Add(self.createBottomPane(), 0, wx.ALL | wx.ALIGN_RIGHT, 5)        

        #
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Fit()
        # ---

    def createBottomPane(self):
        self.btnOk = wx.Button(self, -1, "Ok")
        self.btnCancel = wx.Button(self, -1, "Cancel")
        self.btnHelp = wx.Button(self, -1, "Help")

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.btnOk, 0, wx.ALL, 5)
        hsizer.Add(self.btnCancel, 0, wx.ALL, 5)
        hsizer.Add(self.btnHelp, 0, wx.ALL, 5)
        return hsizer

    def createLeftPane(self, sizer):
        sizer.Add(wx.StaticText(self, -1, "Please enter instance connection parameters"), 0, wx.ALL, 5)

        gbs = rcs.RowColSizer()

        self.cbUserName = wx.ComboBox(self, -1)#, style = wx.CB_DROPDOWN)
        gbs.Add(wx.StaticText(self, -1, "User name"), row = 0, col = 0, flag = wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self.cbUserName, row = 0, col = 2, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self.tbPassword = wx.TextCtrl(self, -1, "", style = wx.TE_PASSWORD)
        gbs.Add(wx.StaticText(self, -1, "Password"), row = 1, col = 0, flag = wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self.tbPassword, row = 1, col = 2, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self.chConnectAs = wx.Choice(self, -1, choices = ["normal"])
        gbs.Add(wx.StaticText(self, -1, "Connect as"), row = 2, col = 0, flag = wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self.chConnectAs, row = 2, col = 2, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self.chConnectUsing = wx.Choice(self, -1, choices = ["sampleList"])
        gbs.Add(wx.StaticText(self, -1, "Connect using"), row = 3, col = 0, flag = wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self.chConnectUsing, row = 3, col = 2, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self.cbTNSName = wx.ComboBox(self, -1)#, style = wx.CB_DROPDOWN)
        gbs.Add(wx.StaticText(self, -1, "TNS name"), row = 4, col = 0, flag = wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self.cbTNSName, row = 4, col = 2, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        sizer.Add(gbs, 0, wx.ALL, 5)

    def onCollectOSInfoChecked(self, evt):
        evt.Skip()
        self.enableCollectInfoControls(evt.Checked())

    def createRightPane(self, sizer):
        self.cbCollectOSInfo = wx.CheckBox(self, -1, "Collect operation system data")
        self.Bind(wx.EVT_CHECKBOX, self.onCollectOSInfoChecked, self.cbCollectOSInfo)
        sizer.Add(self.cbCollectOSInfo, 1, wx.ALL, 5)

        self.cbCollectOSInfoControls = []

        gbs = rcs.RowColSizer()

        self.cbHost = wx.ComboBox(self, -1)#, style = wx.CB_DROPDOWN)
        gbs.Add(wx.StaticText(self, -1, "Host"), row = 0, col = 0, flag = wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self.cbHost, row = 0, col = 2, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self.chOSType = wx.Choice(self, -1, choices = ["Windows"])
        gbs.Add(wx.StaticText(self, -1, "OS Type"), row = 1, col = 0, flag = wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self.chOSType, row = 1, col = 2, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self.cbOSUserName = wx.ComboBox(self, -1)#, style = wx.CB_DROPDOWN)
        gbs.Add(wx.StaticText(self, -1, "User name"), row = 3, col = 0, flag = wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self.cbOSUserName, row = 3, col = 2, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self.tbOSPassword = wx.TextCtrl(self, -1, "", style = wx.TE_PASSWORD)
        gbs.Add(wx.StaticText(self, -1, "Password"), row = 4, col = 0, flag = wx.ALIGN_CENTER_VERTICAL)
        gbs.Add(self.tbOSPassword, row = 4, col = 2, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self.cbCollectOSInfoControls.append(self.cbHost.GetId())
        self.cbCollectOSInfoControls.append(self.chOSType.GetId())
        self.cbCollectOSInfoControls.append(self.cbOSUserName.GetId())
        self.cbCollectOSInfoControls.append(self.tbOSPassword.GetId())

        self.enableCollectInfoControls(False)

        sizer.Add(gbs, 0, wx.ALL, 5)

    def enableCollectInfoControls(self, flag):
        for c in self.cbCollectOSInfoControls:
            self.FindWindowById(c).Enable(flag)


def _test():
    class TopFrame(wx.Frame):
        def __init__(self, parentFrame, title):
            wx.Frame.__init__(self, parentFrame, -1, title,
                pos=(150, 150), size=(350, 200))

            d = AddDatabaseDialog(self, "")
            d.Show()

    class NanoApp(wx.App):
        def OnInit(self):
            frame = TopFrame(None, "NanoICQ")
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()


# ---

