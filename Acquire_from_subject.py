# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 14:16:07 2018

@author: macchini
"""

import os

import HRI_communication as hri

I_AM_IN_DRONEDOME = False
I_AM_ON_WINDOWS = True

#########################
    

# close eventual previous instance sockets

if 'comm' in locals():
    comm.close_sockets()
    
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


#########################


# close previous sockets
comm.close_sockets()


# initialize new sockets
comm.setup_sockets()


#comm.settings.n_readings = 30

# run acquisition
comm.subject = 'pilot_x1'
comm.instance = 3

comm.run('acquisition')


# pilot_x1 - matteo, new calibration method