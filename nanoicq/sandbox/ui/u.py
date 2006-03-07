
import sys
sys.path.insert(0, '../..')

from utils import *

d = restoreFromFile('userFound_07DA_00C8')
print type(d)

'''
SNAC(15,03)/07DA/00C8   META_BASIC_USERINFO 

Basic user information packet. If success byte doesn't equal 0x0A - it is last SNAC byte. 
'''
assert d[0] == '\x0a'

vals = ['nick', 'first', 'last', 'email', 'city', 'state', 'phone',
    'fax', 'address', 'cell', 'zip']

rest =['coutry_code', 'gmt_offset', 'authorization_flag',
    'webaware_flag', 'dc_permission', 'publish_primary_email_flag']

d = d[1:]

print coldump(d)

for v in vals:
    value, d = parseAsciiz(d)
    #print coldump(d)
    print v, value
    #eval("" = v)

'''
SNAC(15,03)/07DA/00D2   META_WORK_USERINFO 

Work user information packet. If success byte doesn't equal 0x0A - it is last SNAC byte. 
'''

d = restoreFromFile('userFound_07DA_00D2')
assert d[0] == '\x0a'

vals = ['work_city', 'work_state', 'work_phone', 'work_fax',
    'work_address', 'work_zip', ('work_country_code',), 'work_company', 
    'work_department', 'work_position', ('work_occupation_code',),
    'work_webpage' ]

d = d[1:]

for v in vals:
    if type(v) == type(()):
        value, d = parseWordLE(d)
        exec("%s = %s" % (v[0], value))
    else:
        value, d = parseAsciiz(d)
        if len(value) > 0:
            exec("%s = '%s'" % (v, value))
    print v, value

'''
SNAC(15,03)/07DA/00DC   META_MORE_USERINFO 

More user information packet. If success byte doesn't equal 0x0A - it is 
last SNAC byte. This snac contain some data not setable/viewable in current 
ICQ clients (except ICQLite and ICQ2003b), but you can change it thru your 
whitepage on wwp.icq.com. ICQLite (up to build 1150) doesn't use "marital 
status" field too. 
'''

vals = [('age',), ('gender', ''), 'homepage_address', 
    ('birth_year',), ('birth_month', ''), ('birth_day', ''), 
    ('speaking_language_1', ''), ('speaking_language_2', ''), 
    ('speaking_language_3', ''), ('unknown'), 'original_from_city',
    'original_from_state', ('original_from_country_code',), ('timezone', '')
]

d = restoreFromFile('userFound_07DA_00DC')
assert d[0] == '\x0a'

d = d[1:]

for v in vals:
    if type(v) == type(()):
        if len(v) == 1:
            value, d = parseWordLE(d)
        else:
            value, d = parseByteLE(d)
    else:
        value, d = parseAsciiz(d)
    print v, value

'''
SNAC(15,03)/07DA/00E6   META_NOTES_USERINFO 

Notes user information packet. If success byte doesn't 
equal 0x0A - it is last SNAC byte. 
'''

vals = [ 'notes' ]

d = restoreFromFile('userFound_07DA_00E6')
assert d[0] == '\x0a'

d = d[1:]

for v in vals:
    if type(v) == type(()):
        if len(v) == 1:
            value, d = parseWordLE(d)
        else:
            value, d = parseByteLE(d)
    else:
        value, d = parseAsciiz(d)
        if len(value) > 0:
            exec("%s = '''%s'''" % (v, value))
            print eval("%s" % v)
    print v, value


'''
SNAC(15,03)/07DA/00EB   META_EMAIL_USERINFO 

Extended email user information packet. If success byte doesn't 
equal 0x0A - it is last SNAC byte. 
'''

d = restoreFromFile('userFound_07DA_00EB')
assert d[0] == '\x0a'

d = d[1:]

nemail, d = parseByteLE(d)
nemail = int(nemail)

if nemail != 0:
    for ii in range(nemail):
        value, d = parseAsciiz(d)

    pemail_flag, d = parseByteLE(d)
    emailn, d = parseAsciiz(d)
    print emailn

'''
SNAC(15,03)/07DA/00F0   META_INTERESTS_USERINFO 

Interests email user information packet. If success 
byte doesn't equal 0x0A - it is last SNAC byte. 
'''

d = restoreFromFile('userFound_07DA_00F0')
assert d[0] == '\x0a'

d = d[1:]

nelem, d = parseByteLE(d)

for ii in range(int(nelem) - 1):
    interest_code, d = parseByteLE(d)
    interest, d = parseAsciiz(d)
    print interest_code, interest_code

'''
SNAC(15,03)/07DA/00FA   META_AFFILATIONS_USERINFO 

Past/Affilations email user information packet. 
If success byte doesn't equal 0x0A - it is last SNAC byte. 
'''

print '='*40

d = restoreFromFile('userFound_07DA_00FA')
assert d[0] == '\x0a'

d = d[1:]

nelem, d = parseByteLE(d)

for ii in range(int(nelem) - 1):
    past_category_code, d = parseWordLE(d)
    past_keyword, d = parseAsciiz(d)
    print past_category_code, past_keyword

nelem, d = parseByteLE(d)

for ii in range(int(nelem) - 1):
    aff_category_code, d = parseWordLE(d)
    aff_keyword, d = parseAsciiz(d)
    print aff_category_code, aff_keyword

'''
SNAC(15,03)/07DA/010E   META_HPAGECAT_USERINFO 

Homepage category user information packet. If success byte 
doesn't equal 0x0A - it is last SNAC byte. 
'''

d = restoreFromFile('userFound_07DA_010E')
assert d[0] == '\x0a'

d = d[1:]

enabled_flag, d = parseByteLE(d)
enabled_flag = int(enabled_flag)

if enabled_flag != 0:
    homepage_category, d = parseWordLE(d)
    homepage_keywords, d = parseAsciiz(d)
    print homepage_category, homepage_keywords

'''
SNAC(15,03)/07DA/019A   unknown
'''

#d = restoreFromFile('userFound_07DA_019A')
#assert d[0] == '\x0a'
#
#d = d[1:]

#---