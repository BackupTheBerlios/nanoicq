
#
# $Id: Captcha.py,v 1.1 2006/02/28 13:33:02 lightdruid Exp $
#

import sys

import wx

sys.path.insert(0, '../..')
from events import *
from iconset import IconSet
from utils import *


class CaptchaPanel(wx.Panel):
    ID_TEXT = wx.NewId()

    def __init__(self, parent, iconSet, img):
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)

        self.bmp = wx.StaticBitmap(self, -1, img.ConvertToBitmap())
        sizer.Add(self.bmp, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        txt = 'Please retype letters from the picture above:'
        self.text = wx.TextCtrl(self, self.ID_TEXT, "")
        self.button = wx.Button(self, wx.ID_OK, "Ok")
        sizer.Add(wx.StaticText(self, -1, txt), 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.text, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(self.button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.button.Enable(False)

        # ---
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_TEXT, self.onText)
        self.Bind(wx.EVT_TEXT_ENTER, self.postPictureText)
        self.Bind(wx.EVT_BUTTON, self.postPictureText, id = self.button.GetId())

    def postPictureText(self, evt):
        evt.Skip()
        txt = self.text.GetValue()
        if len(txt) == 0:
            return
        print 'Posting captcha text (%s)...' % txt

    def onText(self, evt):
        evt.Skip()
        self.button.Enable(len(self.text.GetValue()) > 0)

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
            frame = CaptchaFrame(None, -1)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
