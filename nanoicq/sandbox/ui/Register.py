
#
# $Id: Register.py,v 1.1 2006/02/28 14:45:11 lightdruid Exp $
#

import sys

import wx
import  wx.wizard as wiz

sys.path.insert(0, '../..')
from events import *
from iconset import IconSet
from utils import *
from Captcha import CaptchaPanel


def makePageTitle(wizPg, title):
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)

    font = wizPg.GetFont()
    font.SetPointSize(font.GetPointSize() + 2)
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    title.SetFont(font)

    sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 3)
    sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND | wx.ALL, 3)

    return sizer


class TitledPage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
        self.sizer = makePageTitle(self, title)


class ProcessingTimer(wx.Timer):
    _subs = []

    def subscribe(self, subscriber):
        self._subs.append(subscriber)

    def Notify(self):
        for sub in self._subs:
            sub.notify()


class ImagePage(wiz.WizardPageSimple):
    MC = 100
    count = 0

    def __init__(self, parent, title, iconSet, img):
        wiz.WizardPageSimple.__init__(self, parent)
        self.sizer = makePageTitle(self, title)

        self.panel = CaptchaPanel(self, iconSet, img)
        self.sizer.Add(self.panel, 0, wx.ALL | wx.ALIGN_CENTER, 3)

        self.g = wx.Gauge(self, -1, self.MC, size = (-1, 5), style = wx.GA_SMOOTH)
        self.g.SetBezelFace(0)
        self.g.SetShadowWidth(0)

        self.sizer.Add(self.g, 0, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER, 5)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

        self._timer = ProcessingTimer()
        self._timer.subscribe(self)

    def notify(self):
        self.count = self.count + 1

        if self.count >= self.MC:
            self.count = 0

        self.g.SetValue(self.count)

    def startProcessing(self):
        self._timer.Start(10)

    def stopProcessing(self):
        self._timer.Stop()


class RegisterWizard(wiz.Wizard):
    def __init__(self, parentFrame, ID, title = 'New UIN registration'):

        wiz.Wizard.__init__(self, None, ID, title = title)

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

        page1 = TitledPage(self, "Choose protocol")
        page2 = ImagePage(self, "Confirmation", self.iconSet, img)

        self.page1Id = page1.GetId()
        self.page2Id = page2.GetId()

        page1.SetNext(page2)
        page2.SetPrev(page1)

        self.Bind(wiz.EVT_WIZARD_PAGE_CHANGED, self.onWizPageChanged)

        if self.RunWizard(page1):
            print 'Ok'
        else:
            print 'Cancelled'

    def onWizPageChanged(self, evt):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()
        if hasattr(page, "startProcessing"):
            page.startProcessing()
        print "OnWizPageChanged: %s, %s\n" % (dir, page.__class__)


def _test():
    class NanoApp(wx.App):
        def OnInit(self):
            frame = wx.Frame(None, -1)
            r = RegisterWizard(frame, -1)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
