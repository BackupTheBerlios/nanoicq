
#
# $Id: Options.py,v 1.13 2006/11/16 16:20:01 lightdruid Exp $
#

import elementtree.ElementTree as ET

import sys
import string
import copy

import wx
import wx.lib.rcsizer as rcs
import wx.lib.mixins.listctrl as listmix
import wx.lib.hyperlink as hyperlink

sys.path.insert(0, '../..')
from events import *
from buddy import Buddy
from iconset import IconSet
from utils import *
from validator import *

import Plugin

_ID_OK_BUTTON = wx.NewId()
_ID_CANCEL_BUTTON = wx.NewId()


def dump(elem, f):
    # debugging
    if not isinstance(elem, ET.ElementTree):
        elem = ET.ElementTree(elem)
    elem.write(f)
    tail = elem.getroot().tail
    if not tail or tail[-1] != "\n":
        f.write("\n")



class OptionsNB(wx.Notebook):
    def __init__(self, parent, id):
        wx.Notebook.__init__(self, parent, id,
                             style = wx.NB_TOP | wx.NB_MULTILINE
                             )

class _Pane_Core:
    def __init__(self, domain, name, xmlChunk):
        self._domainName = domain
        self._panelName = name
        self._xmlChunk = xmlChunk

        self.x = {}

    def restore(self, xml):
        for c in [x for x in xml.getchildren() if x.text is not None]:
            w = self.FindWindowById(self.x[c.tag])
            if type(w) == wx.TextCtrl:
                w.SetValue(c.text)
            elif type(w) == wx.CheckBox:
                w.SetValue(bool(int(c.text)))
            elif type(w) == wx.RadioButton:
                w.SetValue(bool(int(c.text)))
            else:
                raise Exception("Unknown element type: " + str(type(w)))

    def store(self):
        root = ET.Element(self._panelName)
        root.set("Internal", "1")
        for k in self.x:
            e = ET.Element(k)
            w = self.FindWindowById(self.x[k])
            if type(w) == wx.TextCtrl:
                v = w.GetValue()
            elif type(w) == wx.CheckBox:
                v = str(int(w.GetValue()))
            elif type(w) == wx.RadioButton:
                v = str(int(w.GetValue()))
            else:
                raise Exception("Unknown element type: " + str(type(w)))
            e.text = v
            root.append(e)

        return root


class Pane_General(wx.Panel, _Pane_Core):
    def __init__(self, parent, domain, name, xmlChunk):
        wx.Panel.__init__(self, parent, -1)
        _Pane_Core.__init__(self, domain, name, xmlChunk)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)


class Pane_Root(wx.Panel, _Pane_Core):
    def __init__(self, parent, domain, name, xmlChunk):
        wx.Panel.__init__(self, parent, -1)
        _Pane_Core.__init__(self, domain, name, xmlChunk)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        self.sz.Add(wx.StaticText(self, -1, "NanoICQ options\n\nPlease choose specific group of options"))

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)


