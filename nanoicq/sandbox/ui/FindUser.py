
#
# $Id: FindUser.py,v 1.13 2006/03/06 21:42:06 lightdruid Exp $
#

import sys
import traceback
import string

import wx
import wx.lib.rcsizer as rcs
import wx.lib.mixins.listctrl as listmix

sys.path.insert(0, '../..')
from events import *
from buddy import Buddy
from iconset import IconSet
from persistence import PersistenceMixin


class SearchStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(2)
        self.SetStatusWidths([-2, -1])

        #self.Reposition()

    def setFileName(self, fn):
        path, fileName = os.path.split(fn)
        self.SetStatusText(fileName, 0)

    def setRowCol(self, row, col):
        self.SetStatusText("%d,%d" % (row,col), 1)

    def setDirty(self, dirty):
        if dirty:
            self.SetStatusText("...", 2)
        else:
            self.SetStatusText(" ", 2)

    def __OnSize(self, evt):
        self.Reposition()
        self.sizeChanged = True

    def __OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()

    def __Reposition(self):
        rect = self.GetFieldRect(1)
        self.g.SetPosition((rect.x+2, rect.y+2))
        self.g.SetSize((rect.width-4, rect.height-4))
        self.sizeChanged = False


_DIGIT_ONLY = 2

class DigitValidator(wx.PyValidator):
    def __init__(self, flag = _DIGIT_ONLY, pyVar = None):
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return DigitValidator(self.flag)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        
        if self.flag == _DIGIT_ONLY:
            for x in val:
                if x not in string.digits:
                    return False

        return True

    def OnChar(self, event):
        key = event.KeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if self.flag == _DIGIT_ONLY and chr(key) in string.digits:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        return


class ResultsList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    ID_SEND_MESSAGE = wx.NewId()
    ID_USER_DETAILS = wx.NewId()
    ID_SEND_MESSAGE = wx.NewId()

    def __init__(self, parent, ID, iconSet, pos = wx.DefaultPosition,
            size = wx.DefaultSize, style = wx.LC_REPORT | wx.BORDER_SIMPLE):

        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

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

        self.SetColumnWidth(0, 22)

        headers = ("Nick", "First Name", "Last Name", "E-mail", "User ID")
        ii = 1
        for t in headers:
            info.m_text = t
            self.InsertColumnInfo(ii, info)
            ii += 1

#        for ii in range(len(headers)):
#            self.SetColumnWidth(ii, wx.LIST_AUTOSIZE)
#            pass

        self.il = wx.ImageList(16, 16)

        for status in IconSet.FULL_SET:
            self.idx1 = self.il.Add(self.iconSet[status])
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        # FIXME: it looks like bug, EVT_RIGHT_UP doesn't work,
        # it triggers only on second click
        self.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected, self)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemDeselected, self)
        self.Bind(EVT_UNABLE_ADD_USER_TO_LIST, self.onUnableAddUserToList)

    def onUnableAddUserToList(self, evt):
        '''
        Unable to add user to list (UIN already exists, etc.)
        '''
        evt.Skip()
        print 'onUnableAddUserToList', evt.getVal()

    def onItemSelected(self, evt):
        self.currentItem = evt.m_itemIndex

    def onItemDeselected(self, evt):
        self.currentItem = -1

    def onRightClick(self, evt):
        self.createPopUpMenu()
        #evt.Skip()

    def createPopUpMenu(self):
        _topMenu = (
            (self.ID_SEND_MESSAGE, "Add to list", "self.onAddToContactList"),
            (),
            (self.ID_USER_DETAILS, "User details", "self.onUserDetails"),
            (self.ID_SEND_MESSAGE, "Send message", "self.onSendMessage"),
        )

        #if self.currentItem == -1: return

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

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def onAddToContactList(self, evt):
        print 'onAddToContactList'
        evt.StopPropagation()

        b = Buddy()
        b.name = self.getColumnText(self.currentItem, 1)
        b.first = self.getColumnText(self.currentItem, 2)
        b.last = self.getColumnText(self.currentItem, 3)
        b.email = self.getColumnText(self.currentItem, 4)
        b.uin = self.getColumnText(self.currentItem, 5)

        newEvent = NanoEvent(nanoEVT_ADD_USER_TO_LIST, self.GetId())
        newEvent.setVal(b)
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(newEvent)

    def onUserDetails(self, evt):
        evt.Skip()
        print evt

    def onSendMessage(self, evt):
        evt.Skip()
        print evt


ID_userIDRadio = wx.NewId()
ID_emailRadio = wx.NewId()
ID_nameRadio = wx.NewId()


