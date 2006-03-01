
#
# $Id: Register.py,v 1.7 2006/03/01 15:17:10 lightdruid Exp $
#

import sys

import wx

sys.path.insert(0, '../..')
from events import *
from iconset import IconSet
from utils import *
from Captcha import CaptchaPanel


class RegisterFrame(wx.Frame):
    def __init__(self, parentFrame, ID, connector, iconSet, title = 'New UIN registration'):
        wx.Frame.__init__(self, None, ID, title = title, size = (300, 450))

        self.connector = connector

        self.iconSet = iconSet
        self.mainIcon = wx.EmptyIcon()
        self.mainIcon.CopyFromBitmap(self.iconSet['main'])
        self.SetIcon(self.mainIcon)

        self.cp = CaptchaPanel(self, connector, self.iconSet)

        self.Bind(EVT_GOT_NEW_UIN, self.onGotNewUin)
        self.Bind(EVT_GOT_CAPTCHA, self.onGotCaptcha)

    def onGotNewUin(self, evt):
        self.cp.stage3StopProcessing(evt.getVal())

    def onGotCaptcha(self, evt):
        self.cp.stage2StopProcessing(evt.getVal())


def _test():
    class NanoApp(wx.App):
        def OnInit(self):
            connector = None
            frame = RegisterFrame(None, -1, connector)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
