
#
# Multimethods
#
# $Id: mm.py,v 1.2 2006/01/04 12:22:36 lightdruid Exp $
#

# This code is from http://www.artima.com/forums/flat.jsp?forum=106&thread=101605 

registry = {}

class MultiMethod(object):
    def __init__(self, name):
        self.name = name
        self.typemap = {}
    def __call__(self, *args):
        types = tuple(arg.__class__ for arg in args) # a generator expression!
        function = self.typemap.get(types)
        if function is None:
            raise TypeError("no match")
        return function(*args)
    def register(self, types, function):
        if types in self.typemap:
            raise TypeError("duplicate registration")
        self.typemap[types] = function


def multimethod(*types):
    def register(function):
        function = getattr(function, "__lastreg__", function)
        name = function.__name__
        mm = registry.get(name)
        if mm is None:
            mm = registry[name] = MultiMethod(name)
        mm.register(types, function)
        mm.__lastreg__ = function
        return mm
    return register


class SymmetricMM(MultiMethod):
    def __call__(self, *args):
        types = tuple(sorted(arg.__class__ for arg in args)) 
        function = self.typemap.get(types)
        if function is None:
            raise TypeError("no match")
        return function(*args)


def symmetric_mm(*types):
    def register(function):
        name = function.__name__
        mm = registry.get(name)
        if mm is None:
            mm = registry[name] = SymmetricMM(name)
        mm.register(tuple(sorted(types)), function)
        return mm
    return register

if __name__ == '__main__':
    import unittest

    @symmetric_mm(int, float)
    def test(a, b):
        return a * b

    @multimethod(int, float)
    def f(a, b):
        return a * b

    class InterfaceTest(unittest.TestCase):

        def testSymmetricPositive(self):
            test(1, 1.0)
            test(1.0, 1)

        def testSymmetricNegative(self):
            self.assertRaises(TypeError, test, 1.0, 1.0)

        def testMMPositive(self):
            f(1, 1.0)
   
        def testMMNegative(self):
            self.assertRaises(TypeError, f, 1.0, 1)
            self.assertRaises(TypeError, f, 1.0, 1.0)

unittest.main()
 
# ---

