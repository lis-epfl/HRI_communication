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

I_AM_IN_DRONEDOME = False
I_AM_ON_WINDOWS = True


#########################


def test_class(comm):
    
#    mapp = comm.import_mapping()
    
    comm.close_sockets()
    comm.setup_sockets()
    comm.settings.simulate_query = True
#    comm.settings.n_readings = 100
    comm.settings.control_from_dummy_data = True
    comm.run('control')
    
    return comm


#########################
    

# close eventual previous instance sockets

if 'comm' in locals():
    comm.close_sockets()
    
####################
### CREATE CLASS ###
####################
    
comm = hri.HRI_communication()

# working folder depends on pc
if I_AM_ON_WINDOWS:
    # Windows folder
    comm.settings.data_folder = 'G:\\My Drive\\Matteo\\EPFL\\LIS\\PhD\\Natural_Mapping\\DATA\\acquired_data'
    comm.settings.interface_folder = os.path.normpath(os.path.join(comm.settings.data_folder, '..', 'interfaces'))
    comm._create_hri_folders()
if I_AM_IN_DRONEDOME:
    # DroneDome folder
    comm.settings.data_folder = 'D:\\LIS\\Matteo\\DATA\\acquired_data'
    comm.settings.interface_folder = os.path.normpath(os.path.join(comm.settings.data_folder, '..', 'interfaces'))
    comm._create_hri_folders()

###################
### CHOOSE USER ###
###################

comm.user.settings = {'train' : {'subject' : ['pilot_x2'],
                            'maneuvre' : ['straight'],
                            'instance' : ['inst_1', 'inst_2']
                            },
                 'test' :  {'subject' : ['pilot_x2'],
                            'maneuvre' : [''],
                            'instance' : ['inst_3']
                            }
                 }

##################
### TEST CLASS ###
##################

comm.settings.control_preproc_pandas = False
comm = test_class(comm)
comm.close_sockets()

###################
### CHECK INPUT ###
###################

res_np = comm._debug_control

real_input_unprocessed = comm.mapp.motion_data_unprocessed['test']
real_input = comm.mapp.motion_data['test']

############
### PLOT ###
############

comm.mapp._plot_score(res = comm.res_all)


real_input = comm.mapp.motion_data['train']
