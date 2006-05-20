#!/usr/bin/python

class A:
    val1 = 'v1'
    val2 = 'v2'

    def _collapseLocals(self):
        out = []
        for k in self.__class__.__dict__.keys():
            if not callable(getattr(self, k)) and not k.startswith("__"):
                out.append( (k, getattr(self, k)) )
        return out

    def test1(self, a, *kw, **kws):
        print a, kw, kws

a = A()
#print dir(a)

a.test1('a', b='1')

# ---
