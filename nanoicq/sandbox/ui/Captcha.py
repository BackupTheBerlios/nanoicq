
#
# $Id: Captcha.py,v 1.13 2006/08/28 15:25:52 lightdruid Exp $
#

import sys
import thread
import time

import wx
import wx.lib.newevent

sys.path.insert(0, '../..')
from events import *
from iconset import IconSet
from utils import *
from icq import log

(_UpdateEvent, EVT_UPDATE_EVENT) = wx.lib.newevent.NewEvent()

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


class LengthValidator(wx.PyValidator):
    ''' Check length of the control's value, it must be validated
        by 'constraint' function, something like this one:
            lambda x : x < 7 - value can't be longer than 7 characters
    '''
    def __init__(self, constraint):
        wx.PyValidator.__init__(self)
        self._constraint = constraint
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return LengthValidator(self._constraint)

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        if not self._constraint(len(text)):
            wx.MessageBox("Password is too long (7 characters max)", "Password")
            return False
        else:
            return True

    def OnChar(self, event):
        key = event.KeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if self._constraint(len(self.GetWindow().GetValue())):
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()


class CaptchaPanel(wx.Panel):
    ID_TEXT = wx.NewId()
    ID_PASS = wx.NewId()
    ID_CONTINUE1 = wx.NewId()
    ID_CONTINUE2 = wx.NewId()
    ID_FINISH = wx.NewId()

    protocolList = ["ICQ"]
    count = 0
    MC = 100

    def __init__(self, parent, connector, iconSet, img = wx.NullBitmap):
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)

        self.connector = connector

        self.protocol = wx.ComboBox(self, -1, self.protocolList[0], size = (110, -1), choices = self.protocolList, style = wx.CB_READONLY)
        self.button1 = wx.Button(self, self.ID_CONTINUE1, "Continue")
        sizer.Add(self.protocol, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.button1, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.bmp = wx.StaticBitmap(self, -1, img)
        sizer.Add(self.bmp, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        txt = 'Please retype letters from the picture above:'
        self.text = wx.TextCtrl(self, self.ID_TEXT, "")
        self.label1 = wx.StaticText(self, -1, txt)
        sizer.Add(self.label1, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.text, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.password = wx.TextCtrl(self, self.ID_PASS, "",
            validator = LengthValidator(lambda x : x < 7))
        self.label2 = wx.StaticText(self, -1, 'Choose password (up to 7 characters):')
        sizer.Add(self.label2, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.password, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.button2 = wx.Button(self, self.ID_CONTINUE2, "Continue")
        sizer.Add(self.button2, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.status = wx.StaticText(self, -1, '')
        sizer.Add(self.status, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.newUin = wx.TextCtrl(self, self.ID_TEXT, "", style = wx.BORDER_NONE)
        self.newUin.SetEditable(False)
        self.newPassword = wx.TextCtrl(self, self.ID_TEXT, "", style = wx.BORDER_NONE)
        self.newPassword.SetEditable(False)

        sizer.Add(self.newUin, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.newPassword, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.button3 = wx.Button(self, self.ID_FINISH, "Finish")
        sizer.Add(self.button3, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        #self.status = wx.StaticText(self, -1, '')
        #sizer.Add(self.status, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.bmp.Hide()
        self.text.Hide()
        self.label1.Hide()
        self.button2.Hide()

        self.label2.Hide()
        self.password.Hide()

        self.status.Hide()
        self.button3.Hide()

        self.newUin.Hide()
        self.newPassword.Hide()

        # ---
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.button1.SetFocus()

        self.Bind(wx.EVT_TEXT, self.onPasswordText, id = self.ID_PASS)
        self.Bind(wx.EVT_TEXT_ENTER, self.postPictureText, id = self.ID_TEXT)
        self.Bind(wx.EVT_BUTTON, self.onButton)

        self.Bind(EVT_REGISTRATION_ERROR, self.onRegistrationError)

        self.Bind(wx.EVT_TIMER, self.onTimer)

    def onRegistrationError(self, evt):
        print 'onRegistrationError'

    def onTimer(self, evt):
        del self.busy
        self.timer.Stop()

    def onButton(self, evt):
        evt.Skip()

        if evt.GetId() == self.ID_CONTINUE1:
            self.stage2StartProcessing()
        elif evt.GetId() == self.ID_CONTINUE2:
            self.stage3StartProcessing()

    def stage3StartProcessing(self):
        self.button2.Enable(False)
        self.Layout()

        # This is gust a guard, so if we didn't receive any response
        # from server in 5 secs, just give up
        self.timer = wx.Timer(self)
        self.timer.Start(5000)

        self.busy = wx.BusyInfo("One moment ...")
        wx.Yield()

        self.connector.registrationImageResponse(self.text.GetValue(),
            self.password.GetValue())

    def stage3StopProcessing(self, newUin):
        self.text.Enable(False)
        self.password.Enable(False)
        self.status.SetLabel("Registration complete, your UIN and password:")

        self.newUin.SetValue(newUin)
        self.newPassword.SetValue(self.password.GetValue())

        self.newUin.Show()
        self.newPassword.Show()

        self.showStage3()

    def stage2StartProcessing(self):
        self.button1.Enable(False)
        self.Layout()

        busy = wx.BusyInfo("One moment ...")
        wx.Yield()

        attempts = 0
        maxAttempts = 5
        while True:
            try:
                attempts += 1
                self.startRegistration()
                break
            except Exception, exc:
                if attempts >= maxAttempts:
                    msg = "Unable to login to server: " + str(exc)
                    log().log(msg)
                    del busy
                    raise Exception(msg)
                log().log("Unsuccessful attempt, trying one more time: " + str(exc))
                time.sleep(1)

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
        self.label1.Show(flag)
        self.button2.Show(flag)
        self.button2.Enable(False)
        self.label2.Show(flag)
        self.password.Show(flag)
        self.text.SetFocus()
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
        log().log('Posting captcha text (%s)...' % str(txt))

    def onPasswordText(self, evt):
        evt.Skip()
        self.button2.Enable(len(self.password.GetValue()) > 0)

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

