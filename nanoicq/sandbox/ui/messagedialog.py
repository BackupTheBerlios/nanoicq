
#
# $Id: messagedialog.py,v 1.39 2006/08/27 11:45:48 lightdruid Exp $
#

import sys
import traceback
import wx

from wx.lib.splitter import MultiSplitterWindow

from persistence import PersistenceMixin

sys.path.insert(0, '../..')
from events import *
from message import Message, messageFactory
from history import History
from buddy import Buddy
import HistoryDirection

import guidebug

# Default colorset bg/fg for incoming/outgoing messages
_DEFAULT_COLORSET = ("white", "black", "white", "black")

ID_SPLITTER = 8000
ID_BUTTON_SEND = 8001


class MySplitter(MultiSplitterWindow):
    def __init__(self, parent, ID, name):
        MultiSplitterWindow.__init__(self, parent, ID,
            style = wx.SP_LIVE_UPDATE, name = name)

    def SetSashPosition(self, idx, newPos1):
        self._DoSetSashPosition(idx, newPos1)


class NanoTextDropTarget(wx.TextDropTarget):
    def __init__(self, window):
        wx.TextDropTarget.__init__(self)
        self.window = window

    def OnDropText(self, x, y, text):
        log().log("Drop: (%d, %d)\n%s\n" % (x, y, text))

    def _OnDragOver(self, x, y, d):
        return wx.DragCopy