class FindUserPanel(wx.Panel):
    protocolList = ["ICQ"]

    def __init__(self, parent, iconSet):
        wx.Panel.__init__(self, parent, -1)

        sizer = rcs.RowColSizer()
        r = 0

        self.g = wx.Gauge(self, -1, size = (168, 15), style = wx.GA_SMOOTH)
        self.g.SetBezelFace(0)
        self.g.SetShadowWidth(0)
        sizer.Add(self.g, row = r, col = 1)
        self.g.Hide()
        r += 1

        protoSizer = rcs.RowColSizer()
        self.protocol = wx.ComboBox(self, -1, self.protocolList[0], size = (110, -1), choices = self.protocolList, style = wx.CB_READONLY)
        protoSizer.Add(wx.StaticText(self, -1, 'Search:'), row = 0, col = 0)
        protoSizer.Add(self.protocol, row = 0, col = 3)
        sizer.Add(protoSizer, row = r, col = 1, flag = wx.EXPAND)
        r += 1

        boxSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.userIDRadio = wx.RadioButton(self, ID_userIDRadio, "User ID")
        self.userID = wx.TextCtrl(self, -1, '', size = (155, -1),
            validator = DigitValidator())
        boxSizer1.Add(self.userIDRadio, 0, wx.ALL, 3)
        boxSizer1.Add(self.userID, 0, wx.ALL, 3)
        sizer.Add(boxSizer1, row = r, col = 1)
        r += 1

        boxSizer2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.emailRadio = wx.RadioButton(self, ID_emailRadio, "E-mail address")
        self.email = wx.TextCtrl(self, -1, '', size = (155, -1))
        boxSizer2.Add(self.emailRadio, 0, wx.ALL, 3)
        boxSizer2.Add(self.email, 0, wx.ALL, 3)
        sizer.Add(boxSizer2, row = r, col = 1)
        r += 1

        boxSizer3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.nameRadio = wx.RadioButton(self, ID_nameRadio, "Name")
        self.nick = wx.TextCtrl(self, -1, '', size = (110, -1))
        self.first = wx.TextCtrl(self, -1, '', size = (110, -1))
        self.last = wx.TextCtrl(self, -1, '', size = (110, -1))

        self.nameSizer = rcs.RowColSizer()
        self.nameSizer.Add(wx.StaticText(self, -1, 'Nick:'), row = 0, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nameSizer.Add(self.nick, row = 0, col = 3, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nameSizer.Add(wx.StaticText(self, -1, 'First:'), row = 1, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nameSizer.Add(self.first, row = 1, col = 3, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nameSizer.Add(wx.StaticText(self, -1, 'Last:'), row = 2, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nameSizer.Add(self.last, row = 2, col = 3, flag = wx.ALIGN_CENTER_VERTICAL)

        boxSizer3.Add(self.nameRadio, 0, wx.ALL, 3)
        boxSizer3.Add(self.nameSizer, 0, wx.ALL, 3)
        sizer.Add(boxSizer3, row = r, col = 1)
        r += 1

        boxSizer4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.advancedRadio = wx.RadioButton(self, -1, "Advanced")
        self.advancedButton = wx.ToggleButton(self, -1, 'Advanced >>', size = (155, -1))
        boxSizer4.Add(self.advancedRadio, 0, wx.ALL, 3)
        boxSizer4.Add(self.advancedButton, 0, wx.ALL, 3)
        sizer.Add(boxSizer4, row = r, col = 1)

        r += 2

        searchSizer = wx.BoxSizer(wx.VERTICAL)
        self.searchButton = wx.Button(self, -1, "Search", size = (155, 30))
        searchSizer.Add(self.searchButton, 1, wx.ALL, 8)
        sizer.Add(searchSizer, row = r, col = 1)
        r += 1

        ###
        self.iconSet = iconSet

        resultsSizer = wx.BoxSizer(wx.VERTICAL)
        self.results = ResultsList(self, -1, self.iconSet)
        resultsSizer.Add(self.results, 1, wx.ALL | wx.GROW | wx.EXPAND, 8)
        sizer.Add(resultsSizer, row = 0, col = 2, rowspan = r - 0, colspan = 10, flag = wx.EXPAND)

        sizer.AddGrowableCol(2)
        sizer.AddGrowableRow(r-1)

        self.setDefaults()

        self._binds = [
            (self.userID.GetId(), self.userIDRadio.GetId()),
            (self.email.GetId(), self.emailRadio.GetId()),
            (self.nick.GetId(), self.nameRadio.GetId()),
            (self.first.GetId(), self.nameRadio.GetId()),
            (self.last.GetId(), self.nameRadio.GetId()),
        ]

        self.Bind(wx.EVT_RADIOBUTTON, self.onUserIDSelect)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.onToggle, self.advancedButton)
        self.Bind(wx.EVT_TEXT, self.onText)
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter)

        self.Bind(wx.EVT_BUTTON, self.doSearch, id = self.searchButton.GetId())

        # ---
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def _getActiveSearch(self):
        self.results.DeleteAllItems()

        if self.FindWindowById(ID_userIDRadio).GetValue():
            self._searchByUin()
        elif self.FindWindowById(ID_emailRadio).GetValue():
            self._searchByEmail()
        elif self.FindWindowById(ID_nameRadio).GetValue():
            self._searchByName()
        else:
            assert 1 == 2

    def _checkFilled(self, requestedId):
        rc = False
        for tid, rid in self._binds:
            if rid == requestedId:
                if len(self.FindWindowById(tid).GetValue()) > 0:
                    rc = True
                    break
        if not rc:
            wx.MessageBox('''You haven't filled in the search field. Please enter a search term and try again.''', "Search", wx.OK)
        return rc

    def _searchByUin(self):
        if self._checkFilled(ID_userIDRadio):
            evt = NanoEvent(nanoEVT_SEARCH_BY_UIN, self.GetId())
            evt.setVal(self.userID.GetValue())
            wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(evt)

    def _searchByEmail(self):
        if self._checkFilled(ID_emailRadio):
            evt = NanoEvent(nanoEVT_SEARCH_BY_EMAIL, self.GetId())
            evt.setVal(self.email.GetValue())
            wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(evt)

    def _searchByName(self):
        if self._checkFilled(ID_nameRadio):
            evt = NanoEvent(nanoEVT_SEARCH_BY_NAME, self.GetId())
            evt.setVal( (self.nick.GetValue(), self.first.GetValue(), self.last.GetValue()) )
            wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(evt)

    def showBuddy(self, b):

        index = self.results.InsertImageStringItem(sys.maxint, '', 0)
        self.results.SetStringItem(index, 1, b.name)
        self.results.SetStringItem(index, 2, b.first)
        self.results.SetStringItem(index, 3, b.last)
        self.results.SetStringItem(index, 4, b.email)
        self.results.SetStringItem(index, 5, b.uin)
        self.results.SetItemData(index, int(b.uin))

    def onTextEnter(self, evt):
        evt.Skip()

        self.doSearch(evt)

    def onText(self, evt):
        evt.Skip()

        for id1, id2 in self._binds:
            if evt.GetId() == id1:
                if not self.FindWindowById(id2).GetValue():
                    self.FindWindowById(id2).SetValue(True)
                if self.advancedButton.GetValue():
                    self.advancedButton.SetValue(False)
                break

    def onToggle(self, evt):
        evt.Skip()
        self.advancedRadio.SetValue(True)

    def onUserIDSelect(self, evt):
        evt.Skip()

        for id1, id2 in self._binds:
            if evt.GetId() == id2:
                self.FindWindowById(id1).SetFocus()
                break

    def setDefaults(self):
        self.userIDRadio.SetValue(True)
        self.userID.SetFocus()

    def doSearch(self, evt):
        evt.Skip()
        self._getActiveSearch()


class FindUserFrame(wx.Frame, PersistenceMixin):
    def __init__(self, parentFrame, ID, iconSet, title = 'Find/Add Contacts...',
            size = (650, 465), 
            pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX  | wx.MINIMIZE_BOX):

        wx.Frame.__init__(self, None, ID, size = size, style = style,
            title = title)

        self.iconSet = iconSet
        self.mainIcon = wx.EmptyIcon()
        self.mainIcon.CopyFromBitmap(self.iconSet['main'])
        self.SetIcon(self.mainIcon)

        self.panel = FindUserPanel(self, self.iconSet)

        PersistenceMixin.__init__(self, self.panel, 'searchPanel.save')

        self.sb = SearchStatusBar(self)
        self.SetStatusBar(self.sb)

        self.Bind(EVT_RESULT_BY_UIN, self.onResultByUin)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        try:
            self.restoreObjects([self.GetId()], name = "icq")
        except:
            typ, value, tb = sys.exc_info()
            list = traceback.format_tb(tb, None) + \
                traceback.format_exception_only(type, value)
            err = "%s %s" % (
                "".join(list[:-1]),
                list[-1],
            )
            print 'restoreObjects: '
            print err

    def storeWidgets(self):
        self.storeObjects([self], name = "icq")

    def onClose(self, evt):
        self.storeWidgets()
        evt.Skip()

    def onResultByUin(self, evt):
        evt.Skip()
        b = evt.getVal()
        print 'Got it', b
        self.panel.showBuddy(b)

def _test():
    class NanoApp(wx.App):
        def OnInit(self):
            self.iconSet = IconSet()
            self.iconSet.addPath('icons/aox')
            self.iconSet.loadIcons()
            self.iconSet.setActiveSet('aox')            

            frame = FindUserFrame(None, -1, self.iconSet)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = NanoApp(redirect = False)
    app.MainLoop()


if __name__ == '__main__':
    _test()

# ---
