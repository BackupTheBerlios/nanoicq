
#
# $Id: version.py,v 1.2 2006/03/14 15:47:56 lightdruid Exp $
#

version_major = 0
version_minor = 1
version_rev = 2
version_status = 'alpha'
version_name = 'Camelot'

version_string = '%d.%d.%d-%s' % (version_major, version_minor, version_rev, version_status)
version_full_string = version_string + ' ("%s")' % version_name

# ---