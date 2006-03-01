
#
# $Id: Register.py,v 1.4 2006/03/01 00:33:13 lightdruid Exp $
#

import sys

import wx

sys.path.insert(0, '../..')
from events import *
from iconset import IconSet
from utils import *
from Captcha import CaptchaPanel


class ProcessingTimer(wx.Timer):
    _subs = []

    def subscribe(self, subscriber):
        self._subs.append(subscriber)

    def Notify(self):
        for sub in self._subs:
            sub.notify()


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

        #sizer = wx.BoxSizer(wx.VERTICAL)

        #p = wx.Panel(self, -1)

        cp = CaptchaPanel(self, self.iconSet, img)
        #sizer.Add(cp, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 5)

        #self.SetSizer(sizer)
        #self.SetAutoLayout(True)

        self.Bind(EVT_SEND_CAPTCHA_TEXT, self.onSendCaptchaText)

    def onSendCaptchaText(self, evt):
        print 'WIZARD: onSendCaptchaText'
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
