#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
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

from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.Errors import *
from umit.icm.agent.secure.Key import *

########################################################################
class KeyManager(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        ag_key_tup = g_db_helper.get_value('aggregator_public_key', None)
        if not ag_key_tup:
            raise InitializationError("Missing aggregator public key.")
        self.aggregator_public_key = RSAKey()
        self.aggregator_public_key.construct(*ag_key_tup)

        self.ciphered_public_keys = {}
        self.public_keys = {}
        self.private_keys = {}
        self.symmetric_keys = {}

    def add_key_pair(self, name, public_key, private_key):
        self.public_keys[name] = public_key
        self.private_keys[name] = private_key

    def remove_key_pair(self, name):
        del self.public_keys[name]
        del self.private_keys[name]

    def set_public_key(self, name, public_key):
        self.public_keys[name] = public_key

    def set_private_key(self, name, private_key):
        self.private_key[name] = private_key

    def get_public_key(self, name):
        if name in self.public_keys:
            return self.public_keys[name]
        else:
            g_logger.warn("Public key for '%s' not found." % name)
            return None

    def get_private_key(self, name):
        if name in self.private_key:
            return self.private_key[name]
        else:
            g_logger.warn("Private key for '%s' not found." % name)
            return None

