
"""
This is a way to save the startup time when running img2py on lots of
files...
"""

import sys

from wx.tools import img2py


command_lines = [
    "-u -i -n LimeWire LimeWireP2P-16.ico images.py",
    "-u -i -n Smiles -m #FFFFFF smiles2.bmp images.py",
]

if __name__ == "__main__":
    for line in command_lines:
        args = line.split()
        img2py.main(args)

# ---
