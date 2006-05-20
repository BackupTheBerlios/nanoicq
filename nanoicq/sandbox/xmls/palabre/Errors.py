#!/usr/bin/python

# $Id: Errors.py,v 1.1 2006/05/20 21:47:54 lightdruid Exp $

from util import *

[
E_NO_ERROR,
E_INVALID_SESSION_ID,

E_ROOM_MANAGE_EXISTS,
E_ROOM_MANAGE_PASSWORD,
E_ROOM_MANAGE_LEVEL,

E_USER_MANAGE_NOT_EXISTS,
E_USER_MANAGE_PASSWORD,
E_USER_MANAGE_LEVEL,

E_ROOM_ACCESS_DENIED,
E_ROOM_NOT_EXISTS,
E_ROOM_INCORRECT_GID,

E_GROUP_MODERATION_LEVEL,
E_GROUP_MANAGE_LEVEL,

E_DB_UNSUFFICIENT_RIGHTS 

] = range(14)

_loc = [x for x in locals().keys() if x.startswith('E_')]
 
class Errors:

    def __init__(self):
        self.loc = _loc

    def __getitem__(self, ndx):
        if type(ndx) == type(0):
            return self.loc[ndx]
        return self.loc.index(ndx)


if __name__ == '__main__':
    e = Errors()
    print e[12]
    print e['E_DB_UNSUFFICIENT_RIGHTS']

#---

