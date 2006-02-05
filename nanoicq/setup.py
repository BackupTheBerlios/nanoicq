
#
# $Id: setup.py,v 1.2 2006/02/05 16:07:19 lightdruid Exp $
#

# Just a sample script for nanoicq, it does nothing
# useful for this moment

import sys, glob

from distutils.core import setup
from distutils.command.install_data import install_data


datafiles=[
        ('icons/aox', glob.glob('icons/aox/*.ico'))
    ] # only works for bdist and friends

if sys.platform.find("win32", 0, 5) == 0:
    platform="WIN32"
else:
    platform="UN*X"

setup(name = 'NanoICQ',
      version = '0.1',
      description = 'ICQ client',
      author = 'Andrey Sidorenko',
      author_email = 'sidorenko@gmail.com',
      url = "http://nanoicq.berlios.de",
      license = "MIT",
      long_description = """ """,
      platforms = [platform],
      packages=['sandbox','sandbox.ui'],
      data_files = datafiles)

# ---
