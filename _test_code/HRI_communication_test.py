#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 18:05:40 2018

@author: matteomacchini
"""

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
if parentdir not in sys.path:
    sys.path.insert(0,parentdir) 

import matplotlib.pyplot as plt

import HRI_communication as hri


#########################


def test_class(comm):
    
#    mapp = comm.import_mapping()
    
    comm.close_sockets()
    comm.setup_sockets()
    comm.settings.simulate_query = True
#    comm.settings.n_readings = 100
    comm.run('control')
    
    return comm


#########################
    

# close eventual previous instance sockets

if 'comm' in locals():
    comm.close_sockets()
    
comm = hri.HRI_communication()


comm.settings.control_preproc_pandas = False
comm = test_class(comm)
comm.close_sockets()
res_np = comm._debug_control

###################
### CHECK INPUT ###
###################

real_input_unprocessed = comm.mapp.motion_data_unprocessed['test']
real_input = comm.mapp.motion_data['test']

############
### PLOT ###
############

comm.mapp._plot_score(res = comm.res_all)


real_input = comm.mapp.motion_data['train']
