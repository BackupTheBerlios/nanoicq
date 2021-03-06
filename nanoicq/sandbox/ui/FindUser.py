
#
# $Id: FindUser.py,v 1.22 2006/11/10 16:22:15 lightdruid Exp $
#

import sys
import traceback
import string
from gettext import gettext as _

import wx
import wx.lib.rcsizer as rcs
import wx.lib.mixins.listctrl as listmix

sys.path.insert(0, '../..')
from events import *
from buddy import Buddy
from iconset import IconSet
from persistence import PersistenceMixin
from validator import DigitValidator

ID_RESULTS_LIST = wx.NewId()
ID_ADVANCED = wx.NewId()

class SearchStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(2)
        self.SetStatusWidths([-2, -1])

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



class ResultsList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    ID_ADD_TO_LIST = wx.NewId()
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

        headers = (_("Nick"), _("First Name"), _("Last Name"), _("E-mail"), _("User ID"))
        ii = 1
        for t in headers:
            info.m_text = t
            self.InsertColumnInfo(ii, info)
            ii += 1

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
            (self.ID_ADD_TO_LIST, _("Add to list"), "self.onAddToContactList"),
            (),
            (self.ID_USER_DETAILS, _("User details"), "self.onUserDetails"),
            (self.ID_SEND_MESSAGE, _("Send message"), "self.onSendMessage"),
        )

        # If user clicked outside of filled list
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

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def _grabCurrentUser(self):
        b = Buddy()
        b.name = self.getColumnText(self.currentItem, 1)
        b.first = self.getColumnText(self.currentItem, 2)
        b.last = self.getColumnText(self.currentItem, 3)
        b.email = self.getColumnText(self.currentItem, 4)
        b.uin = self.getColumnText(self.currentItem, 5)
        return b

    def onAddToContactList(self, evt):
        print 'onAddToContactList'
        evt.StopPropagation()

        b = self._grabCurrentUser()

        newEvent = NanoEvent(nanoEVT_ADD_USER_TO_LIST, self.GetId())
        newEvent.setVal(b)
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(newEvent)

    def onUserDetails(self, evt):
        evt.Skip()
        print evt

        b = self._grabCurrentUser()
        newEvent = NanoEvent(nanoEVT_REQUEST_USER_INFO, self.GetId())
        newEvent.setVal(b)
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(newEvent)

    def onSendMessage(self, evt):
        evt.Skip()
        print evt

        b = self._grabCurrentUser()
        evt = NanoEvent(nanoEVT_MESSAGE_PREPARE, self.GetId())
        evt.setVal(b)
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(evt)


ID_userIDRadio = wx.NewId()
ID_emailRadio = wx.NewId()
ID_nameRadio = wx.NewId()


