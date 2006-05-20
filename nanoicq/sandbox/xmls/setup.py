#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup

#samples_dir = "doc/samples"

#samples_files = os.listdir (samples_dir)

#def samples_string(str):
#    return "%s/%s" % (samples_dir, str)

setup(name = "Palabre",
      version = "0.4",
      description = "XML Socket Python Server",
      long_description = "Flash XML Multiuser Socket Server :-)",
      author = "Célio Conort",
      author_email = "palabre-dev@lists.tuxfamily.org",
      url = "http://palabre.gavroche.net/",
      license = "GPL, see COPYING for details",
      platforms = "Linux",
      packages = ["palabre"],
      scripts = ["scripts/palabre"],
      data_files = [
                    ("/etc", ["etc/palabre.conf"]),
		    ("/usr/local/share/doc/palabre", ["doc/README"]),
		 		   ]
     )
#   ("/usr/local/share/doc/palabre/samples", map(samples_string, samples_files)),
