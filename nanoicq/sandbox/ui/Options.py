
#
# $Id: Options.py,v 1.4 2006/11/08 13:12:52 lightdruid Exp $
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

class _Pane_Core:
    def __init__(self):
        pass

    def store(self):
        return ET.Element("_Pane_Core")

    def restore(self, xml):
        return


class Pane_General(wx.Panel, _Pane_Core):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        _Pane_Core.__init__(self)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Pane_UI(wx.Panel, _Pane_Core):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        _Pane_Core.__init__(self)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)


class Pane_Network(wx.Panel, _Pane_Core):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        _Pane_Core.__init__(self)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Pane_ICQ(wx.Panel, _Pane_Core):
    _DEFAULT_LOGIN_SERVER = wx.NewId()

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        _Pane_Core.__init__(self)

        self._panelName = "ICQ"

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        ssz1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'ICQ'), wx.VERTICAL)

        self.icqNumber = wx.TextCtrl(self, -1, "")
        self.icqPassword = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)

        self.hl = hyperlink.HyperLinkCtrl(self, -1, "Create new account using ICQ website", URL = "http://www.icq.com/register/")

        rc = rcs.RowColSizer()

        rc.Add(wx.StaticText(self, -1, "ICQ Number:" ), flag=wx.RIGHT, row=0, col=0)
        rc.Add(wx.StaticText(self, -1, "Password:" ), flag=wx.ALIGN_RIGHT, row=1, col=0)

        rc.Add(self.icqNumber, row=0, col=2)
        rc.Add(self.icqPassword, row=1, col=2)

        ssz1.Add(rc, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        ssz1.Add(self.hl, 0, wx.ALL, 5)

        # ---
        ssz2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Connection settings'), wx.VERTICAL)

        hs = wx.BoxSizer(wx.HORIZONTAL)

        self.loginServer = wx.TextCtrl(self, -1, "")
        self.port = wx.TextCtrl(self, -1, "")
        self.setDefaultLoginServer = wx.Button(self, self._DEFAULT_LOGIN_SERVER, "Default")

        hs.Add(wx.StaticText(self, -1, "Login Server:"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hs.Add(self.loginServer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hs.Add(wx.StaticText(self, -1, "Port:"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hs.Add(self.port, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        hs.Add(self.setDefaultLoginServer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.Bind(wx.EVT_BUTTON, self.onSetDefaultLoginServer, id=self._DEFAULT_LOGIN_SERVER)

        ssz2.Add(hs, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        sz.Add(ssz1)
        sz.Add(ssz2)

        self.x = {}
        self.x["ICQNumber"] = self.icqNumber.GetId()
        self.x["ICQPassword"] = self.icqPassword.GetId()
        self.x["LoginServer"] = self.loginServer.GetId()
        self.x["Port"] = self.port.GetId()

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

    def onSetDefaultLoginServer(self, evt):
        self.loginServer.SetValue("login.icq.com")
        self.port.SetValue("5190")

        xml = self.store()
        self.restore(xml)

    def restore(self, xml):
        for c in xml.getchildren():
            self.FindWindowById(self.x[c.tag]).SetValue(c.text)

    def store(self):
        root = ET.Element(self._panelName)
        for k in self.x:
            e = ET.Element(k)
            e.text = self.FindWindowById(self.x[k]).GetValue()
            root.append(e)

        return root

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

        #self.okButton.Enable(False)

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
        f = open("options-new.xml", "wb")
        r = ET.Element("nanoicq")
        o = ET.SubElement(r, "options")
        for p in self.panes:
            o.append(self.panes[p].store())
        ET.dump(r)
        f.close()

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
            size = (620, 280), pos = wx.DefaultPosition,
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
