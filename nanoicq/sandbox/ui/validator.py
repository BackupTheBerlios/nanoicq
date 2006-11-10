
#
# $Id: validator.py,v 1.1 2006/11/10 16:22:15 lightdruid Exp $
#

import string

import wx

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

class DigitLengthValidator(DigitValidator):
    def __init__(self, flag = _DIGIT_ONLY, pyVar = None, maxLen=-1):
        DigitValidator.__init__(self)
        self.flag = flag
        self.maxLen = maxLen

        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return DigitLengthValidator(self.flag, maxLen = self.maxLen)

    def OnChar(self, event):
        key = event.KeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if self.flag == _DIGIT_ONLY and chr(key) in string.digits:
            tc = self.GetWindow()
            val = tc.GetValue()

            if len(val) < self.maxLen:
                event.Skip()
                return

        if not wx.Validator_IsSilent():
            wx.Bell()

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()

        return DigitLengthValidator.Validate(win) and len(val) <= self.maxValue
        
# ---
