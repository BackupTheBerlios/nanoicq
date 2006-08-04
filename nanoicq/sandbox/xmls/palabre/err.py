
# $Id: err.py,v 1.1 2006/08/04 08:10:19 lightdruid Exp $

ERRORS = {
1 : "Can't find group with id='%d'",
2 : "Can't find group with name = '%s'",
3 : "Can't find information about current user id=%d in users database",

4 : "Can't find room with id='%d'",
5 : "Can't find user id=%d in room id='%d'",
6 : "Can't find user with id='%d'",

7 : "Can't find user with name = '%s'",
8 : "Empty password, room is password protected",
9 : "Internal error: User '%s' does not exists after insert",

10 : "Internal error: can't find user id=%d in 'users' table",
11 : "Internal error: login is unable to find user with id=%d",
12 : "Invalid '%s' attribute in request",

13 : "Invalid password, room is password protected",
14 : "Invalid pvtPassword",
15 : "Leave all rooms: Unable to find user with id = %d",

16 : "Message type %d not yet supported",
17 : "Missing '%s' attribute in request",
18 : "Must be specified either roomId or roomName",

19 : "Not implemented yet",
20 : "Password is too short",
21 : "Property '%s' is not defined in class",

22 : "Room ID (rid) must be specified for personal and private messages",
23 : "Room is password protected, but no publicPassword specified",
24 : "Room is password protected, but publicPassword is too short or empty",

25 : "Room is password protected, invalid pvtPassword",
26 : "Room name not specified",
27 : "Room properties are password protected, but no pvtPassword specified",

28 : "Room with name '%s' already exists",
29 : "Silent period is invalid or not specified",
30 : "Unable to delete room with id='%d' following users are in room: %s",

31 : "Unable to find group id=%d (allowedGroupId)",
32 : "Unable to find user id=%d",
33 : "Unknown database type in config",

34 : "User '%s' already exists with id=%d",
35 : "User id=%d already in allowed list for room id=%d",
36 : "User id=%d already in room id=%d",

37 : "User id=%d can't send messages to room id=%d",
38 : "User id=%d has too low moderation level (%d) to delete group, must be equal or greater than %d",
39 : "User id=%d is not in allowed list for room id=%d",

40 : "User id=%d is offline now",
41 : "User id=%d is set to silent, unable to send message",
42 : "User id=%d not found in allowed list for room id=%d",

43 : "User id=%d not in room id=%d",
44 : "User id='%d' does not exist",
45 : "Wrong value for isblocked, must be 0 or 1",

46 : "Can't find room with name='%s'",
47 : "isBlocked: Can't find user #%d",
48 : "newPvtPassword is not specified",

49 : "newPvtPassword is too short",
50 : "pvtPasswordProtected has invalid value",
}

# Reversed version
_ERRORS_REV = {}
for k in ERRORS:
    _ERRORS_REV[ERRORS[k]] = k

# Reverse dict lookup
def ERRORS_lookup(v):
    return _ERRORS_REV[v]

assert ERRORS_lookup("Can't find group with id='%d'") == 1

# Avoid duplicates
assert len(set(ERRORS.values())) == len(ERRORS.values())

#_ERRORS.sort()

#_ii = 0
#for e in ERRORS:
#    #print "%d : %s," % (_ii, e)
#    print '%d : "%s",' % (_ii, ERRORS[e])
#    ERRORS[_ii] = e
#    _ii += 1

#print ERRORS[1]

# ---
