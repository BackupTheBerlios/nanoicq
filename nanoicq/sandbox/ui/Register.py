
#
# $Id: Register.py,v 1.8 2006/03/01 16:29:09 lightdruid Exp $
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
            title = 'New UIN registration', config):

        wx.Frame.__init__(self, None, ID, title = title, size = (300, 490))

        self.connector = connector
        self.config = config

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
            self.config.set('icq', 'uin', self.cp.newUin.GetValue())
            self.config.set('icq', 'password', self.cp.newPassword.GetValue())
            self.config.write()
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
