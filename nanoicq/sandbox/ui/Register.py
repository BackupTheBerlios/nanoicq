
#
# $Id: Register.py,v 1.5 2006/03/01 12:16:14 lightdruid Exp $
#

import sys

import wx

sys.path.insert(0, '../..')
from events import *
from iconset import IconSet
from utils import *
from Captcha import CaptchaPanel


class RegisterFrame(wx.Frame):
    def __init__(self, parentFrame, ID, connector, title = 'New UIN registration'):

        wx.Frame.__init__(self, None, ID, title = title, size = (300, 450))

        self.connector = connector

        self.iconSet = IconSet()
        self.iconSet.addPath('icons/aox')
        self.iconSet.loadIcons()
        self.iconSet.setActiveSet('aox')            

        self.mainIcon = wx.EmptyIcon()
        self.mainIcon.CopyFromBitmap(self.iconSet['main'])
        self.SetIcon(self.mainIcon)

        import cStringIO
        tlvs = restoreFromFile('tlvs.req')
        img = wx.ImageFromStream(cStringIO.StringIO(tlvs))

        self.cp = CaptchaPanel(self, connector, self.iconSet, img)

        self.Bind(EVT_SEND_CAPTCHA_TEXT, self.onSendCaptchaText)
        self.Bind(EVT_GOT_CAPTCHA, self.onGotCaptcha)

    def onGotCaptcha(self, evt):
        self.cp.stage2StopProcessing(evt.getVal())

    def onSendCaptchaText(self, evt):
        print 'onSendCaptchaText'
        #self.currentPage.startProcessing()

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
