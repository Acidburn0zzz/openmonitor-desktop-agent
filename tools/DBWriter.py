#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
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
import sys

# find root directory
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
while not os.path.exists(os.path.join(ROOT_DIR, 'umit')):
    new_dir = os.path.abspath(os.path.join(ROOT_DIR, os.path.pardir))
    if ROOT_DIR == new_dir:
        raise Exception("Can't find root dir.")
    ROOT_DIR = new_dir

execfile(os.path.join(ROOT_DIR, 'deps', 'umit-common', 'utils', 'importer.py'))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'icm-common'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'umit-common'))


#----------------------------------------------------------------------
from umit.icm.agent.Global import *
from umit.icm.agent.BasePaths import *
from umit.icm.agent.config import FileConfig, DBConfig

from umit.icm.agent.secure.Key import RSAKey
from umit.icm.agent.utils.CreateDB import create

try:
    g_config = DBConfig(DB_PATH)
except IOError:
    from umit.icm.agent.utils import CreateConf
    CreateConf.create_db_conf(DB_PATH)
    g_config = DBConfig(DB_PATH)


#ag_key = RSAKey()
#ag_key.construct()

mod = 93740173714873692520486809225128030132198461438147249362129501889664779512410440220785650833428588898698591424963196756217514115251721698086685512592960422731696162410024157767288910468830028582731342024445624992243984053669314926468760439060317134193339836267660799899385710848833751883032635625332235630111L
exp = 65537L

#print(ag_key.mod)
#print(ag_key.exp)
g_db_helper.set_value('keys','aggregator_public_key', (mod, exp))


