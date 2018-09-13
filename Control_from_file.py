# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 12:30:10 2018

@author: macchini
"""



import os

import HRI_communication as hri


#########################
    

# close eventual previous instance sockets

if 'comm' in locals():
    comm.close_sockets()
    
comm = hri.HRI_communication()


#########################


# close previous sockets
comm.close_sockets()


# initialize new sockets
comm.setup_sockets()


# DroneDome folder
comm.settings.data_folder = 'D:\\LIS\\Matteo\\DATA\\acquired_data'
comm.settings.interface_folder = os.path.normpath(os.path.join(comm.settings.data_folder, '..', 'interfaces'))
comm._create_hri_folders()


# read dummy data
comm.settings.control_from_dummy_data = True

# run control

comm.run('control')