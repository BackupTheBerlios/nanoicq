
#
# $Id: slider.py,v 1.2 2006/01/25 16:21:54 lightdruid Exp $
#

from threading import *

import wx

havePopupWindow = 1
if wx.Platform == '__WXMAC__':
    havePopupWindow = 0
    wx.PopupWindow = wx.PopupTransientWindow = wx.Window

#---------------------------------------------------------------------------

class TestPopup(wx.PopupWindow):
    """Adds a bit of text and mouse movement to the wx.PopupWindow"""
    def __init__(self, parent, style):
        wx.PopupWindow.__init__(self, parent, style)
        self.SetBackgroundColour("CADET BLUE")

        st = wx.StaticText(self, -1,
                          "This is a special kind of top level\n"
                          "window that can be used for\n"
                          "popup menus, combobox popups\n"
                          "and such.\n\n"
                          "Try positioning the demo near\n"
                          "the bottom of the screen and \n"
                          "hit the button again.\n\n"
                          "In this demo this window can\n"
                          "be dragged with the left button\n"
                          "and closed with the right."
                          ,
                          pos=(10,10))

        sz = st.GetBestSize()
        self.SetSize( (sz.width+20, sz.height+20) )

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

        st.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        st.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        st.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        st.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

        self.SetPosition((0, 0))

        self.initPos = self.GetPositionTuple()
        pos = self.initPos
        print 'init slide... relative to parent', pos
        pos = self.ClientToScreenXY(pos[0], pos[1])
        print 'init slide... relative to screen', pos

        self.gap = 0.0
        self.maxPixels = 50
        self.pixels = 0

        wx.CallAfter(self.Refresh)
        wx.CallAfter(self.setTimer)

    def updateGap(self):
        self.gap += 0.001
        self.pixels += 1

    def setTimer(self):
        self.timer = Timer(self.gap, self.slide)
        self.updateGap()
        if self.pixels >= self.maxPixels:
            self.Refresh()
            return
        self.timer.start()

    def slide(self):
        #print 'moving...'

        pos = self.GetPositionTuple()
        self.MoveXY(pos[0] - self.initPos[0], pos[1] - self.initPos[1] + 1)

        wx.CallAfter(self.setTimer)
        return

        print 'slide... relative to parent', pos
        pos = self.ClientToScreenXY(pos[0], pos[1])
        print 'slide... relative to screen', pos
        print 'rect', self.GetRect()
        sz = self.GetSize()
        print 'size', sz
        pos = (pos[0], pos[1] + 1)
        print '->', pos
        self.MoveXY(pos[0], pos[1])
#        self.MoveXY(0, 1)

        wx.CallAfter(self.setTimer)

    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0,0))
        self.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            nPos = (self.wPos.x + (dPos.x - self.ldPos.x),
                    self.wPos.y + (dPos.y - self.ldPos.y))
            self.Move(nPos)

    def OnMouseLeftUp(self, evt):
        self.ReleaseMouse()

    def OnRightUp(self, evt):
        self.Show(False)
        self.Destroy()


class TestTransientPopup(wx.PopupTransientWindow):
    """Adds a bit of text and mouse movement to the wx.PopupWindow"""
    def __init__(self, parent, style, log):
        wx.PopupTransientWindow.__init__(self, parent, style)
        self.log = log
        self.SetBackgroundColour("#FFB6C1")
        st = wx.StaticText(self, -1,
                          "wx.PopupTransientWindow is a\n"
                          "wx.PopupWindow which disappears\n"
                          "automatically when the user\n"
                          "clicks the mouse outside it or if it\n"
                          "(or its first child) loses focus in \n"
                          "any other way."
                          ,
                          pos=(10,10))
        sz = st.GetBestSize()
        self.SetSize( (sz.width+20, sz.height+20) )

    def ProcessLeftDown(self, evt):
        self.log.write("ProcessLeftDown\n")
        return False

    def OnDismiss(self):
        self.log.write("OnDismiss\n")



class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        wx.Panel.__init__(self, parent, -1)
        self.log = log

        b = wx.Button(self, -1, "Show wx.PopupWindow", (25, 50))
        self.Bind(wx.EVT_BUTTON, self.OnShowPopup, b)

        b = wx.Button(self, -1, "Show wx.PopupTransientWindow", (25, 95))
        self.Bind(wx.EVT_BUTTON, self.OnShowPopupTransient, b)

        # This isn't working so well, not sure why. Commented out for
        # now.
        
#        b = wx.Button(self, -1, "Show wx.PopupWindow with listbox", (25, 140))
#        self.Bind(wx.EVT_BUTTON, self.OnShowPopupListbox, b)


    def OnShowPopup(self, evt):
        win = TestPopup(self, wx.SIMPLE_BORDER)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = evt.GetEventObject()
        pos = btn.ClientToScreen( (0,0) )
        sz =  btn.GetSize()
#        win.Position(pos, (0, sz[1]))

        win.Show(True)


    def OnShowPopupTransient(self, evt):
        win = TestTransientPopup(self,
                                 wx.SIMPLE_BORDER,
                                 self.log)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = evt.GetEventObject()
        pos = btn.ClientToScreen( (0,0) )
        sz =  btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()


    def OnShowPopupListbox(self, evt):
        win = TestPopupWithListbox(self, wx.NO_BORDER, self.log)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = evt.GetEventObject()
        pos = btn.ClientToScreen( (0,0) )
        sz =  btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Show(True)

# This class is currently not implemented in the demo. It does not
# behave the way it should, so for the time being it's only here
# for show. If you figure out how to make it work, please send
# a corrected file to Robin! 
class TestPopupWithListbox(wx.PopupWindow):
    def __init__(self, parent, style, log):
        wx.PopupWindow.__init__(self, parent, style)

        import keyword

        self.lb = wx.ListBox(self, -1, choices = keyword.kwlist)
        #sz = self.lb.GetBestSize()
        self.SetSize((150, 75)) #sz)
        self.lb.SetSize(self.GetClientSize())
        self.lb.SetFocus()
        self.Bind(wx.EVT_LISTBOX, self.OnListBox)
        self.lb.Bind(wx.EVT_LEFT_DOWN, self.OnLeft)

    def OnLeft(self, evt):
        obj = evt.GetEventObject()
        print "OnLeft", obj
        print 'Selected: %s' % obj.GetStringSelection()
        obj.Show(False)
        evt.Skip()

    def OnListBox(self, evt):
        obj = evt.GetEventObject()
        print "OnListBox", obj
        print 'Selected: %s' % obj.GetString()
        evt.Skip()



#---------------------------------------------------------------------------

def runTest(frame, nb, log):
    if havePopupWindow:
        win = TestPanel(nb, log)
        return win
    else:
        from Main import MessagePanel
        win = MessagePanel(nb, 'wx.PopupWindow is not available on this platform.',
                           'Sorry', wx.ICON_WARNING)
        return win

import sys

class NanoApp(wx.App):
    def OnInit(self):
        frame = wx.Frame(None, -1, "NanoICQ")
        p = TestPanel(frame, sys.stdout)
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

wx.InitAllImageHandlers()
app = NanoApp(redirect = False)
app.MainLoop()

# ---
