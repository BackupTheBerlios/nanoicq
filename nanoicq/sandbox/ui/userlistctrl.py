
#
# $Id: userlistctrl.py,v 1.22 2006/08/16 09:59:01 lightdruid Exp $
#

import sys
import wx
import wx.lib.mixins.listctrl as listmix
import wx.lib.mixins.listctrl as listmix

sys.path.insert(0, '../..')
from events import *
from buddy import Buddy
from iconset import IconSet


class NanoTextEditMixin(listmix.TextEditMixin):
    def __init__(self):
        listmix.TextEditMixin.__init__(self)

        self.Unbind(wx.EVT_LEFT_DCLICK)
        self.Bind(wx.EVT_CHAR, self.onMainChar)

        self._origValue = self.editor.GetValue()

    def OnLeftDown(self, evt=None):
        evt.Skip()

    def onMainChar(self, event):

        keycode = event.GetKeyCode()
        if keycode == wx.WXK_F2:

            self.col_locs = [0]
            loc = 0
            for n in range(self.GetColumnCount()):
                loc = loc + self.GetColumnWidth(n)
                self.col_locs.append(loc)

            if self.editor.IsShown():
                event.Skip()
            else:
                self.CloseEditor()
                if self.curRow >= 0:
                    self._SelectIndex(self.curRow)
                    self.OpenEditor(1, self.curRow)
        elif keycode == wx.WXK_ESCAPE:
            self.CloseEditor()
            #self.editor.SetValue(self._origValue)
        else:
            event.Skip()

    def OnChar(self, event):

        keycode = event.GetKeyCode()

        if keycode == wx.WXK_TAB and event.ShiftDown():
            self.CloseEditor()
            if self.curCol-1 >= 0:
                self.OpenEditor(self.curCol-1, self.curRow)
            
        elif keycode == wx.WXK_TAB:
            self.CloseEditor()
            if self.curCol+1 < self.GetColumnCount():
                self.OpenEditor(self.curCol+1, self.curRow)

        elif keycode == wx.WXK_ESCAPE:
            self.CloseEditor()
            #self.editor.SetValue(self._origValue)

        elif keycode in [wx.WXK_UP, wx.WXK_DOWN]:
            pass

        else:
            event.Skip()


class UserListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin,
        listmix.ColumnSorterMixin, NanoTextEditMixin):

    ID_SEND_MESSAGE                 = wx.NewId()
    ID_USER_DETAILS                 = wx.NewId()
    ID_USER_ADD_TO_SERVER_LIST      = wx.NewId()
    ID_USER_RENAME                  = wx.NewId()
    ID_USER_DELETE                  = wx.NewId()

    def __init__(self, parent, ID, iconSet, pos = wx.DefaultPosition,
            size = wx.DefaultSize, style = wx.LC_REPORT | wx.BORDER_NONE): # wx.BORDER_SIMPLE):

        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, 2)
        NanoTextEditMixin.__init__(self)

        # 212 208 200
        #self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetBackgroundColour(wx.Color(212, 208, 200))

        self.itemDataMap = {}
        self.currentItem = -1

        self._parent = parent

        assert isinstance(iconSet, IconSet)
        self.iconSet = iconSet

        self.currentItem = -1
        self.buddies = {}

        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = ""
        self.InsertColumnInfo(0, info)

