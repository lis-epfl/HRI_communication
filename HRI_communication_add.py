#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 19:10:31 2018

@author: matteomacchini
"""


#####################################################


import datetime
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.multioutput import MultiOutputRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVR

import os


#####################################################


class HRI_communication_param():
    
    ######################################
    # should come from mapping structure #
    ######################################
    
    normalization_values = None
    
    
#####################################################
    
    
class HRI_communication_user():
    
    ######################################
    # should come from mapping structure #
    ######################################
    
    settings = {'train' : {'subject' : ['pilot3_'],
                          'maneuvre' : ['pitch_straight'],
                          'instance' : ['inst_1', 'inst_2']
                         },
                'test' : {'subject' : ['pilot3_'],
                         'maneuvre' : ['pitch_straight'],
                         'instance' : ['inst_3']
                         }
                 }
    
    
#####################################################
    

class HRI_communication_settings():
    
    ######################################
    # should come from mapping structure #
    ######################################
    
    used_body_parts = [3, 6, 7, 8, 9, 10, 11, 12, 13]
    variance_perc = 70
    init_values_to_remove = 300   
    debug = False    
    regress_each = False
    test_regressors = True
    force_clean_online = False
    pll_mode = 'av delay'    
    pll_av_delay = 100
    
    # options : 'full', 'angles', 'euler', 'quaternions'
    features_used = 'angles'
    # options : 'full', 'reduced', 'search'
    regressors = 'reduced'
    # options : 'roll', 'pitch', both (list)
    outputs = ['roll', 'pitch']
    # options : 'roll', 'pitch'
    main_output = 'pitch'
    
    output_pll = main_output
    is_final_mapping = True
    plot_reg_score = True
    
    data_folder = '/Users/matteomacchini/Google Drive/Matteo/EPFL/LIS/PhD/Natural_Mapping/DATA/acquired_data/'
    home_folder = os.path.dirname(os.path.realpath(__file__))
    
    
    interface_folder = os.path.join(data_folder, 'interfaces/') 
    
    ####################################################
    # should come from communication structure (so ok) #
    ####################################################
    
    
    EXAMPLE_DATA = True
    USE_DF_METHOD = True
    
    n_rigid_bodies_in_skeleton = 21
    n_data_per_rigid_body = 8
    
    timeout = 0.001 #1ms to read everything
    
    
    # options : 'avatar', 'acquisition', 'control'
    mode = 'control'
    
    filename = datetime.datetime.now().strftime("%Y_%b_%d_%I_%M_%S%p")
    foldername = '/Users/matteomacchini/Google Drive/Matteo/EPFL/LIS/PhD/Natural_Mapping/DATA/acquired_data/'
    
    
    n_readings = 100
    
    
    motive_indices = np.array([])
    
    motive_indices_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w'])
    
    regression_indices = np.array([])
    
    regression_indices_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w', 'roll', 'pitch', 'yaw'])
    
    for i in range(n_rigid_bodies_in_skeleton):
    
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
    
#####################################################
    
    
class HRI_communication_sockets():
    
    # MOTIVE
    
    motive = {'IP' : "127.0.0.1", 'PORT' : 9000}  # Local MOTIVE client, arbitrary non-privileged port
    
    #UNITY
    
    unity = {'IP' : "127.0.0.1", 'PORT' : 30011}  # Local UNITY client, arbitrary non-privileged port
    unity_calib = {'IP' : "127.0.0.1", 'PORT' : 30012}  # Local UNITY client, arbitrary non-privileged port
    unity_info = {'IP' : "127.0.0.1", 'PORT' : 30013}  # Local UNITY client, arbitrary non-privileged port
    unity_write_sk = {'IP' : "127.0.0.1", 'PORT' : 30000}  # Local UNITY client, arbitrary non-privileged port
    unity_write_sk_client = {'IP' : "127.0.0.1", 'PORT' : 26000}  # Local UNITY client, arbitrary non-privileged port
    
    # OPEN
    
    read_unity_query = None
    write_unity_sk = None
    read_unity_control = None
    read_unity_info = None
    read_motive_sk = None
    
#####################################################