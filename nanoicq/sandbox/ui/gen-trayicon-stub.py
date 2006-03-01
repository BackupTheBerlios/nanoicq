#!/usr/bin/python

#
# $Id: gen-trayicon-stub.py,v 1.1 2006/03/01 15:55:03 lightdruid Exp $
#

inside = False

out = open('stub', 'wb')

for line in open('TrayIconWindows.py', 'rb').xreadlines():
    if not inside and line.startswith('class TrayIcon'):
        inside = True
        print >> out, line.rstrip()
        continue
    elif not inside and line.startswith('#'):
        print >> out, line.rstrip()
        continue
    if line.startswith('    def '):
        print >> out, line.rstrip()
        print >> out, " " * 8 + "pass\n"

print >> out, "\n# ---"
out.close()

# ---
