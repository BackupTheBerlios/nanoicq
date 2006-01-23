
#
# $Id: userlistctrl.py,v 1.1 2006/01/23 09:21:24 lightdruid Exp $
#

import sys
import wx
import wx.lib.mixins.listctrl as listmix

sys.path.insert(0, '../..')
from events import *

class UserListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos = wx.DefaultPosition,
            size = wx.DefaultSize, style = 0):

        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self._parent = parent

        self.currentItem = -1
        self.buddies = {}
 
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

# ---