class Pane_ContactList(wx.Panel, _Pane_Core):
    _HIDE_OFFLINE_USERS = wx.NewId()
    _HIDE_EMPTY_GROUPS = wx.NewId()
    _DISABLE_GROUPS = wx.NewId()
    _ASK_BEFORE_DELETING = wx.NewId()

    _SINGLE_CLICK_INTERFACE = wx.NewId()
    _ALWAYS_SHOW_STATUS = wx.NewId()
    _DISABLE_ICON_BLINKING = wx.NewId()

    _BY_NAME = wx.NewId()
    _BY_STATUS = wx.NewId()
    _BY_PROTOCOL = wx.NewId()

    def __init__(self, parent, domain, name, xmlChunk):
        wx.Panel.__init__(self, parent, -1)
        _Pane_Core.__init__(self, domain, name, xmlChunk)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        ssz1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Contact list'), wx.VERTICAL)
        self.cbHideOfflineUsers = wx.CheckBox(self, self._HIDE_OFFLINE_USERS, "Hide offline users")
        self.cbHideEmptyGroups = wx.CheckBox(self, self._HIDE_EMPTY_GROUPS, "Hide empty groups")
        self.cbDisableGroups = wx.CheckBox(self, self._DISABLE_GROUPS, "Disable groups")
        self.cbAskBeforeDeleting = wx.CheckBox(self, self._ASK_BEFORE_DELETING, "Disable groups")

        ssz1.Add(self.cbHideOfflineUsers, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        ssz1.Add(self.cbHideEmptyGroups, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        ssz1.Add(self.cbDisableGroups, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        ssz1.Add(self.cbAskBeforeDeleting, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        ssz2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Contact list sorting'), wx.VERTICAL)
        self.rbByName = wx.RadioButton(self, self._BY_NAME, "Sort contacts by name", style = wx.RB_GROUP)
        self.rbByStatus = wx.RadioButton(self, self._BY_STATUS, "Sort contacts by status")
        self.rbByProtocol = wx.RadioButton(self, self._BY_PROTOCOL, "Sort contacts by protocol")

        self.rbByName.SetValue(1)
        self.rbByStatus.SetValue(0)
        self.rbByProtocol.SetValue(0)

        self.rbSortGroup = [
            self.rbByName,
            self.rbByStatus,
            self.rbByProtocol,
        ]

        for radio in self.rbSortGroup:
            self.Bind(wx.EVT_RADIOBUTTON, self.onGroupSortSelect, radio)

        ssz2.Add(self.rbByName, 1, wx.ALIGN_LEFT|wx.ALL, 5)
        ssz2.Add(self.rbByStatus, 1, wx.ALIGN_LEFT|wx.ALL, 5)
        ssz2.Add(self.rbByProtocol, 1, wx.ALIGN_LEFT|wx.ALL, 5)

        ssz3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'System tray icon'), wx.VERTICAL)
        self.cbSingleClickInterface = wx.CheckBox(self, self._SINGLE_CLICK_INTERFACE, "Hide offline users")
        self.cbAlwaysShowStatusInTooltip = wx.CheckBox(self, self._ALWAYS_SHOW_STATUS, "Hide empty groups")
        self.cbDisableIconBlinking = wx.CheckBox(self, self._DISABLE_ICON_BLINKING, "Disable groups")

        ssz3.Add(self.cbSingleClickInterface, 1, wx.ALIGN_LEFT|wx.ALL, 5)
        ssz3.Add(self.cbAlwaysShowStatusInTooltip, 1, wx.ALIGN_LEFT|wx.ALL, 5)
        ssz3.Add(self.cbDisableIconBlinking, 1, wx.ALIGN_LEFT|wx.ALL, 5)

        rc = rcs.RowColSizer()
        rc.Add(ssz1, row=0, col=0, flag=wx.EXPAND, rowspan=2)
        rc.Add(ssz2, row=0, col=1, flag=wx.EXPAND)
        rc.Add(ssz3, row=1, col=1, flag=wx.EXPAND)

        sz.Add(rc)

        self.x["HideOfflineUsers"] = self.cbHideOfflineUsers.GetId()
        self.x["HideEmptyGroups"] = self.cbHideEmptyGroups.GetId()
        self.x["DisableGroups"] = self.cbDisableGroups.GetId()
        self.x["AskBeforeDeleting"] = self.cbAskBeforeDeleting.GetId()

        self.x["SingleClickInterface"] = self.cbSingleClickInterface.GetId()
        self.x["AlwaysShowStatusInTooltip"] = self.cbAlwaysShowStatusInTooltip.GetId()
        self.x["DisableIconBlinking"] = self.cbDisableIconBlinking.GetId()

        self.x["SortByName"] = self.rbByName.GetId()
        self.x["SortByStatus"] = self.rbByStatus.GetId()
        self.x["SortByProtocol"] = self.rbByProtocol.GetId()

        self.restore(self._xmlChunk)

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

    def onGroupSortSelect(self, evt):
        rs = evt.GetEventObject()
        evt.Skip()


class Pane_Network(wx.Panel, _Pane_Core):
    def __init__(self, parent, domain, name, xmlChunk):
        wx.Panel.__init__(self, parent, -1)
        _Pane_Core.__init__(self, domain, name, xmlChunk)

        self.sz = wx.BoxSizer(wx.VERTICAL)
        sz = self.sz

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)


class Pane_ICQ(wx.Panel, _Pane_Core):
    _DEFAULT_LOGIN_SERVER = wx.NewId()

    def __init__(self, parent, domain, name, xmlChunk):
        wx.Panel.__init__(self, parent, -1)
        _Pane_Core.__init__(self, domain, name, xmlChunk)

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
        self.port = wx.TextCtrl(self, -1, "", validator = DigitLengthValidator(maxLen = 5))
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

        self.x["ICQNumber"] = self.icqNumber.GetId()
        self.x["ICQPassword"] = self.icqPassword.GetId()
        self.x["LoginServer"] = self.loginServer.GetId()
        self.x["Port"] = self.port.GetId()

        self.restore(self._xmlChunk)

        # ---
        self.SetSizer(sz)
        self.SetAutoLayout(True)

    def onSetDefaultLoginServer(self, evt):
        self.loginServer.SetValue("login.icq.com")
        self.port.SetValue("5190")

        xml = self.store()
        self.restore(xml)

class OptionsTree(wx.TreeCtrl):
    def __init__(self, parent, id, plugins):
        wx.TreeCtrl.__init__(self, parent, id)

        self._plugins = plugins

        fn = "options.xml"
        tree = ET.parse(fn)
        root = tree.getroot()
        print dir(root), root.tag

        if root.tag != "Nanoicq":
            raise Exception("Wrong XML format in '%d'" % fn)

        child = root.getchildren()[0]
        if child.tag != "Options":
            raise Exception("Wrong XML format in '%d'" % fn)

        #parent_map = dict((c, p) for p in children.getiterator() for c in p)
        #print parent_map

        #self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onActivate, self)


        # Setup root pane

        self._domains = {}
        self._panes = {}

        self.root = self.AddRoot("/")
        self.SetPyData(self.root, ("/", "Root"))

        self._panes["Root"] = None
        self._domains["/"] = copy.copy(self._panes)

        self._panes = {}

        # Setup other panes from XML

        for c in child.getchildren():

            predef = False
            try:
                predef = int(c.attrib["Internal"]) == 1
            except KeyError:
                pass

            if predef:
                ch = self.AppendItem(self.root, c.tag)
                self.SetPyData(ch, (c.tag, c.tag))
                self._panes[c.tag] = copy.copy(c)

                for d in c.getchildren():
                    predef = False
                    try:
                        predef = int(d.attrib["Internal"]) == 1
                    except KeyError:
                        pass

                    if predef:
                        dh = self.AppendItem(ch, d.tag)
                        self.SetPyData(dh, (c.tag, d.tag))
                        self._panes[d.tag] = copy.copy(d)
            else:
                ch = self.AppendItem(self.root, c.tag)
                self.SetPyData(ch, (c.tag, c.tag))
                #self._panes[c.tag] = copy.copy(c)
                #self._domains[c.tag] = copy.copy(c)
                pass

            self._domains[c.tag] = copy.copy(self._panes)
            self._panes = {}

            self.Expand(ch)

        self.Expand(self.root)

        # Load the rest of plugins
        c = self.GetRootItem()

        for pl in [px for px in self._plugins.values() if not px.isLoaded()]:
            domain = pl.getDomain().capitalize()
            name = pl.getName().capitalize()

            domainRoot = self.haveDomain(self.root, domain)
            print '>', domain, name, domainRoot

            if domainRoot:
                domainPanes = self._domains[domain]
                domainPanes[name] = None

                dh = self.AppendItem(domainRoot, name)
                self.SetPyData(dh, (domain, name))
                self._domains[domain] = domainPanes
            else:
                ch = self.AppendItem(self.root, domain)
                dh = self.AppendItem(ch, name)
                self.SetPyData(ch, (domain, domain))
                self.SetPyData(dh, (domain, name))

                self._panes = {}
                self._panes[domain] = None
                self._panes[name] = None

                self._domains[domain] = self._panes

            self.Expand(ch)

    def haveDomain(self, root, d):
        found = None

        (child, cookie) = self.GetFirstChild(root)
        while child.IsOk():
            if d == self.GetItemText(child):
                found = child
                break
            (child, cookie) = self.GetNextChild(root, cookie)

        return found

    def getDomains(self):
        return self._domains


class OptionsPanel(wx.Panel):
    _head = [
        'General', 'ICQ'
    ]

    _dirty = False
    _activePane = None

    def __init__(self, parent, plugins):
        wx.Panel.__init__(self, parent, -1)

        self._parent = parent
        self._plugins = plugins

        sz = wx.BoxSizer(wx.VERTICAL)
        self.tree = OptionsTree(self, -1, plugins)

        self.tz = wx.BoxSizer(wx.HORIZONTAL)
        self.tz.Add(self.tree, 1, wx.ALL | wx.EXPAND, 5)

        hz = wx.BoxSizer(wx.HORIZONTAL)
        self.cancelButton = wx.Button(self, _ID_CANCEL_BUTTON, 'Cancel')
        self.okButton = wx.Button(self, _ID_OK_BUTTON, 'Ok')
        hz.Add(self.cancelButton, 0, wx.ALL, 1)
        hz.Add(self.okButton, 0, wx.ALL | wx.ALIGN_RIGHT, 1)

        sz.Add(self.tz, 7, wx.EXPAND | wx.ALL, 5)
        sz.Add(hz, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        #self.okButton.Enable(False)

        self.SetSizer(sz)
        self.SetAutoLayout(True)

        self.tz.Layout()
        self.Layout()

        # Create panes
        domains = self.tree.getDomains()
        self.domains = copy.copy(domains)

        for d in domains:
            for p in domains[d]:
                xmlChunk = self.domains[d][p]
                self.domains[d][p] = self.createPane(d, p, xmlChunk)
                self.domains[d][p].Hide()

        self._currentData = None

        # Events
        self.Bind(wx.EVT_BUTTON, self.onOkButton, id = _ID_OK_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.onCancelButton, id = _ID_CANCEL_BUTTON)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelChanged, self.tree)

        self.first_time = True

    def onOkButton(self, evt):
        import os, shutil
        from tempfile import mkstemp

        fn = mkstemp()[1]
        f = open(fn, "wb")

        r = ET.Element("Nanoicq")
        o = ET.SubElement(r, "Options")
        for d in self.domains:
            top = ET.SubElement(o, d)
            top.set("Internal", "1")
            for p in self.domains[d]:
                if p == d:
                    continue
                top.append(self.domains[d][p].store())
        dump(r, f)
        f.close()

        shutil.copy(fn, "options.xml")

    def onCancelButton(self, evt):
        self._parent.Close()

    def updateDirty(self, flag = None):
        if flag is not None:
            self._dirty = flag
        self.okButton.Enable(self._dirty == True)

    def createPane(self, domain, name, xmlChunk):
        # If it's plugin pane - let plugin to create it
        if self._plugins.has_key(name.lower()):
            return self._plugins[name.lower()].drawOptions(self)

        #print 'name, domain', name, domain, self.domains[domain][domain]
        if name == domain:        
            d = domain
            if self.domains[d][d] is None:
                p = Pane_General(self, domain, name, None)
                return p

        return eval("Pane_%s(self, '%s', '%s', xmlChunk)" % (name, domain, name))

    def onSelChanged(self, evt):

        item = evt.GetItem()
        data = self.tree.GetPyData(item)

        if self._currentData is not None:
            domain, paneName = self._currentData
            self.tz.Detach(self.domains[domain][paneName])
            self.domains[domain][paneName].Hide()

        domain, paneName = data
        self._currentData = data

        self.tz.Add(self.domains[domain][paneName], 3, wx.ALL | wx.EXPAND, 5)
        self.domains[domain][paneName].Show()
        self.tz.Layout()
        self.Layout()


class OptionsFrame(wx.Frame):
    def __init__(self, parentFrame, ID, icon, plugins, title = 'Options',
            size = (620, 280), pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE 
                | wx.MAXIMIZE_BOX 
                | wx.MINIMIZE_BOX
                | wx.RESIZE_BORDER
                ):

        wx.Frame.__init__(self, parentFrame, ID, size = size, style = style,
            title = title)

        self.SetIcon(icon)

        tz = wx.BoxSizer(wx.VERTICAL)

        self.panel = OptionsPanel(self, plugins)

        tz.Add(self.panel, 1, wx.ALL | wx.EXPAND, 0)

        self.SetSizer(tz)
        self.SetAutoLayout(True)

def _test():
    class NanoApp(wx.App):
        def OnInit(self):

            c = {}
            c['icq'] = None
            p = Plugin.load_plugins('../../plugins', '../plugins',
                connector = c)

            frame = OptionsFrame(None, -1, wx.EmptyIcon(), p)
            self.SetTopWindow(frame)
            frame.CentreOnParent()
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
