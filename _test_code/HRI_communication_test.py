#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 18:05:40 2018

@author: matteomacchini
"""

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import HRI_communication as hri

# close eventual previous instance sockets

if 'comm' in locals():
    comm.close_sockets()

comm = hri.HRI_communication()

mapp = comm.import_mapping()


comm.close_sockets()

comm.setup_sockets()

comm.settings.mode = 'avatar'

comm.run('acquisition')