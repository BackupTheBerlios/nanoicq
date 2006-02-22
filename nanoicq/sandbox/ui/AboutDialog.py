                                                                                                                                    
#
# $Id: AboutDialog.py,v 1.1 2006/02/22 12:44:42 lightdruid Exp $
#

import sys
import wx
import wx.html
import wx.lib.wxpTag
import wx.lib.hyperlink as hl

import version

_ = wx.GetTranslation

class AboutDialog(wx.Dialog):
    credits = [
        ("Filip Muskalski for excellent icon set",  "http://www.a0x.info"),
    ]

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, _("About NanoICQ"),
            style = wx.DEFAULT_DIALOG_STYLE)

        ver = version.version_full_string
        py_ver = sys.version.split()[0]

        sz = wx.StaticBoxSizer(wx.StaticBox(self, -1, ''), wx.VERTICAL)
        sz.Add(wx.StaticText(self, -1, "NanoICQ " + ver), 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sz.Add(wx.StaticText(self, -1, "Running on Python " + py_ver + " and wxPython " + wx.VERSION_STRING), 0, wx.ALIGN_CENTRE|wx.ALL, 0)
        sz.Add(wx.StaticLine(self, -1, style = wx.LI_HORIZONTAL), 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
        sz.Add(wx.StaticText(self, -1, "Credits:"), 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        for c, url in self.credits:
            sh = wx.BoxSizer(wx.HORIZONTAL)
            sh.Add(wx.StaticText(self, -1, c), 0, wx.ALIGN_CENTRE|wx.ALL, 2)
            sh.Add(hl.HyperLinkCtrl(self, -1, url, URL = url), 0, wx.ALIGN_CENTRE|wx.ALL, 2)
            sz.Add(sh, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

        sz.Add(wx.StaticLine(self, -1, style = wx.LI_HORIZONTAL), 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
        sz.Add(hl.HyperLinkCtrl(self, -1, "NanoICQ main page", URL = "http://nanoicq.berlios.de"), 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sz.Add(wx.StaticText(self, -1, "Copyright (C) 2005-2006 Andrey Sidorenko"), 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        sz.Add(wx.Button(self, wx.ID_OK, "Ok"), 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.SetSizer(sz)
        self.SetAutoLayout(True)

        self.CentreOnParent(wx.BOTH)


def _test():
    class TopFrame(wx.Frame):
        def __init__(self, parentFrame, title):
            wx.Frame.__init__(self, parentFrame, -1, title,
                pos=(150, 150), size=(350, 200))

            d = AboutDialog(self)
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