#        info.m_format = wx.LIST_FORMAT_RIGHT
        info.m_text = ""
        self.InsertColumnInfo(1, info)

        self.il = wx.ImageList(16, 16)

        # for blinnking
        self._iconsOn = True

        self._emptyIcon = wx.EmptyIcon()
        self._emptyIcon.CopyFromBitmap(self.iconSet['empty'])

        for status in IconSet.FULL_SET:
            self.idx1 = self.il.Add(self.iconSet[status])
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
 
        self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected, self)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemDeselected, self)

        if "wxMSW" in wx.PlatformInfo:
            # Works on MSW only
            self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.onRightClick)
        else:
            # Works on GTK only, not sure about Mac
            self.Bind(wx.EVT_RIGHT_UP, self.onRightClick)

        self._blinking = {}
        ###

    def setBuddyNick(self, b, nick = None):
        if nick is None:
            if hasattr(b, 'nick') and b.nick is not None:
                nick = b.nick
            else:
                return

        idx = -1

        while True:
            idx = self.GetNextItem(idx)
            if idx == -1:
                break
            uin = str(self.GetItemData(idx))
            if uin == b.uin:
                self.SetStringItem(idx, 1, b.nick)
                break

    def blinkIcon(self, b):
        print 'userlist - blinkIcon', b

        userName = b.name
        idx = -1

        while True:
            idx = self.GetNextItem(idx)
            if idx == -1:
                break
            u = self.getColumnText(idx, 1)
            if u == userName:
                self._blinking[userName] = (True, b)

                if self._iconsOn:
                    self.SetStringItem(idx, 0, '', IconSet.FULL_SET.index('empty'))
                else:
                    self.SetStringItem(idx, 0, '', IconSet.FULL_SET.index(b.status))
                self._iconsOn = not self._iconsOn
                break
 
    def createPopUpMenu(self):
        _topMenu = (
            (self.ID_SEND_MESSAGE, "Send message", "self.onSendMessage"),
            (),
            (self.ID_USER_DETAILS, "User details", "self.onUserDetails"),
            (self.ID_USER_ADD_TO_SERVER_LIST, "Add to server list", "self.onUserAddToServerList"),
            (),
            (self.ID_USER_RENAME, "Rename", "self.onUserRename"),
            (self.ID_USER_DELETE, "Delete", "self.onUserDelete"),
        )

        if self.currentItem == -1:
            return

        self.popUpMenu = wx.Menu()

        for d in _topMenu:
            if len(d) == 0:
                self.popUpMenu.AppendSeparator()
            else:
                ids, txt, func = d
                item = wx.MenuItem(self.popUpMenu, ids, txt, txt)
                self.Bind(wx.EVT_MENU, eval(func), id = ids)
                self.popUpMenu.AppendItem(item)

        self.PopupMenu(self.popUpMenu)

    def onSendMessage(self, evt):
        evt.Skip()

        userName = self.getColumnText(self.currentItem, 1)

        evt = NanoEvent(nanoEVT_MESSAGE_PREPARE, self.GetId())
        evt.setVal((self.currentItem, userName))
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(evt)

    def onUserDetails(self, evt):
        evt.Skip()

        userName = self.getColumnText(self.currentItem, 1)

        newEvent = NanoEvent(nanoEVT_REQUEST_USER_INFO, self.GetId())
        newEvent.setVal(userName)
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(newEvent)

    def onUserAddToServerList(self, evt):
        evt.Skip()

        userName = self.getColumnText(self.currentItem, 1)

        newEvent = NanoEvent(nanoEVT_ADD_USER_TO_LIST_BY_NAME, self.GetId())
        newEvent.setVal(userName)
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(newEvent)

    def onUserRename(self, evt):
        evt.Skip()

    def onUserDelete(self, evt):
        #evt.Skip()
        userName = self.getColumnText(self.currentItem, 1)

        evt = NanoEvent(nanoEVT_USER_DELETE, self.GetId())
        evt.setVal(userName)
        self._parent.GetEventHandler().AddPendingEvent(evt)

    def deleteBuddy(self, b):
        item = self.FindItemData(-1, int(b.uin))
        if item != -1:
            self.DeleteItem(item)
        else:
            raise Exception('Unable to delete user %s' % b.uin)

    def addBuddy(self, b):
        index = self.InsertImageStringItem(sys.maxint, '', 0)
        self.SetStringItem(index, 1, b.name)
        self.SetItemData(index, int(b.uin))

        self.changeStatus(b)
        self.itemDataMap[int(b.uin)] = (b.status, b.name)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def GetListCtrl(self):
        return self

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def onItemSelected(self, evt):
        NanoTextEditMixin.OnItemSelected(self, evt)
        self.currentItem = evt.m_itemIndex

    def onItemDeselected(self, evt):
        self.currentItem = -1

    def onRightClick(self, evt):
        print self.currentItem
        self.createPopUpMenu()

    def changeStatus(self, b):
        userName = b.name
        idx = -1

        while True:
            idx = self.GetNextItem(idx)
            if idx == -1:
                break
            u = self.getColumnText(idx, 1)
            if u == userName:
                self.SetStringItem(idx, 0, '', IconSet.FULL_SET.index(b.status))
                break

    def onDoubleClick(self, evt):
        evt.Skip()

        # Simply return if user clicked empty list or outside of list
        if self.currentItem == -1:
            return

        userName = self.getColumnText(self.currentItem, 1)

        try:
            if self._blinking[userName][0] == True:
                del self._blinking[userName]

                # Just restore icon
                self.changeStatus(b)
        except KeyError, exc:
            pass

        evt = NanoEvent(nanoEVT_MESSAGE_PREPARE, self.GetId())
        evt.setVal((self.currentItem, userName))
        self._parent.GetEventHandler().AddPendingEvent(evt)

        self.Update()
        self.Refresh()

    def onHideOffline(self, blist, flag):
        #for k in self.itemDataMap:
        #    item = self.FindItemData(-1, k)
        #    if item != -1:
        #        self.DeleteItem(item)

        assert flag in [True, False]
        print 'onHideOffline, flag: ', flag

        if flag:
            for b in blist:
                item = self.FindItemData(-1, int(b.uin))
                if item != -1:
                    self.DeleteItem(item)
        else:
            for b in blist:
                self.addBuddy(b)

    def sampleFill(self):

        musicdata = {
        1 : ("", "a"),
        2 : ("", "b"),
        3 : ("", "c"),
        4 : ("", "d"),
        5 : ("", "e"),
        6 : ("", "f"),
        7 : ("", "g"),
        }

        ii = 0
        items = musicdata.items()
        for key, data in items:
            index = self.InsertImageStringItem(sys.maxint, data[0], ii)
            self.SetStringItem(index, 1, IconSet.FULL_SET[ii])
            b = Buddy()
            b.name = str(key)
            self.buddies[key] = b
            self.itemDataMap[key] = (b.status, b.name)
            self.SetItemData(index, key)
            ii += 1

            #break

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        if 0:
            # Turn on labeltips in list control 
            from win32api import SendMessage 
            import commctrl # from win32 extensions for constants 

            # All of the extended label styles are missing from the  
            # current version (1.1) of commctrl.py, but this is the value  
            # needed: 
            LVS_EX_LABELTIP = 16384 

            style = SendMessage(self.GetHandle(),  
                         commctrl.LVM_GETEXTENDEDLISTVIEWSTYLE, 0, 0) 
            style = style | LVS_EX_LABELTIP 
            SendMessage(self.GetHandle(),  
                 commctrl.LVM_SETEXTENDEDLISTVIEWSTYLE, 0, style) 

def _test():
    class TopFrame(wx.Frame):
        def __init__(self, parent, title):
            wx.Frame.__init__(self, parent, -1, title,
                pos=(150, 150), size=(350, 200))
            self.p = wx.Panel(self, -1)

#            message = messageFactory("icq", 'user', '12345', 'text', History.Incoming)

#            h = History()
#            b = Buddy()
#            b.name = 'user'
#            d = MessageDialog(self, -1, b, message, h)
#            d.Show(True)

            self.iconSet = IconSet()
            self.iconSet.addPath('icons/aox')
            self.iconSet.loadIcons()
            self.iconSet.setActiveSet('aox')            

            self.ul = UserListCtrl(self.p, -1, self.iconSet)
            self.ul.sampleFill()


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
