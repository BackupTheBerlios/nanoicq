
# $Id: DB.py,v 1.1 2006/07/10 23:29:15 lightdruid Exp $

import cx_Oracle as CX

class PConnection(CX.Connection):
    pass

def connect(user, password, tns):
    #return CX.connect(user, password, dsn, mode, handle, pool, threaded, twophase)
    return CX.connect(user, password, tns)

def begin():
    return CX.begin()

def commit():
    return CX.commit()

def rollback():
    return CX.rollback()

if __name__ == '__main__':
    pc = PConnection('admin', 'admin', 'HPORA')
    c = connect('admin', 'admin', 'HPORA')

    curs = pc.cursor()
    curs.execute("select * from dual")
    rs = curs.fetchall()
    assert len(rs) == 1 and rs[0][0] == 'X'

    c.close()
    pc.close()

# ---
