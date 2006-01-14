
#
# $Id: TrayIcon.py,v 1.3 2006/01/14 02:48:21 lightdruid Exp $
#

# The piece stolen from wxPython demo

import wx
import images

class TrayIcon(wx.TaskBarIcon):
    TBMENU_RESTORE = wx.NewId()
    TBMENU_CLOSE   = wx.NewId()
    TBMENU_CHANGE  = wx.NewId()
    TBMENU_REMOVE  = wx.NewId()

    TBMENU_STATUS_MENU          = wx.NewId()
    TBMENU_STATUS_OFFLINE       = wx.NewId()
    TBMENU_STATUS_ONLINE        = wx.NewId()
    TBMENU_STATUS_AWAY          = wx.NewId()
    TBMENU_STATUS_NA            = wx.NewId()
    TBMENU_STATUS_OCCIPIED      = wx.NewId()
    TBMENU_STATUS_DND           = wx.NewId()
    TBMENU_STATUS_FREE          = wx.NewId()
    TBMENU_STATUS_INVISIBLE     = wx.NewId()

    _statusMenuItems = [
        ("TBMENU_STATUS_OFFLINE"       , "Offline"),
        ("TBMENU_STATUS_ONLINE"        , "Online"),
        ("TBMENU_STATUS_AWAY"          , "Away"),
        ("TBMENU_STATUS_NA"            , "N/A"),
        ("TBMENU_STATUS_OCCIPIED"      , "Occupied"),
        ("TBMENU_STATUS_DND"           , "DND"),
        ("TBMENU_STATUS_FREE"          , "Free for chat"),
        ("TBMENU_STATUS_INVISIBLE"     , "Invisible"),
    ]

    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame

        # Set the image
        icon = self.MakeIcon(images.getLimeWireImage())
        self.SetIcon(icon, "NanoICQ")
        self.imgidx = 1

        # bind some events
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.onCancelTaskBarActivate)
        self.Bind(wx.EVT_MENU, self.onCancelTaskBarActivate, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.onCancelTaskBarClose, id=self.TBMENU_CLOSE)
        #self.Bind(wx.EVT_MENU, self.onCancelTaskBarChange, id=self.TBMENU_CHANGE)
        #self.Bind(wx.EVT_MENU, self.onCancelTaskBarRemove, id=self.TBMENU_REMOVE)


    def CreatePopupMenu(self):
        """
        This method is called by the base class when it needs to popup
        the menu for the default EVT_RIGHT_DOWN event.  Just create
        the menu how you want it and return it from this function,
        the base class takes care of the rest.
        """
        statusMenu = wx.Menu()
        for ids, txt in self._statusMenuItems:
            statusMenu.Append(getattr(self, ids), txt)

        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, "Hide/Show")
        menu.AppendMenu(self.TBMENU_STATUS_ONLINE, 'Status', statusMenu)
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE,   "Exit")
        #menu.Append(self.TBMENU_CHANGE, "Change the TB Icon")
        #menu.Append(self.TBMENU_REMOVE, "Remove the TB Icon")
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
