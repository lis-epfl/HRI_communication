# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 14:16:07 2018

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
comm.settings.data_folder = 'D:\\LIS\\Matteo\\DATA\\Acquired_data'
comm.settings.interface_folder = os.path.join(comm.settings.data_folder, 'interfaces/')


#comm.settings.n_readings = 30

# run acquisition
comm.subject = 'pilot_x1'
comm.instance = 3

comm.run('acquisition')


# pilot_x1 - matteo, new calibration method