class AdvancedPanel(wx.Panel):

    def __init__(self, parent, ids):
        wx.Panel.__init__(self, parent, ids)

        self._names = []

        sizer = rcs.RowColSizer()

        # 1st
        self.summarySizerB = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Summary'), wx.VERTICAL)
        self.summarySizer = rcs.RowColSizer()

        self.summarySizer.Add(wx.StaticText(self, -1, 'First name:'), row = 0, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.first = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.summarySizer.Add(self.first, row = 0, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.summarySizer.Add(wx.StaticText(self, -1, 'Last name:'), row = 1, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.last = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.summarySizer.Add(self.last, row = 1, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.summarySizer.Add(wx.StaticText(self, -1, 'Nickname:'), row = 2, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.nick = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.summarySizer.Add(self.nick, row = 2, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.summarySizer.Add(wx.StaticText(self, -1, 'E-mail:'), row = 3, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.email = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.summarySizer.Add(self.email, row = 3, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.summarySizer.Add(wx.StaticText(self, -1, 'Gender:'), row = 5, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.gender = wx.Choice(self, -1, size = (137, -1))
        self.summarySizer.Add(self.gender, row = 5, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.summarySizer.Add(wx.StaticText(self, -1, 'Age:'), row = 6, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.age = wx.Choice(self, -1, size = (137, -1))
        self.summarySizer.Add(self.age, row = 6, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.summarySizerB.Add(self.summarySizer, 0, wx.ALL | wx.EXPAND, 0)

        sizer.Add(self.summarySizerB, row = 0, col = 0, flag = wx.EXPAND)

        vlist = ['first', 'last', 'nick', 'email', 'gender', 'age']
        for v in vlist:
            self._names.append(v)

        # 2nd
        self.workSizerB = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Work'), wx.VERTICAL)
        self.workSizer = rcs.RowColSizer()

        self.workSizer.Add(wx.StaticText(self, -1, 'Field:'), row = 0, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.field = wx.Choice(self, -1, size = (137, -1))
        self.workSizer.Add(self.field, row = 0, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.workSizer.Add(wx.StaticText(self, -1, 'Company:'), row = 1, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.company = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.workSizer.Add(self.company, row = 1, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.workSizer.Add(wx.StaticText(self, -1, 'Department:'), row = 2, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.department = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.workSizer.Add(self.department, row = 2, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.workSizer.Add(wx.StaticText(self, -1, 'Position:'), row = 3, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.position = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.workSizer.Add(self.position, row = 3, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.workSizer.Add(wx.StaticText(self, -1, 'Organisation:'), row = 5, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.organisation = wx.Choice(self, -1, size = (137, -1))
        self.workSizer.Add(self.organisation, row = 5, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.workSizer.Add(wx.StaticText(self, -1, 'Keywords:'), row = 6, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.keywords = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.workSizer.Add(self.keywords, row = 6, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.workSizerB.Add(self.workSizer, 1, wx.ALL | wx.EXPAND, 0)

        sizer.Add(self.workSizerB, row = 1, col = 0, flag = wx.EXPAND)

        vlist = ['field', 'company', 'department', 'position', 'organisation', 'keywords']
        for v in vlist:
            self._names.append(v)

        # 3rd
        self.locationSizerB = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Work'), wx.VERTICAL)
        self.locationSizer = rcs.RowColSizer()

        self.locationSizer.Add(wx.StaticText(self, -1, 'Language:'), row = 0, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.language = wx.Choice(self, -1, size = (137, -1))
        self.locationSizer.Add(self.language, row = 0, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.locationSizer.Add(wx.StaticText(self, -1, 'Country:'), row = 1, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.country = wx.Choice(self, -1, size = (137, -1))
        self.locationSizer.Add(self.country, row = 1, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.locationSizer.Add(wx.StaticText(self, -1, 'State:'), row = 2, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.state = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.locationSizer.Add(self.state, row = 2, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.locationSizer.Add(wx.StaticText(self, -1, 'City:'), row = 3, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.city = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.locationSizer.Add(self.city, row = 3, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.locationSizerB.Add(self.locationSizer, 1, wx.ALL | wx.EXPAND, 0)

        sizer.Add(self.locationSizerB, row = 0, col = 2, flag = wx.EXPAND)

        vlist = ['language', 'country', 'state', 'city']
        for v in vlist:
            self._names.append(v)

        # 3th
        self.backgroundSizerB = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Background'), wx.VERTICAL)
        self.backgroundSizer = rcs.RowColSizer()

        self.backgroundSizer.Add(wx.StaticText(self, -1, 'Interests'), row = 0, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.backgroundSizer.Add(wx.StaticLine(self, -1, size = (100, -1)), row = 0, col = 2, flag = wx.ALIGN_CENTER)

        self.backgroundSizer.Add(wx.StaticText(self, -1, 'Category:'), row = 1, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.interestsCategory = wx.Choice(self, -1, size = (137, -1))
        self.backgroundSizer.Add(self.interestsCategory, row = 1, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.backgroundSizer.Add(wx.StaticText(self, -1, 'Keywords:'), row = 2, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.interestsKeywords = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.backgroundSizer.Add(self.interestsKeywords, row = 2, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.backgroundSizer.Add(wx.StaticText(self, -1, 'Past'), row = 3, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.backgroundSizer.Add(wx.StaticLine(self, -1, size = (100, -1)), row = 3, col = 2, flag = wx.ALIGN_CENTER)

        self.backgroundSizer.Add(wx.StaticText(self, -1, 'Category:'), row = 4, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.pastCategory = wx.Choice(self, -1, size = (137, -1))
        self.backgroundSizer.Add(self.pastCategory, row = 4, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.backgroundSizer.Add(wx.StaticText(self, -1, 'Keywords:'), row = 5, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.pastKeywords = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.backgroundSizer.Add(self.pastKeywords, row = 5, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.backgroundSizer.Add(wx.StaticText(self, -1, 'Home page'), row = 6, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.backgroundSizer.Add(wx.StaticLine(self, -1, size = (100, -1)), row = 6, col = 2, flag = wx.ALIGN_CENTER)

        self.backgroundSizer.Add(wx.StaticText(self, -1, 'Category:'), row = 7, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.homePageCategory = wx.Choice(self, -1, size = (137, -1))
        self.backgroundSizer.Add(self.homePageCategory, row = 7, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.backgroundSizer.Add(wx.StaticText(self, -1, 'Keywords:'), row = 8, col = 1, flag = wx.ALIGN_CENTER_VERTICAL)
        self.homePageKeywords = wx.TextCtrl(self, -1, '', size = (137, -1))
        self.backgroundSizer.Add(self.homePageKeywords, row = 8, col = 2, flag = wx.ALIGN_CENTER_VERTICAL)

        self.backgroundSizerB.Add(self.backgroundSizer, 1, wx.ALL | wx.EXPAND, 0)

        sizer.Add(self.backgroundSizerB, row = 1, col = 2, flag = wx.EXPAND)

        vlist = ['interestsCategory', 'interestsKeywords', 
            'pastCategory', 'pastKeywords', 
            'homePageCategory', 'homePageKeywords']
        for v in vlist:
            self._names.append(v)

        # ---
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def prepareDict(self):
        d = {}
        for n in self._names:
            widget = getattr(self, n)
            if isinstance(widget, wx.Choice):
                v = widget.GetStringSelection()
            else:
                v = widget.GetValue()
            if v is not None:
                v = string.strip(v)
                if len(v) > 0:
                    d[n] = v
        return d


class FindUserPanel(wx.Panel):
    protocolList = ["ICQ"]

    def __init__(self, parent, iconSet):
        wx.Panel.__init__(self, parent, -1)

        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = rcs.RowColSizer()
        r = 0

        self.g = wx.Gauge(self, -1, size = (168, 15), style = wx.GA_SMOOTH)
        self.g.SetBezelFace(0)
        self.g.SetShadowWidth(0)
        self.sizer.Add(self.g, row = r, col = 1)
        self.g.Hide()
        r += 1

        protoSizer = rcs.RowColSizer()
        self.protocol = wx.ComboBox(self, -1, self.protocolList[0], size = (110, -1), choices = self.protocolList, style = wx.CB_READONLY)
        protoSizer.Add(wx.StaticText(self, -1, 'Search:'), row = 0, col = 0)
        protoSizer.Add(self.protocol, row = 0, col = 3)
        self.sizer.Add(protoSizer, row = r, col = 1, flag = wx.EXPAND)
        r += 1

        boxSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.userIDRadio = wx.RadioButton(self, ID_userIDRadio, "User ID")
        self.userID = wx.TextCtrl(self, -1, '', size = (155, -1),
            validator = DigitValidator())
        boxSizer1.Add(self.userIDRadio, 0, wx.ALL, 3)
        boxSizer1.Add(self.userID, 0, wx.ALL, 3)
        self.sizer.Add(boxSizer1, row = r, col = 1)
        r += 1

        boxSizer2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.emailRadio = wx.RadioButton(self, ID_emailRadio, "E-mail address")
        self.email = wx.TextCtrl(self, -1, '', size = (155, -1))
        boxSizer2.Add(self.emailRadio, 0, wx.ALL, 3)
        boxSizer2.Add(self.email, 0, wx.ALL, 3)
        self.sizer.Add(boxSizer2, row = r, col = 1)
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
        self.sizer.Add(boxSizer3, row = r, col = 1)
        r += 1

        boxSizer4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        self.advancedRadio = wx.RadioButton(self, -1, "Advanced")
        self.advancedButton = wx.ToggleButton(self, -1, 'Advanced >>', size = (155, -1))
        boxSizer4.Add(self.advancedRadio, 0, wx.ALL, 3)
        boxSizer4.Add(self.advancedButton, 0, wx.ALL, 3)
        self.sizer.Add(boxSizer4, row = r, col = 1)

        r += 2

        searchSizer = wx.BoxSizer(wx.VERTICAL)
        self.searchButton = wx.Button(self, -1, "Search", size = (155, 30))
        searchSizer.Add(self.searchButton, 1, wx.ALL, 8)
        self.sizer.Add(searchSizer, row = r, col = 1)
        r += 1

        ###
        self.iconSet = iconSet

        self.advanced = AdvancedPanel(self, ID_ADVANCED)
        self.advanced.Hide()

        self.resultsSizer = wx.BoxSizer(wx.VERTICAL)
        self.results = ResultsList(self, ID_RESULTS_LIST, self.iconSet)
        self.resultsSizer.Add(self.results, 1, wx.ALL | wx.GROW | wx.EXPAND, 8)
        self.sizer.Add(self.resultsSizer, row = 0, col = 2, rowspan = 30, colspan = 10, flag = wx.EXPAND)

        self.sizer.AddGrowableCol(2)
        self.sizer.AddGrowableRow(r-1)

        self.setDefaults()

        self._binds = [
            (self.userID.GetId(), self.userIDRadio.GetId()),
            (self.email.GetId(), self.emailRadio.GetId()),
            (self.nick.GetId(), self.nameRadio.GetId()),
            (self.first.GetId(), self.nameRadio.GetId()),
            (self.last.GetId(), self.nameRadio.GetId()),
        ]

        self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.onToggle, self.advancedButton)
        self.Bind(wx.EVT_TEXT, self.onText)
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextEnter)

        self.Bind(wx.EVT_BUTTON, self.doSearch, id = self.searchButton.GetId())

        # ---
        self.topSizer.Add(self.sizer, 1, wx.ALL | wx.GROW, 0)
        self.SetSizer(self.topSizer)
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
            self._searchByAdvanced()

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

    def _searchByAdvanced(self):
        d = self.advanced.prepareDict()
        print d
        rc = wx.MessageBox("Advanced search is not implemented yet", '', wx.OK)

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
        self._toggleAdvanced(evt.GetInt())

    def _toggleAdvanced(self, flag, toggleRadio = True):
        self.advancedRadio.SetValue(toggleRadio)
        if flag != 0:
            self.resultsSizer.Detach(self.results)
            self.results.Hide()
            self.resultsSizer.Add(self.advanced, 1, wx.ALL | wx.GROW | wx.EXPAND, 8)
            self.advanced.Show()

            self.advanced.Layout()
            self.sizer.Layout()
            self.Layout()
            self.Refresh()
        else:
            self.resultsSizer.Detach(self.advanced)
            self.advanced.Hide()
            self.resultsSizer.Add(self.results, 1, wx.ALL | wx.GROW | wx.EXPAND, 8)
            self.results.Show()

            self.results.Layout()
            self.sizer.Layout()
            self.Layout()
            self.Refresh()

    def onRadioButton(self, evt):
        evt.Skip()

        for id1, id2 in self._binds:
            if evt.GetId() == id2:
                self.FindWindowById(id1).SetFocus()

                # FIXME: need to hide advanced panel after user switched to
                # different type of search

                #if self.advancedRadio.GetId() != id1:
                #    if self.advanced.IsShown():
                #        self._toggleAdvanced(0, False)

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

