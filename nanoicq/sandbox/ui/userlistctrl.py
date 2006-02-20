
#
# $Id: userlistctrl.py,v 1.11 2006/02/20 16:19:32 lightdruid Exp $
#

import sys
import wx
import wx.lib.mixins.listctrl as listmix

sys.path.insert(0, '../..')
from events import *
from buddy import Buddy
from iconset import IconSet


class UserListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent, ID, iconSet, pos = wx.DefaultPosition,
            size = wx.DefaultSize, style = wx.LC_REPORT | wx.BORDER_SIMPLE):

        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, 2)

        self.itemDataMap = {}

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

        for status in IconSet.FULL_SET:
            self.idx1 = self.il.Add(self.iconSet[status])
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
 
        self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected, self)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemDeselected, self)
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.onRightClick)

    def addBuddy(self, b):
        index = self.InsertImageStringItem(sys.maxint, '', 0)
        self.SetStringItem(index, 1, b.name)
        self.SetItemData(index, int(b.uin))

        print b, b.status
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
        self.currentItem = evt.m_itemIndex

    def onItemDeselected(self, evt):
        self.currentItem = -1

    def onRightClick(self, evt):
        print self.currentItem

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