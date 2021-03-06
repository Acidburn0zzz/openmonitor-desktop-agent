
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com> 
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


import os
# Override the setup name in the main setup.py
from setuptools import setup
import sys

encoding = sys.getfilesystemencoding()

if hasattr(sys,'frozen'):
    ROOT_DIR = os.path.dirname(unicode(sys.executable,encoding))
    ROOT_DIR = os.path.join(ROOT_DIR,'icmagent')  #the address is the EXE execute path
else:
    ROOT_DIR = os.path.abspath(
                    os.path.join(os.path.dirname(unicode(__file__,encoding)),os.path.pardir))

print ROOT_DIR
ROOT_DIR="/Volumes/EXT1/bastiao/Umit/github/openmonitor-desktop-agent"
if os.path.exists(os.path.join(ROOT_DIR,'umit')):
     sys.path.insert(0, ROOT_DIR)
     execfile(os.path.join(ROOT_DIR, 'deps', 'umit-common', 'utils', 'importer.py'))
     sys.path.insert(0, os.path.join(ROOT_DIR, 'deps'))
     sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'icm-common'))
     sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'umit-common'))
     sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'higwidgets'))
else:
     raise Exception("Can't find root dir.")


from install_scripts import common



import re
import sys

from stat import *
from glob import glob

import os
import os.path
import shutil

from distutils.core import setup, Extension, Command
from distutils.command.install import install
from distutils.command.build import build
from distutils.command.sdist import sdist
from distutils import log, dir_util

from umit.icm.agent.Version import VERSION

from install_scripts.common import *
from install_scripts import common

#ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


# py2app requires the values in the app's list to have known extensions, but
# bin/umit doesn't. Here bin/umit is renamed to bin/umit_main.py and the old
# name is stored in common.OLD_UMIT_MAIN so it can be renamed again later.
import shutil
#shutil.move(common.UMIT_MAIN, common.ICM_AGENT_MAIN + '_main.py')
#common.OLD_UMIT_MAIN = common.ICM_AGENT_MAIN
common.ICM_AGENT_MAIN = os.path.join(common.BIN_DIRNAME, 'icm-agent')




##################### Umit banner #######################################
print
print "%s OpenMonitor Desktop Agent for Mac OS %s %s" % ("#" * 10, VERSION, "#" * 10)
print
#########################################################################

setup(
        name         = 'icm-agent',
        version      =  VERSION,
        description  = 'Open Monitor Desktop Agent made easy',
        author       = 'Umit Group',
        author_email = 'Umit-devel@lists.sourceforge.net',  
        url          = 'http://www.openmonitor.org',
        download_url = 'http://www.openmonitor.org',
        maintainer = 'Adriano Monteiro',
        maintainer_email = 'adriano@umitproject.org',       
        license      = 'GNU GPL 2',
        requires     = ['gtk'],
        platforms    = ['Platform Independent'],        
        zipfile      = "lib/library.zip",
        #options = options,
        #data_files   = data_files,
        #scripts      = [os.path.join('icmagent','bin','icm-agent')],
        
        app = [common.ICM_AGENT_MAIN],
        options = {'py2app': {
            'argv_emulation': False,
            'compressed': True,
            'packages': [],
            'includes': []
            }
            },
        setup_requires = ["py2app"],
        packages     = ['umit', 
                      #'umit.icm'
                      #'icmagent.bin','icmagent.install_scripts',
                      #'icmagent.conf','icmagent.tools',
                      'umit.icm.agent',
                      'umit.icm.agent.core',
                      'umit.icm.agent.gui',
                      'umit.icm.agent.rpc',
                      'umit.icm.agent.secure',           
                      'umit.icm.agent.super', 
                      'umit.icm.agent.utils',                                 
                     ],
        #package_dir  = {'umit' : os.path.join(ROOT_DIR, 'umit')},
)


