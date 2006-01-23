
#
# $Id: userlistctrl.py,v 1.2 2006/01/23 16:53:43 lightdruid Exp $
#

import sys
import wx
import wx.lib.mixins.listctrl as listmix

sys.path.insert(0, '../..')
from events import *
#from message import messageFactory
#from buddy import Buddy


class UserListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos = wx.DefaultPosition,
            size = wx.DefaultSize, style = wx.LC_REPORT | wx.BORDER_SIMPLE):

        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self._parent = parent

        self.currentItem = -1
        self.buddies = {}

        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = "Status"
        self.InsertColumnInfo(0, info)

#        info.m_format = wx.LIST_FORMAT_RIGHT
        info.m_text = "User"
        self.InsertColumnInfo(1, info)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
 
        self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected, self)

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def onItemSelected(self, evt):
        self.currentItem = evt.m_itemIndex

    def onDoubleClick(self, evt):
        evt.Skip()

        # Simply return if user clicked empty list or outside of list
        if self.currentItem == -1:
            return

        userName = self.getColumnText(self.currentItem, 1)
        print "nDoubleClick item %d:%s" % (self.currentItem, userName)

        evt = NanoEvent(nanoEVT_MESSAGE_PREPARE, self.GetId())
        evt.setVal((self.currentItem, userName))
        self._parent.GetEventHandler().AddPendingEvent(evt)


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

            self.ul = UserListCtrl(self.p, -1)
            self.sampleFill()

        def sampleFill(self):
            from buddy import Buddy

            musicdata = {
            1 : ("", "a"),
            2 : ("", "b"),
            3 : ("", "c"),
            4 : ("", "d"),
            5 : ("", "e"),
            6 : ("", "f"),
            7 : ("", "g"),
            8 : ("", "h"),
            }

            self.il = wx.ImageList(16, 16)
            self.idx1 = self.il.Add(images.getSmilesBitmap())
            self.ul.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

            # Here we need to setup a list data

            items = musicdata.items()
            for key, data in items:
                index = self.ul.InsertImageStringItem(sys.maxint, data[0], self.idx1)
                self.ul.SetStringItem(index, 1, data[1])
                b = Buddy()
                b.name = str(key)
                self.ul.buddies[key] = b
                self.ul.SetItemData(index, key)

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