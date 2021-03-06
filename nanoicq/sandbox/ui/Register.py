
#
# $Id: Register.py,v 1.10 2006/11/24 13:35:19 lightdruid Exp $
#

import sys

import wx

sys.path.insert(0, '../..')
from events import *
from iconset import IconSet
from utils import *
from Captcha import CaptchaPanel


class RegisterFrame(wx.Frame):
    def __init__(self, parentFrame, ID, connector, iconSet,
        xmlConfig, title = 'New UIN registration'):

        wx.Frame.__init__(self, None, ID, title = title, size = (300, 490))

        self.connector = connector
        self._xmlConfig = xmlConfig

        self.iconSet = iconSet
        self.mainIcon = wx.EmptyIcon()
        self.mainIcon.CopyFromBitmap(self.iconSet['main'])
        self.SetIcon(self.mainIcon)

        self.cp = CaptchaPanel(self, connector, self.iconSet)

        self.Bind(EVT_GOT_NEW_UIN, self.onGotNewUin)
        self.Bind(EVT_GOT_CAPTCHA, self.onGotCaptcha)
        self.Bind(wx.EVT_BUTTON, self.onFinishButton, id = CaptchaPanel.ID_FINISH)

    def onFinishButton(self, evt):
        evt.Skip()
        rc = wx.MessageBox("Save this UIN and password in your config file?",
            "Save", wx.YES_NO)
        if rc == wx.YES:
            self._xmlConfig.set("./Options/Network/ICQ/ICQNumber", self.cp.newUin.GetValue())
            self._xmlConfig.set("./Options/Network/ICQ/ICQPassword", self.cp.newPassword.GetValue())
            self._xmlConfig.save()
        self.Close()

    def onGotNewUin(self, evt):
        self.cp.stage3StopProcessing(evt.getVal())

    def onGotCaptcha(self, evt):
        self.cp.stage2StopProcessing(evt.getVal())


def _test():
    class NanoApp(wx.App):
        def OnInit(self):
            connector = None
            iconSetName = 'aox'
            self.iconSet = IconSet()
            self.iconSet.addPath('icons/' + iconSetName)
            self.iconSet.loadIcons()
            self.iconSet.setActiveSet(iconSetName)
            frame = RegisterFrame(None, -1, connector, self.iconSet)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
