
#
# Stolen from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252158
#
# $Id: antarctica.py,v 1.1 2005/12/21 14:54:26 lightdruid Exp $
#

def frozen(set):
    """Raise an error when trying to set an undeclared name, or when calling
       from a method other than Frozen.__init__ or the __init__ method of
       a class derived from Frozen"""
    def set_attr(self,name,value):
        import sys
        if hasattr(self,name):                                  #If attribute already exists, simply set it
            set(self,name,value)
            return
        elif sys._getframe(1).f_code.co_name is '__init__':     #Allow __setattr__ calls in __init__ calls of proper object types
            for k,v in sys._getframe(1).f_locals.items():
                if k=="self" and isinstance(v, self.__class__):
                    set(self,name,value)
                    return
        raise AttributeError("You cannot add attributes to %s" % self)
    return set_attr

class Frozen(object):
    """Subclasses of Frozen are frozen, i.e. it is impossibile to add
     new attributes to them and their instances."""
    __setattr__=frozen(object.__setattr__)
    class __metaclass__(type):
        __setattr__=frozen(type.__setattr__)

if __name__ == '__main__':

    class Person(Frozen):
        def __init__(self,firstname,lastname):
            self.firstname=firstname
            self.lastname=lastname

    class AgedPerson(Person):
        def __init__(self, firstname, lastname, age):
            Person.__init__(self, firstname, lastname)
            self.age = age
            self.firstname = " ".join(("Aged", firstname))

    me = Person("Michael", "Loritsch")
    agedMe = AgedPerson("Michael", "Loritsch", 31)

    me.firstname = 'abcd'

    try:
        me.a = 'a'
    except AttributeError, msg:
        if not str(msg).startswith('You cannot add attributes to'): raise
    try:
        agedMe.a = 'a'
    except AttributeError, msg:
        if not str(msg).startswith('You cannot add attributes to'): raise

    print 'Passed'

# ---
