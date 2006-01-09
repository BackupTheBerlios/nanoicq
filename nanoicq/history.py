
#
# $Id: history.py,v 1.1 2006/01/09 16:26:07 lightdruid Exp $
#

class History:
    def __init__(self):
        self._d = []

    def __getitem__(self, n):
        return self._d[n]

    def __delitem__(self, n):
        del self._d[n]

    def append(self, v):
        self._d.append(v)

def _test():
    h = History()

if __name__ == '__main__':
    _test()

# ---
