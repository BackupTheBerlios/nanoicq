
#
# $Id: setup.py,v 1.4 2006/08/28 10:46:16 lightdruid Exp $
#

# Just a sample script for nanoicq, it does nothing
# useful for this moment

import sys, glob

from distutils.core import setup
from distutils.command.install_data import install_data

from setuptools import setup, find_packages


datafiles = [
        ('icons/aox', glob.glob('sandbox/ui/icons/aox/*')),
]

if sys.platform.find("win32", 0, 5) == 0:
    platform="WIN32"
else:
    platform="UNIX"

p_packages = list(find_packages())
p_packages.append("plugins/weather")

setup(
    name = 'NanoICQ',
    version = '0.1',
    description = 'ICQ client',
    author = 'Andrey Sidorenko',
    author_email = 'sidorenko@gmail.com',
    url = "http://nanoicq.berlios.de",
    license = "MIT",
    long_description = """ """,
    platforms = [platform],
    scripts = glob.glob("*.py"),
    #packages=['sandbox','sandbox.ui', 'plugins', 'thirdparty'],
    #py_modules = ["plugins/weather"],
    packages = p_packages,
    data_files = datafiles
)

# ---
