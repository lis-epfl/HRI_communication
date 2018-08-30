#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 15:43:19 2018

@author: matteomacchini
"""


#####################################################


#import matplotlib.pyplot as plt
#import numpy as np
#import os
#import pandas as pd
#from sklearn import metrics
#import time
#
#from hri_mapping_add import *
#import quaternion_operations as quat_op


#####################################################

class HRI_communication():
    
    
    ### DATA ###
    
used_body_parts = [3, 6, 7, 8, 9, 10, 11, 12, 13]


##################       SETTINGS       ##################

EXAMPLE_DATA = True
USE_DF_METHOD = True


mode = Mode_enum(3)

filename = date_t.now().strftime("%Y_%b_%d_%I_%M_%S%p")
foldername = 'acquired_data'


sett.N_READS = 100

sett.READ_MOTIVE_RB = 0
sett.READ_MOTIVE_SK = 0
sett.READ_XSENS = 0
sett.READ_FROM_UNITY = 0
sett.READ_QUERY_FROM_UNITY = 0

sett.WRITE_SK_TO_UNITY = 0

sett.OPEN_CLOSE_CONTINUOUS = 0

sett.DUMMY_READ = False

# MOTIVE

UDP_sett.IP_MOTIVE = "127.0.0.1"   # Local MOTIVE client
UDP_sett.PORT_MOTIVE = 9000    # Arbitrary non-privileged port

#UNITY

UDP_sett.IP_UNITY = "127.0.0.1"

UDP_sett.PORT_UNITY_QUERY = 30011

UDP_sett.PORT_UNITY_READ_CALIB = 30012
UDP_sett.PORT_UNITY_READ_CALIB_INFO = 30013


UDP_sett.PORT_UNITY_WRITE_SK = 30000

UDP_sett.PORT_UNITY_WRITE_SK_CLIENT = 26000


if mode.name=='avatar':

    sett.N_READS = 1000

    sett.READ_MOTIVE_SK = 1

    sett.READ_QUERY_FROM_UNITY = 1

    sett.WRITE_SK_TO_UNITY = 1

    sett.OPEN_CLOSE_CONTINUOUS = 1

    sett.DUMMY_READ = False


if mode.name=='acquisition':

    sett.N_READS = math.inf

    sett.READ_MOTIVE_SK = 1

    sett.READ_QUERY_FROM_UNITY = 1

    sett.WRITE_SK_TO_UNITY = 1

    sett.OPEN_CLOSE_CONTINUOUS = 1

    sett.DUMMY_READ = False


if mode.name=='control':

    sett.N_READS = math.inf

    sett.READ_MOTIVE_SK = 1

    sett.READ_QUERY_FROM_UNITY = 1

    sett.WRITE_SK_TO_UNITY = 1

    sett.OPEN_CLOSE_CONTINUOUS = 1

    sett.DUMMY_READ = False


SUBJECTS = {'MatteoM' : 'pilot1', 'StefanoM' : 'pilot2', 'DavideZ' : 'pilot3'}

subject = SUBJECTS['DavideZ']

###################       IMPORT DATA      ###################

regressor_filename = subject + '_best_mapping'
parameters_filename = subject + '_PARAM' + '.txt'


regressor_filename = subject + '_best_mapping'
parameters_filename = subject + '_PARAM' + '.txt'

if mode.name=='control':
    data_folder = settings.data_folder
    interface_folder = data_folder + 'interfaces/'
    # load interface to fileaaaa
    best_mapping = load_obj(interface_folder + regressor_filename)
    parameters = pd.read_csv(data_folder + parameters_filename)
    
    
##################      IMPLEMENTATION      ##################


start = date_t.now()


if sett.WRITE_SK_TO_UNITY:
    unity_sk_client = Socket_info()

    unity_sk_client.IP = UDP_sett.IP_UNITY
    unity_sk_client.PORT = UDP_sett.PORT_UNITY_WRITE_SK_CLIENT

count = 0

query = ''

# define data structure and headers

        
motive_indices = np.array([])

motive_indices_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w'])

regression_indices = np.array([])

regression_indices_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w', 'roll', 'pitch', 'yaw'])

for i in range(N_RB_IN_SKEL):

    n = np.char.array([('_' + str(i+1))])

    if i==0:
        motive_indices = motive_indices_base + (n)
        if i+1 in used_body_parts:
            regression_indices = regression_indices_base + (n)
    else:
        motive_indices = np.r_[motive_indices, motive_indices_base + (n)]
        if i+1 in used_body_parts:
            regression_indices = np.r_[regression_indices, regression_indices_base + (n)]


        
unity_indices_calib = np.char.array([ 'input1', 'input2', 'input3', 'input4', 'roll', 'pitch', 'yaw', 'roll_rate', 'pitch_rate', 'yaw_rate', 'vel_x', 'vel_y', 'vel_z', 'vel_semiloc_x', 'vel_semiloc_y', 'vel_semiloc_z', 'corr_roll', 'corr_pitch', 'pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z', 'rot_w', 'timestamp' ])
unity_indices_info = np.char.array([ 'calib_axis', 'calib_phase', 'is_input_not_zero', 'instance', 'loop counter' ])

motive_data = np.array(motive_indices)
unity_data_calib = np.array(unity_indices_calib)
unity_data_info = np.array(unity_indices_info)
unity_data = np.r_[unity_indices_calib, unity_indices_info]

calib_data = np.r_[motive_indices, unity_data]

data = calib_data
data = data.reshape(1, data.size)

data_num = np.array([])

skel_num = np.array([])

unity_num = np.array([])

if not EXAMPLE_DATA:
    skel = []

used_str = ['_' + str(x) for x in used_body_parts]
my_cols = [col for col in motive_indices if any(y in col for y in used_str)]

acquired_first_skel = False

input_data = 'angles'

outputs = ['roll', 'pitch']

# select features

if input_data == 'all':
    feats = [col for col in regression_indices if '_' in col]
elif input_data == 'angles':
    feats = [col for col in regression_indices if 'quat' in col or 'roll_' in col or 'pitch_' in col or 'yaw_' in col]
elif input_data == 'euler':
    feats = [col for col in regression_indices if 'roll_' in col or 'pitch_' in col or 'yaw_' in col]
elif input_data == 'quaternions':
    feats = [col for col in regression_indices if 'quat' in col]
    

#if not EXAMPLE_DATA:
# create unity read query / write skeleton socket
Read_unity_query = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_QUERY, 'UNITY_QUERY', timeout = 0.001)
Write_unity_sk = Read_unity_query

# create unity control read socket
Read_unity_control = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_READ_CALIB, 'UNITY_CALIB',  timeout = 0.001)

# create unity info read socket
Read_unity_info = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_READ_CALIB_INFO, 'UNITY_INFO',  timeout = 0.001)

# create motive read socket
Read_motive_sk = setup(UDP_sett.IP_MOTIVE, UDP_sett.PORT_MOTIVE, 'MOTIVE_SK',  timeout = 0.001) #1ms to read everything
        
if EXAMPLE_DATA:

    ###################        TEST        ###################
    
    test_data = pd.read_csv(data_folder + 'pilot3_inst_1_2018_Jun_22_06_53_03PM_roll_straight.txt')
    
    in_data = test_data.iloc[:,:231]
    
    out_data = test_data.iloc[:,231:]
    
    col_no_eul = [x for x in in_data if any(y in x for y in motive_indices_base)]
    
    in_data = in_data[col_no_eul]
    
    parameters = parameters.iloc[:,:-2]   
    parameters_val = parameters.values
    
    param_av = parameters_val[0,:].reshape(len(used_body_parts),-1)
    param_std = parameters_val[1,:].reshape(len(used_body_parts),-1)

    # limit loop duration
    
    sett.N_READS = 10 # len(test_data)
#    sett.N_READS = len(test_data)

    # don't wait for query
    unity_query = 'c'
    
    y_score_all = []
    
#    plt.ion()
#    fig = plt.figure()
#    ax1 = fig.add_subplot(211)
#    ax2 = fig.add_subplot(212)
             
    regress_data_list = []
    
    df_first = []
    first_skel = []