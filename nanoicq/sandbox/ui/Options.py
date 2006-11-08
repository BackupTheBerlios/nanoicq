
#
# $Id: Options.py,v 1.1 2006/11/08 09:58:54 lightdruid Exp $
#

import sys
import string

import wx
import wx.lib.rcsizer as rcs
import wx.lib.mixins.listctrl as listmix
import wx.lib.hyperlink as hyperlink

sys.path.insert(0, '../..')
from events import *
from buddy import Buddy
from iconset import IconSet
from utils import *

_ID_OK_BUTTON = wx.NewId()

class OptionsNB(wx.Notebook):
    def __init__(self, parent, id):
        wx.Notebook.__init__(self, parent, id, size=(21,21),
                             style=
                             wx.NB_TOP | wx.NB_MULTILINE
                             #wx.NB_BOTTOM
                             #wx.NB_LEFT
                             #wx.NB_RIGHT
                             )

class Pane_General(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Pane_ICQ(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)


class OptionsPanel(wx.Panel):
    _head = [
        'General', 'ICQ'
    ]

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        sz = wx.BoxSizer(wx.VERTICAL)
        self.nb = OptionsNB(self, -1)

        for h in self._head:
            try:
                win = eval("Pane_%s(self.nb)" % h)
                self.nb.AddPage(win, h)
            except NameError, msg:
                print msg
                raise

        self.nb.Layout()

        hz = wx.BoxSizer(wx.HORIZONTAL)
        self.cancelButton = wx.Button(self, -1, 'Cancel')
        self.okButton = wx.Button(self, _ID_OK_BUTTON, 'Ok')
        hz.Add(self.cancelButton, 0, wx.ALL, 1)
        hz.Add(self.okButton, 0, wx.ALL | wx.ALIGN_RIGHT, 1)

        sz.Add(self.nb, 7, wx.EXPAND | wx.ALL, 5)
        sz.Add(hz, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        self.SetSizer(sz)
        self.SetAutoLayout(True)

class OptionsFrame(wx.Frame):
    def __init__(self, parentFrame, ID, title = 'Options',
            size = (370, 280), pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE 
                | wx.MAXIMIZE_BOX 
                | wx.MINIMIZE_BOX
                | wx.RESIZE_BORDER
                ):

        wx.Frame.__init__(self, parentFrame, ID, size = size, style = style,
            title = title)

        self.panel = OptionsPanel(self)


def _test():
    class NanoApp(wx.App):
        def OnInit(self):

            frame = OptionsFrame(None, -1)
            self.SetTopWindow(frame)
            frame.CentreOnParent()
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
