
#
# $Id: setup.py,v 1.3 2006/08/28 10:03:56 lightdruid Exp $
#

# Just a sample script for nanoicq, it does nothing
# useful for this moment

import sys, glob

from distutils.core import setup
from distutils.command.install_data import install_data

from setuptools import setup, find_packages


datafiles=[
        ('icons/aox', glob.glob('icons/aox/*.ico'))
    ] # only works for bdist and friends

if sys.platform.find("win32", 0, 5) == 0:
    platform="WIN32"
else:
    platform="UNIX"

setup(name = 'NanoICQ',
    version = '0.1',
    description = 'ICQ client',
    author = 'Andrey Sidorenko',
    author_email = 'sidorenko@gmail.com',
    url = "http://nanoicq.berlios.de",
    license = "MIT",
    long_description = """ """,
    platforms = [platform],
    packages=['sandbox','sandbox.ui', 'plugins', 'thirdparty'],
    #packages = find_packages(),
    package_dir = {'zzz': 'plugins'},

    data_files = datafiles)

# ---
