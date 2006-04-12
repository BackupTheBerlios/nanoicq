
#
# $Id: iconset.py,v 1.8 2006/04/12 13:45:58 lightdruid Exp $
#

import wx
import os
import sys
import warnings

sys.path.insert(0, '../..')
from icq import log

class IconSetException(Exception): pass

class IconSet:
    FULL_SET = ['main', 'online', 'offline', 'na', 'dnd', 'free', 'invisible', 'away', 'occupied', 'empty']
    _EXTENSIONS = ['.ico']

    def __init__(self):
        self._path = []
        self._icons = {}
        self._activeSet = None

    def __getitem__(self, a):
        return self._activeSet[a]

    def setActiveSet(self, s):
        assert s is not None
        self._activeSet = self._icons[s]

    def addPath(self, path, alias = None):
        ''' Add alias and path where to search icons '''
        npath = os.path.abspath(path)
        if os.path.isdir(npath):
            if npath not in self._path:
                if alias is None:
                    alias = os.path.basename(npath)
                self._path.append((alias, npath))
        else:
            log().log("Passed wrong icon set path: '%s'" % str(path))
            raise IconSetException("Wrong path")

    def _getIconType(self, ext):
        '''
        Determine icon's type from file extension
        '''
        if ext == '.ico': return wx.BITMAP_TYPE_ICO

        log().log("Passed wrong icon type: '%s'" % str(ext))
        raise IconSetException("Unknown file type: '%s'" % ext)

    def _isFullSet(self, icons):
        return len(icons.keys()) == len(self.FULL_SET)

    def loadIcons(self, adjust_missing = True):
        '''
        Load icon sets and create null'ed icons if some of
        icons are missing in icon set
        '''

        for alias, path in self._path:

            def loadIcon(icons, dir, entries):
                for e in entries:
                    fullName = os.path.join(dir, e)
                    name, ext = os.path.splitext(e)
                    ext = ext.lower()
                    if ext not in self._EXTENSIONS:
                        continue

                    name = name.lower()
                    if name not in self.FULL_SET:
                        continue

                    try:
                        img = wx.Image(fullName)
                        icon = wx.BitmapFromImage(img.Scale(16, 16))
                    except Exception, e:
                        log().log("Got exception while loading icon: %s" % str(e))
                        continue

                    icons[name] = icon

            icons = {}
            os.path.walk(path, loadIcon, icons)

            if not self._isFullSet(icons):
                log().log("Loaded '%s' (not complete) icon set" % alias)

                if adjust_missing:
                    self._adjustMissing(icons)
            else:
                log().log("Loaded '%s' icon set" % alias)

        self._icons[alias] = icons

    def _adjustMissing(self, icons):
        ''' Create missing (empty) icons for icon set '''
        s = set(self.FULL_SET)
        for name in s.difference(icons.keys()):
            icons[name] = wx.NullIcon

    def dump(self):
        for alias in self._icons:
            print 'Icon set:', alias
            for img in self._icons[alias]:
                print '\t', img


def _test():
    w = wx.App(False)
    wx.InitAllImageHandlers()

    ic = IconSet()
    ic.addPath('icons/aox/')
    ic.loadIcons()
    ic.dump()
    ic.setActiveSet('aox')
    ic['offline']


if __name__ == '__main__':
    _test()

# ---