class MessagePanel(wx.Panel):
    def __init__(self, parent, userName):
        wx.Panel.__init__(self, parent, -1)

        self._showSendButton = False

        self._parent = parent
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        box1 = wx.StaticBox(self, -1)
        self.boxSizer1 = wx.StaticBoxSizer(box1, wx.HORIZONTAL)

        self._userUin = wx.StaticText(self, -1, '')
        self.boxSizer1.Add(self._userUin, 0, wx.ALIGN_LEFT | wx.ALL, 3)

        self.boxSizer1.Add(wx.StaticLine(self, -1, style = wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 3)

        # TODO: status must be set by passing argumant or using buddy's properties
        self._status = wx.StaticText(self, -1, 'offline')
        self.boxSizer1.Add(self._status, 1, wx.ALIGN_RIGHT | wx.EXPAND | wx.ALL, 3)

        # 2nd
        box2 = wx.StaticBox(self, -1)
        self.boxSizer2 = wx.StaticBoxSizer(box2, wx.HORIZONTAL)

        self.splitter = MySplitter(self, ID_SPLITTER,
            name = 'splitter_' + userName)

        #
        self.incoming = wx.Panel(self.splitter, style=0)
        self.incomingSizer = wx.BoxSizer(wx.VERTICAL)
        self._incoming = wx.TextCtrl(self.incoming, -1, "",
            style = wx.TE_MULTILINE | wx.TE_RICH2 | wx.CLIP_CHILDREN | wx.TE_READONLY)
        self.incomingSizer.Add(self._incoming, 1, wx.EXPAND, 1)
        self.incoming.SetSizer(self.incomingSizer)
        self.incoming.SetAutoLayout(True)
        self.incomingSizer.Fit(self.incoming)

        #
        self.outgoing = wx.Panel(self.splitter, style=0)
        self.outgoingSizer = wx.BoxSizer(wx.VERTICAL)
        self._outgoing = wx.TextCtrl(self.outgoing, -1, "",
            size=wx.DefaultSize, style = wx.TE_MULTILINE | wx.TE_RICH2)

        # Send messages on Ctrl-Enter
        # FIXME: ugly
        self._outgoing.Bind(wx.EVT_KEY_DOWN, self._parent.onCtrlEnter)

        self.dropTarget = NanoTextDropTarget(self._outgoing)
        self._outgoing.SetDropTarget(self.dropTarget)

        self.outgoingSizer.Add(self._outgoing, 1, wx.EXPAND, 1)
        self.outgoing.SetSizer(self.outgoingSizer)
        self.outgoing.SetAutoLayout(True)
        self.outgoingSizer.Fit(self.incoming)

        self.splitter.SetOrientation(wx.VERTICAL)
        self.splitter.SetMinimumPaneSize(20)
        self.splitter.AppendWindow(self.incoming)
        self.splitter.AppendWindow(self.outgoing)

        self._pane = self.splitter
        self.outgoing.SetFocus()

        self.boxSizer2.Add(self._pane, 1, wx.EXPAND)

        if self._showSendButton:
            # 3rd
            box3 = wx.StaticBox(self, -1)
            self.boxSizer3 = wx.StaticBoxSizer(box3, wx.HORIZONTAL)
            self.buttonOk = wx.Button(self, ID_BUTTON_SEND, 'Send',
                name = 'buttonOk_' + userName)
            self.boxSizer3.Add(self.buttonOk, 0, wx.ALIGN_RIGHT)

        # 4th
        box4 = wx.StaticBox(self, -1)
        self.boxSizer4 = wx.BoxSizer(wx.HORIZONTAL)
        self._sb = wx.StaticText(self, -1, '')
        self.boxSizer4.Add(self._sb, 0, wx.ALIGN_RIGHT)

        #
        self.sizer.Add(self.boxSizer1, 0, wx.EXPAND)
        self.sizer.Add(self.boxSizer2, 4, wx.EXPAND)
        if self._showSendButton:
            self.sizer.Add(self.boxSizer3, 0, wx.EXPAND)
        self.sizer.Add(self.boxSizer4, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.SetAutoLayout(True)

        # Bug fix for [ wxwindows-Bugs-1428169 ] wx.StaticBox seems to be interfering  with DnD
        box1.Lower()
        box2.Lower()
        if self._showSendButton:
            box3.Lower()


class MessageDialog(wx.Frame, PersistenceMixin):
    def __init__(self, parentFrame, ID, user, message, colorSet = _DEFAULT_COLORSET,
            size = wx.DefaultSize, 
            pos = wx.DefaultPosition,
            style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX  | wx.MINIMIZE_BOX):

        wx.Frame.__init__(self, None, ID, user.name, size = size,
            style = style, name = 'message_dialog_' + user.name)


        assert isinstance(user, Buddy)
        self._user = user

        self._parentFrame = parentFrame

        self._history = History.restore(self._user)

        print len(colorSet), len(_DEFAULT_COLORSET)
        assert len(colorSet) == 4
        self._colorSet = colorSet

        self.topPanel = MessagePanel(self, 'junk')
        PersistenceMixin.__init__(self, self.topPanel, 'widgets.save')

        # ---
        self.setUserName(self._user)
        self.setTitle(self._user)

        try:
            self.restoreObjects([self.GetId(), ID_BUTTON_SEND, ID_SPLITTER],
                name = self._user.name)
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

        # Shortcuts
        self._incoming = self.topPanel._incoming
        self._outgoing = self.topPanel._outgoing

        # ---
        self.Bind(wx.EVT_BUTTON, self.onSendMessage, id = ID_BUTTON_SEND)
        self.Bind(wx.EVT_BUTTON, self.onCancel, id = wx.ID_CANCEL)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.populateHistory()

        if message is not None:
            self.updateMessage(message)

    def Show(self, flag = True):
        wx.Frame.Show(self, flag)
        self._outgoing.SetFocus()

    def Raise(self):
        wx.Frame.Raise(self)
        self._outgoing.SetFocus()

    def populateHistory(self, mmax = None):
        '''
        Fill 'incoming' text with messages from history, up to mmax messages
        '''
        for h in self._history:
            if h is not None:
                self.updateMessage(h)

    def onClose(self, evt):
        self.storeWidgets()
        self.storeHistory()
        self.Hide()
        # Do not process event, just hide window

    def storeHistory(self):
        self._history.store(self._user)

    def setStatus(self, status):
        self.topPanel._status.SetLabel(status)
        self.topPanel._status.Refresh()

    def onCtrlEnter(self, evt):
        keycode = evt.GetKeyCode()

        # 308 (13, 372)
        if keycode in [372, 13]:
            if evt.ControlDown():
                self.onSendMessage(None)
                return

        evt.Skip()

    def addToHistory(self, msg):
        self._history.append(msg)

    def getBuddy(self):
        ''' Return buddy assigned to this conversation '''
        return self._user

    def storeWidgets(self):
        objs = [self, self.topPanel.splitter]
        if self.topPanel._showSendButton:
            objs.append(self.topPanel.buttonOk)

        self.storeObjects(objs,
            name = self._user.name)

        self.storeHistory()

        evt = NanoEvent(nanoEVT_DIALOG_CLOSE, self.GetId())
        evt.setVal(self.GetId())
        print self._parentFrame
        wx.PostEvent(self._parentFrame, evt)

    def onCancel(self, evt):
        self.storeWidgets()
        evt.Skip()

    def _colorize(self, message):
        txt = self._history.format(message, timestamp = True) + '\n'

        if message.getDirection() == HistoryDirection.Incoming:
            bg, fg = self._colorSet[0 : 2]
        else:
            bg, fg = self._colorSet[2 : 4]

        curPos = self._incoming.GetInsertionPoint()
        self._incoming.AppendText(txt)
        self._incoming.SetStyle(curPos, self._incoming.GetInsertionPoint(), wx.TextAttr(fg, bg))

    def updateMessage(self, message):
        self._colorize(message)

        self._incoming.Refresh()
        self._incoming.Update()

        self._incoming.ShowPosition(0)
        self._incoming.ScrollLines(self._incoming.GetNumberOfLines() - 2)

        self._incoming.Refresh()
        self._incoming.Update()

        if message.getDirection() == HistoryDirection.Outgoing:
            self._outgoing.Clear()
            self._outgoing.Update()
        
    def onSendMessage(self, evt):
        print 'onSendMessage()'
        print 'Sending send message event for dialog...', self.GetId()

        print 'Name: ', self._user.name
        print 'uin: ', self._user.uin, type(self._user.uin)

        message = messageFactory("icq",
            self._user.name, self._user.uin,
            self._outgoing.GetValue(), HistoryDirection.Outgoing)

        self._history.append(message)

        evt = NanoEvent(nanoEVT_SEND_MESSAGE, self.GetId())
        evt.setVal( (self._user, message) )
        wx.GetApp().GetTopWindow().GetEventHandler().AddPendingEvent(evt)

        # Update UI
        evt.Skip()
        self.updateMessage(message)

    def setTitle(self, b):
        self.SetTitle(b.name)

    def setUserName(self, b):
        self.topPanel._userUin.SetLabel(b.uin)
        self.topPanel._status.SetLabel(b.status)


def _test():
    class TopFrame(wx.Frame):
        def __init__(self, parentFrame, title):
            wx.Frame.__init__(self, parentFrame, -1, title,
                pos=(150, 150), size=(350, 200))
            wx.Panel(self, -1)

            message = messageFactory("icq", 'user', '12345', 'text', HistoryDirection.Incoming)

#            h = History()
            b = Buddy()
            b.name = 'user'
            b.uin = '123456'
            self.d = MessageDialog(self, -1, b, message)
            self.d.Show(True)

            wx.CallAfter(self.a)

        def a(self):
            self.d.Raise()

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
