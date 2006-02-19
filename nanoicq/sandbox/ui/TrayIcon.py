
#
# $Id: TrayIcon.py,v 1.7 2006/02/19 14:49:52 lightdruid Exp $
#

# The piece stolen from wxPython demo

import sys

if sys.platform == 'win32':
    from TrayIconWindows import *
else:
    class TrayIcon:
        def __init__(self, frame, icon, iconSet):
            pass

        def setToolTip(self, toolTip):
            pass

        def CreatePopupMenu(self):
            pass

        def MakeIcon(self, img):
            pass

        def onCancelTaskBarActivate(self, evt):
            pass

        def onCancelTaskBarClose(self, evt):
            pass

        def onCancelTaskBarChange(self, evt):
            pass

        def onCancelTaskBarRemove(self, evt):
            pass

        def Destroy(self):
            pass

# ---
