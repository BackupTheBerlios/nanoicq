
#
# $Id: Options.py,v 1.2 2006/11/08 11:48:32 lightdruid Exp $
#

import elementtree.ElementTree as ET

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
_ID_CANCEL_BUTTON = wx.NewId()


class OptionsNB(wx.Notebook):
    def __init__(self, parent, id):
        wx.Notebook.__init__(self, parent, id,
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

class Pane_UI(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)


class Pane_Network(wx.Panel):
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

        sz.Add(wx.TextCtrl(self, -1, "asddddddddddddd"))

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class OptionsTree(wx.TreeCtrl):
    def __init__(self, parent, id):
        wx.TreeCtrl.__init__(self, parent, id)

        fn = "options.xml"
        tree = ET.parse(fn)
        root = tree.getroot()
        print dir(root), root.tag

        if root.tag != "nanoicq":
            raise Exception("Wrong XML format in '%d'" % fn)

        child = root.getchildren()[0]
        if child.tag != "options":
            raise Exception("Wrong XML format in '%d'" % fn)

        #parent_map = dict((c, p) for p in children.getiterator() for c in p)
        #print parent_map

        #self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onActivate, self)

        self.root = self.AddRoot("/")
        self.SetPyData(self.root, None)

        self._panes = {}

        if 1:
            for c in child.getchildren():
                print c.tag, c.attrib
                predef = False
                try:
                    predef = int(c.attrib["Prefedined"]) == 1
                except KeyError:
                    pass

                if predef:
                    ch = self.AppendItem(self.root, c.tag)
                    self.SetPyData(ch, c.tag)
                    self._panes[c.tag] = None

                    for d in c.getchildren():
                        predef = False
                        try:
                            predef = int(d.attrib["Prefedined"]) == 1
                        except KeyError:
                            pass

                        if predef:
                            dh = self.AppendItem(ch, d.tag)
                            self.SetPyData(dh, d.tag)
                            self._panes[d.tag] = None

                self.Expand(ch)

        self.Expand(self.root)
        return

        for x in range(15):
            child = self.AppendItem(self.root, "Item %d" % x)
            self.SetPyData(child, None)
            break

            for y in range(5):
                last = self.AppendItem(child, "item %d-%s" % (x, chr(ord("a")+y)))
                self.SetPyData(last, None)

                for z in range(5):
                    item = self.AppendItem(last,  "item %d-%s-%d" % (x, chr(ord("a")+y), z))
                    self.SetPyData(item, None)

    def getPanes(self):
        return self._panes


class OptionsPanel(wx.Panel):
    _head = [
        'General', 'ICQ'
    ]

    _dirty = False
    _activePane = None

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self._parent = parent

        sz = wx.BoxSizer(wx.VERTICAL)
        self.tree = OptionsTree(self, -1)
        self.pane = wx.Panel(self, -1)

        self.tz = wx.BoxSizer(wx.HORIZONTAL)
        self.tz.Add(self.tree, 1, wx.ALL | wx.EXPAND, 5)
        self.tz.Add(self.pane, 3, wx.ALL | wx.EXPAND, 5)

        hz = wx.BoxSizer(wx.HORIZONTAL)
        self.cancelButton = wx.Button(self, _ID_CANCEL_BUTTON, 'Cancel')
        self.okButton = wx.Button(self, _ID_OK_BUTTON, 'Ok')
        hz.Add(self.cancelButton, 0, wx.ALL, 1)
        hz.Add(self.okButton, 0, wx.ALL | wx.ALIGN_RIGHT, 1)

        sz.Add(self.tz, 7, wx.EXPAND | wx.ALL, 5)
        sz.Add(hz, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        self.okButton.Enable(False)

        self.Bind(wx.EVT_BUTTON, self.onOkButton, id = _ID_OK_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.onCancelButton, id = _ID_CANCEL_BUTTON)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelChanged, self.tree)

        self.SetSizer(sz)
        self.SetAutoLayout(True)

        # Create panes
        panes_t = self.tree.getPanes()
        self.panes = {}
        for p in panes_t:
            self.panes[p] = self.createPane(p)
            self.panes[p].Hide()
            print self.panes[p], p

        self._currentData = None

    def onOkButton(self, evt):
        pass

    def onCancelButton(self, evt):
        self._parent.Close()

    def updateDirty(self, flag = None):
        if flag is not None:
            self._dirty = flag
        self.okButton.Enable(self._dirty == True)

    def createPane(self, name):
        return eval("Pane_%s(self)" % name)

    def onSelChanged(self, evt):
        print evt
        item = evt.GetItem()
        data = self.tree.GetPyData(item)
        print 'data', data

        if data is None:
            if self.pane is not None:
                self.pane.Hide()
                self.tz.Detach(self.pane)
                #self.panes[data].Hide()
                pass
            return

        if self.pane is not None:
            if self._currentData is None:
            #self.pane.Close()
                self.tz.Detach(self.pane)
                self.pane.Hide()
            else:
                self.tz.Detach(self.panes[self._currentData])
                self.panes[self._currentData].Hide()


        self._currentData = data
        
        self.tz.Add(self.panes[data], 3, wx.ALL | wx.EXPAND, 5)
        self.panes[data].Show()
        self.tz.Layout()
        self.Layout()

class OptionsPanel1(wx.Panel):
    _head = [
        'General', 'ICQ'
    ]

    _dirty = False

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self._parent = parent

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
        self.cancelButton = wx.Button(self, _ID_CANCEL_BUTTON, 'Cancel')
        self.okButton = wx.Button(self, _ID_OK_BUTTON, 'Ok')
        hz.Add(self.cancelButton, 0, wx.ALL, 1)
        hz.Add(self.okButton, 0, wx.ALL | wx.ALIGN_RIGHT, 1)

        sz.Add(self.nb, 7, wx.EXPAND | wx.ALL, 5)
        sz.Add(hz, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        self.okButton.Enable(False)

        self.Bind(wx.EVT_BUTTON, self.onOkButton, id = _ID_OK_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.onCancelButton, id = _ID_CANCEL_BUTTON)

        self.SetSizer(sz)
        self.SetAutoLayout(True)

    def onOkButton(self, evt):
        pass

    def onCancelButton(self, evt):
        self._parent.Close()

    def updateDirty(self, flag = None):
        if flag is not None:
            self._dirty = flag
        self.okButton.Enable(self._dirty == True)


class OptionsFrame(wx.Frame):
    def __init__(self, parentFrame, ID, title = 'Options',
            size = (570, 280), pos = wx.DefaultPosition,
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
