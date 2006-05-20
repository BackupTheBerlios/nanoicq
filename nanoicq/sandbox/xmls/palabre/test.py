#!/usr/bin/python

import MySQLdb as D

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

#a = A()
#print dir(a)

#a.test1('a', b='1')

dbs = []

for i in range(500):
    db = D.connect(
                host = "10.3.13.7",
                port = 3306,
                user = "postnuke", 
                passwd = "postnuke", 
                db = "test")
    dbs.append(db)

for d in dbs:
    print d
    c = d.cursor()
    c.execute("select * from user where 1=2")
    c.fetchall()
 
# ---
