
#
# $Id: TrayIconWindows.py,v 1.7 2006/02/20 16:43:39 lightdruid Exp $
#

# The piece stolen from wxPython demo

import wx

from events import *

class TrayIcon(wx.TaskBarIcon):
    TBMENU_RESTORE = wx.NewId()
    TBMENU_CLOSE   = wx.NewId()
    TBMENU_CHANGE  = wx.NewId()
    TBMENU_REMOVE  = wx.NewId()

    TBMENU_MAIN                     = wx.NewId()
    TBMENU_MAIN_FIND_CONTACTS       = wx.NewId()
    TBMENU_MAIN_IMPORT              = wx.NewId()
    TBMENU_MAIN_CHANGE_DETAILS      = wx.NewId()
    TBMENU_MAIN_OPTIONS             = wx.NewId()
    TBMENU_MAIN_HELP                = wx.NewId()
    TBMENU_MAIN_EXIT                = wx.NewId()

    TBMENU_STATUS_MENU          = wx.NewId()
    TBMENU_STATUS_OFFLINE       = wx.NewId()
    TBMENU_STATUS_ONLINE        = wx.NewId()
    TBMENU_STATUS_AWAY          = wx.NewId()
    TBMENU_STATUS_NA            = wx.NewId()
    TBMENU_STATUS_OCCIPIED      = wx.NewId()
    TBMENU_STATUS_DND           = wx.NewId()
    TBMENU_STATUS_FREE          = wx.NewId()
    TBMENU_STATUS_INVISIBLE     = wx.NewId()

    _mainMenuItems = [
        ("TBMENU_MAIN_FIND_CONTACTS"        , "Find/Add Contacts..."),
        ("TBMENU_MAIN_IMPORT"               , "Import..."),
        ("TBMENU_MAIN_CHANGE_DETAILS"       , "View/Change My Details..."),
        ("", ""),
        ("TBMENU_MAIN_OPTIONS"              , "Options..."),
        ("", ""),
        ("TBMENU_MAIN_HELP"                 , "Help"),
        ("", ""),
        ("TBMENU_MAIN_EXIT"                 , "Exit"),
    ]

    _statusMenuItems = [
        ("TBMENU_STATUS_OFFLINE"       , "Offline",         "offline"),
        ("TBMENU_STATUS_ONLINE"        , "Online",          "online"),
        ("TBMENU_STATUS_AWAY"          , "Away",            "away"),
        ("TBMENU_STATUS_NA"            , "N/A",             "na"),
        ("TBMENU_STATUS_OCCIPIED"      , "Occupied",        "occupied"),
        ("TBMENU_STATUS_DND"           , "DND",             "dnd"),
        ("TBMENU_STATUS_FREE"          , "Free for chat",   "free"),
        ("TBMENU_STATUS_INVISIBLE"     , "Invisible",       "invisible"),
    ]

    def __init__(self, frame, icon, iconSet):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame

        # Set the image
        self._icon = icon
        self.SetIcon(self._icon, "ICQ offline")

        self._iconSet = iconSet

        # bind some events
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.onCancelTaskBarActivate)

        self.Bind(wx.EVT_MENU, self.onStatusChange)

        self.Bind(wx.EVT_MENU, self.onCancelTaskBarActivate, id = self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.onCancelTaskBarClose, id = self.TBMENU_CLOSE)
        #self.Bind(wx.EVT_MENU, self.onCancelTaskBarChange, id=self.TBMENU_CHANGE)
        #self.Bind(wx.EVT_MENU, self.onCancelTaskBarRemove, id=self.TBMENU_REMOVE)

    def onStatusChange(self, evt):
        evt.Skip()

        eds = evt.GetId()
        for ids, txt, alias in self._statusMenuItems:
            if getattr(self, ids) == eds:
                evt = NanoEvent(nanoEVT_MY_STATUS_CHANGED, eds)
                evt.setVal(alias)
                self.frame.GetEventHandler().AddPendingEvent(evt)
                return

        assert 1 == 2

    def setToolTip(self, toolTip):
        self.SetIcon(self._icon, toolTip)

    def CreatePopupMenu(self):
        statusMenu = wx.Menu()
        for ids, txt, alias in self._statusMenuItems:
            item = wx.MenuItem(statusMenu, getattr(self, ids), txt, txt)
            item.SetBitmap(self._iconSet[alias])
            statusMenu.AppendItem(item)

            #statusMenu.Append(getattr(self, ids), txt)

        mainMenu = wx.Menu()
        for ids, txt in self._mainMenuItems:
            if txt == '':
                mainMenu.AppendSeparator()
            else:
                item = wx.MenuItem(mainMenu, getattr(self, ids), txt, txt)
                #item.SetBitmap(self._iconSet[alias])
                mainMenu.AppendItem(item)

        menu = wx.Menu()
        item = wx.MenuItem(menu, self.TBMENU_RESTORE, "Hide/Show", "")
        font = item.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        item.SetFont(font)
        menu.AppendItem(item)

        menu.AppendMenu(self.TBMENU_MAIN, 'Main Menu', mainMenu)
        menu.AppendMenu(self.TBMENU_STATUS_ONLINE, 'Status', statusMenu)
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE,   "Exit")
        return menu

    def MakeIcon(self, img):
        """
        The various platforms have different requirements for the
        icon size...
        """
        if "wxMSW" in wx.PlatformInfo:
            img = img.Scale(16, 16)
        elif "wxGTK" in wx.PlatformInfo:
            img = img.Scale(22, 22)
        # wxMac can be any size upto 128x128, so leave the source img alone....
        icon = wx.IconFromBitmap(img.ConvertToBitmap() )
        return icon

    def onCancelTaskBarActivate(self, evt):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
            if not self.frame.IsShown():
                self.frame.Show(True)
        else:
            self.frame.Iconize(True)
            if self.frame.IsShown():
                self.frame.Show(False)
        self.frame.Raise()

    def onCancelTaskBarClose(self, evt):
        self.frame.Close()

    def onCancelTaskBarChange(self, evt):
        names = [ "WXPdemo", "Mondrian", "Pencil", "Carrot" ]
        name = names[self.imgidx]

        getFunc = getattr(images, "get%sImage" % name)
        self.imgidx += 1
        if self.imgidx >= len(names):
            self.imgidx = 0

        icon = self.MakeIcon(getFunc())
        self.SetIcon(icon, "This is a new icon: " + name)

    def onCancelTaskBarRemove(self, evt):
        self.RemoveIcon()

# ---
