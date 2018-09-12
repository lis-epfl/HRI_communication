# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 14:16:07 2018

@author: macchini
"""


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

# close previous sockets
comm.subject = 'pilot_1_1'
comm.run('acquisition')