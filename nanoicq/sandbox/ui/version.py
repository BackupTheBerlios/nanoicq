
#
# $Id: version.py,v 1.1 2006/02/23 14:23:30 lightdruid Exp $
#

version_major = 0
version_minor = 1
version_rev = 1
version_status = 'alpha'
version_name = 'The Game'

version_string = '%d.%d.%d-%s' % (version_major, version_minor, version_rev, version_status)
version_full_string = version_string + ' ("%s")' % version_name

# ---