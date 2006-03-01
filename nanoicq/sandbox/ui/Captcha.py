
#
# $Id: Captcha.py,v 1.5 2006/03/01 12:16:14 lightdruid Exp $
#

import sys
import thread

import wx
import wx.lib.newevent

sys.path.insert(0, '../..')
from events import *
from iconset import IconSet
from utils import *

(_UpdateEvent, EVT_UPDATE_EVENT) = wx.lib.newevent.NewEvent()

class ProcessingTimer(wx.Timer):
    _subs = []

    def __init__(self, ids):
        wx.Timer.__init__(self)
        self._ids = ids

    def subscribe(self, subscriber):
        self._subs.append(subscriber)

    def Notify(self):
        for sub in self._subs:
            sub.notify(self._ids)

class ConnectThread:
    def __init__(self, win):
        self.win = win

    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Run(self):
        sleeptime = 0.01

        while self.keepGoing:
            #print 'Run'
            evt = _UpdateEvent()
            wx.PostEvent(self.win, evt)
            time.sleep(sleeptime)

        self.running = False


class CaptchaPanel(wx.Panel):
    ID_TEXT = wx.NewId()
    ID_CONTINUE1 = wx.NewId()
    ID_CONTINUE2 = wx.NewId()
    ID_FINISH = wx.NewId()

    protocolList = ["ICQ"]
    count = 0
    MC = 100

    def __init__(self, parent, connector, iconSet, img):
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)

        self.connector = connector

        self.protocol = wx.ComboBox(self, -1, self.protocolList[0], size = (110, -1), choices = self.protocolList, style = wx.CB_READONLY)
        self.g1 = wx.Gauge(self, -1, size = (-1, 5), style = wx.GA_SMOOTH)
        self.button1 = wx.Button(self, self.ID_CONTINUE1, "Continue")
        sizer.Add(self.protocol, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.button1, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.g1, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.bmp = wx.StaticBitmap(self, -1, img.ConvertToBitmap())
        sizer.Add(self.bmp, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        txt = 'Please retype letters from the picture above:'
        self.text = wx.TextCtrl(self, self.ID_TEXT, "")
        self.label = wx.StaticText(self, -1, txt)
        sizer.Add(self.label, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.text, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.g2 = wx.Gauge(self, -1, size = (-1, 5), style = wx.GA_SMOOTH)
        self.button2 = wx.Button(self, self.ID_CONTINUE2, "Continue")
        sizer.Add(self.button2, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.g2, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.status = wx.StaticText(self, -1, '')
        sizer.Add(self.status, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.button3 = wx.Button(self, self.ID_FINISH, "Finish")
        sizer.Add(self.button3, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.bmp.Hide()
        self.text.Hide()
        self.label.Hide()
        self.g1.Hide()
        self.button2.Hide()

        self.status.Hide()
        self.g2.Hide()
        self.button3.Hide()

        # ---
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_TEXT, self.onText)
        self.Bind(wx.EVT_TEXT_ENTER, self.postPictureText)

        self.Bind(wx.EVT_BUTTON, self.onButton)
#        self.Bind(EVT_UPDATE_EVENT, self.onUpdateEvent)
#
#    def onUpdateEvent(self, evt):
#        evt.Skip()
#        self.notify(self.g1.GetId())

    def onButton(self, evt):
        evt.Skip()
        self.currentEventId = evt.GetId()

        if evt.GetId() == self.ID_CONTINUE1:
            #self.showStage2()
            self.stage2StartProcessing()
        elif evt.GetId() == self.ID_CONTINUE2:
            self.showStage3()

    def stage2StartProcessing(self):
        self.button1.Enable(False)
        self.Layout()

        busy = wx.BusyInfo("One moment ...")
        wx.Yield()

        self.startRegistration()

    def startRegistration(self):
        self.connector.sendHelloServer()

    def stage2StopProcessing(self, captchaImage):
        self._setCaptchaImage(captchaImage.ConvertToBitmap())
        self.showStage2()

    def _setCaptchaImage(self, captchaImage):
        self.bmp.SetBitmap(captchaImage)

    def showStage2(self, flag = True):
        if flag:
            tf = 'Done'
        else:
            tf = 'Continue'
        self.button1.SetLabel(tf)
        self.bmp.Show(flag)
        self.text.Show(flag)
        self.label.Show(flag)
        self.button2.Show(flag)
        self.Layout()

    def showStage3(self, flag = True):
        if flag:
            tf = 'Done'
        else:
            tf = 'Continue'
        self.button2.SetLabel(tf)
        self.status.Show(flag)
        self.button3.Show(flag)
        self.Layout()

    def postPictureText(self, evt):
        evt.Skip()
        txt = self.text.GetValue()
        if len(txt) == 0:
            return
        print 'Posting captcha text (%s)...' % txt


    def onText(self, evt):
        evt.Skip()
#        self.button.Enable(len(self.text.GetValue()) > 0)

class CaptchaFrame(wx.Frame):
    def __init__(self, parentFrame, ID, title = 'New UIN registration',
            size = (300, 240), 
            pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX  | wx.MINIMIZE_BOX):

        wx.Frame.__init__(self, None, ID, size = size, style = style,
            title = title)

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
        self.panel = CaptchaPanel(self, self.iconSet, img)

def _test():
    class NanoApp(wx.App):
        def OnInit(self):
            #frame = CaptchaFrame(None, -1)
            #self.SetTopWindow(frame)
            #frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
