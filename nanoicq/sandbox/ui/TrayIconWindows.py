
#
# $Id: TrayIconWindows.py,v 1.15 2006/08/25 10:10:31 lightdruid Exp $
#

# The piece stolen from wxPython demo

import wx

from events import *
from FindUser import FindUserFrame

class TrayIcon(wx.TaskBarIcon):
    _timer = None

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

    def __init__(self, parent, icon, iconSet):
        wx.TaskBarIcon.__init__(self)
        self.parent = parent

        # Set the image
        self._tmp_icon = None
        self._icon = icon
        self.SetIcon(self._icon, "ICQ offline")

        self._iconSet = iconSet
        self._iconsOn = True

        self._emptyIcon = wx.EmptyIcon()
        self._emptyIcon.CopyFromBitmap(self._iconSet['empty'])

        # bind some events
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.onCancelTaskBarActivate)

        self.Bind(wx.EVT_MENU, self.onStatusChange)

        self.Bind(wx.EVT_MENU, self.onCancelTaskBarActivate, id = self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.onCancelTaskBarClose, id = self.TBMENU_CLOSE)

        self.Bind(wx.EVT_MENU, self.onFindUser, id = self.TBMENU_MAIN_FIND_CONTACTS)

    def blinkIcon(self):

        if self._iconsOn:
            self.SetIcon(self._emptyIcon)
        else:
            self.SetIcon(self._icon)
        self._iconsOn = not self._iconsOn

#    def startFlash(self):
#        if self._timer is None:
#            self._timer = wx.Timer(self, _ID_ICON_TIMER)
#            wx.EVT_TIMER(self, _ID_ICON_TIMER, self.blinkIcon)
#            self._timer.Start(_BLINK_TIMEOUT)
#        else:
#            print "Warning: attempt to start one more icon timer"

    def stopFlash(self):
        if self._timer is not None:
            self._timer.Stop()
            self._timer = None
            if not self._iconsOn:
                self.SetIcon(self._icon)

    def onResultByUin(self, b):
        print 'onResultByUin', b

    def onFindUser(self, evt):
        evt.Skip()
        self.parent.onFindUser(evt)

    def onStatusChange(self, evt):
        evt.Skip()

        eds = evt.GetId()
        for ids, txt, alias in self._statusMenuItems:
            if getattr(self, ids) == eds:
                evt = NanoEvent(nanoEVT_MY_STATUS_CHANGED, eds)
                evt.setVal(alias)
                #self.frame.GetEventHandler().AddPendingEvent(evt)
                wx.PostEvent(self.parent, evt)
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
        #font = item.GetFont()
        #font.SetWeight(wx.FONTWEIGHT_BOLD)
        #item.SetFont(font)
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

        # FIXME: hide on MS only
        if "wxMSW" not in wx.PlatformInfo:
            return

        if self.parent.IsIconized():
            self.parent.Iconize(False)
            if not self.parent.IsShown():
                self.parent.Show(True)
        else:
            self.parent.Iconize(True)
            if self.parent.IsShown():
                self.parent.Show(False)
        self.parent.Raise()

    def onCancelTaskBarClose(self, evt):
        self.parent.Close()

# ---
