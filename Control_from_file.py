# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 12:30:10 2018

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


# read dummy data
#comm.settings.control_from_dummy_data = True
#comm.settings.simulate_query = True

# run control

comm.run('control')