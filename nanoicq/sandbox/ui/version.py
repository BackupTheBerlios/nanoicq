
#
# $Id: version.py,v 1.3 2006/11/10 16:29:26 lightdruid Exp $
#

version_major = 0
version_minor = 1
version_rev = 3
version_status = 'alpha'
version_name = 'Karelia'

version_string = '%d.%d.%d-%s' % (version_major, version_minor, version_rev, version_status)
version_full_string = version_string + ' ("%s")' % version_name

# ---