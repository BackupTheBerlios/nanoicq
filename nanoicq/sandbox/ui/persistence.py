
#
# $Id: persistence.py,v 1.6 2006/02/03 10:41:36 lightdruid Exp $
#

import wx
import cPickle

class PersistenceMixin:
    def __init__(self, fileName, objs = []):
        self._fileName = fileName

        # objs is a list of objects we want to store too
        # ATTENTION: all their IDs must be unique and DEFINED explicitly
        self._objs = objs

    def setObjects(self, olist):
        self._objs = olist

    def storeObjects(self, objs = None, name = 'COMMON'):
        if objs is None: objs = self._objs
        d = {}

        for o in objs:
            ids = o.GetName()
            # print 'Processing', o.__class__, ids

            pos = self.FindWindowByName(ids).GetPosition()
            size = self.FindWindowByName(ids).GetSize()

            try:
                sash = self.FindWindowByName(ids).GetSashPosition()
            except:
                sash = None

            d[ids] = (pos, size, sash)

        fn = self._fileName + '.' + name + '.widgets'
        fp = open(fn, "wb")
        cPickle.dump(d, fp)
        fp.close()

    def restoreObjects(self, ids, name = 'COMMON'):
        fn = self._fileName + '.' + name + '.widgets'
        fp = open(fn, "rb")
        d = cPickle.load(fp)
        fp.close()

        for ids in d:
            pos, size, sash = d[ids]
            print 'restoring', ids, pos, size, sash, self.FindWindowByName(ids)

            self.FindWindowByName(ids).SetPosition(pos)
            self.FindWindowByName(ids).SetSize(size)
            if sash is not None:
                self.FindWindowByName(ids).SetSashPosition(sash)
            self.FindWindowByName(ids).Layout()

    def storeGeometry(self):
        fp = open(self._fileName, "wb")
        try:
            pos = self.GetPosition()
            size = self.GetSize()
            cPickle.dump((pos, size), fp)
        except:
            fp.close()
            raise

    def restoreGeometry(self, npos = None, nsize = None):
        pos = None
        size = None
        fp = None
        try:
            fp = open(self._fileName, "rb")
            pos, size = cPickle.load(fp)
        except:
            if fp is not None: fp.close()

        if pos is None: pos = npos
        if size is None: size = nsize

        self.SetPosition(pos)
        self.SetSize(size)
        self.forceVisible()
        self.Layout()

    def forceVisible(self):
        pos = self.GetPosition()

        if pos[0] < 0: pos = wx.Point(0, pos[1])
        if pos[1] < 0: pos = wx.Point(pos[0], 0)

        dsize = wx.GetDisplaySize()
        if pos[0] >= dsize[0]: pos = wx.Point(0, pos[1])
        if pos[1] >= dsize[1]: pos = wx.Point(pos[0], 0)

        self.SetPosition(pos)
        self.Layout()

def _test():
    ID_PANEL = wx.NewId()
    ID_BUTTON = wx.NewId()

    class MyFrame(wx.Frame, PersistenceMixin):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1)
            PersistenceMixin.__init__(self, 'test.save')
            p = wx.Panel(self, ID_PANEL)
            b = wx.Button(p, ID_BUTTON)

            self.setObjects([p, b])
            self.storeObjects()
            self.restoreObjects([ID_PANEL, ID_BUTTON])
            self.Layout()

    class MyApp(wx.App):
        def OnInit(self):
            frame = MyFrame(None)
            self.SetTopWindow(frame)
            frame.Show(True)
            return True

    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    _test()

# ---
