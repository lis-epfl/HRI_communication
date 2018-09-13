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
    
    def __init__(self):
    
        ######################################
        # should come from mapping structure #
        ######################################
        
        self.normalization_values = None
    
    
#####################################################
    
    
class HRI_communication_user():
    
    def __init__(self):
    
        ######################################
        # should come from mapping structure #
        ######################################
        
        
        self.settings = {'train' : {'subject' : ['pilot3_'],
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
    
    def __init__(self):
    
        ######################################
        # should come from mapping structure #
        ######################################
        
        self.used_body_parts = [3, 6, 7, 8, 9, 10, 11, 12, 13]
        self.variance_perc = 70
        self.init_values_to_remove = 300   
        self.debug = False    
        self.regress_each = False
        self.test_regressors = True
        self.force_clean_online = False
        self.pll_mode = 'av delay'    
        self.pll_av_delay = 100
        
        # options : 'full', 'angles', 'euler', 'quaternions'
        self.features_used = 'angles'
        # options : 'full', 'reduced', 'search'
        self.regressors = 'reduced'
        # options : 'roll', 'pitch', both (list)
        self.outputs = ['roll', 'pitch']
        # options : 'roll', 'pitch'
        self.main_output = 'pitch'
        
        self.output_pll = self.main_output
        self.is_final_mapping = True
        self.plot_reg_score = True
        
        self.data_folder = '/Users/matteomacchini/Google Drive/Matteo/EPFL/LIS/PhD/Natural_Mapping/DATA/acquired_data/'
        self.home_folder = os.path.dirname(os.path.realpath(__file__))
        
        
        self.interface_folder = os.path.join(self.data_folder, 'interfaces') 
        
        ####################################################
        # should come from communication structure (so ok) #
        ####################################################
        
        
        self.dummy_read = False
        self.example_data = True
        self.control_preproc_pandas = False
        
        self.control_from_dummy_data = False
        
        self.n_rigid_bodies_in_skeleton = 21
        self.n_data_per_rigid_body = 8
        
        self.timeout = 0.001 #1ms to read everything
        
        
        # options : 'avatar', 'acquisition', 'control'
        self.mode = 'control'
        
        self.filename = datetime.datetime.now().strftime("%Y_%b_%d_%I_%M_%S%p")
        self.interface_folder = os.path.normpath(os.path.join(self.data_folder, '..', 'interfaces'))
        
        
        self.n_readings = None
        self.simulate_query = False
    
#####################################################
    
    
class HRI_communication_sockets():
    
    def __init__(self):
    
        # MOTIVE
        
        self.motive = {'IP' : "127.0.0.1", 'PORT' : 9000}  # Local MOTIVE client, arbitrary non-privileged port
        
        #UNITY
        
        self.unity = {'IP' : "127.0.0.1", 'PORT' : 30011}  # Local UNITY client, arbitrary non-privileged port
        self.unity_calib = {'IP' : "127.0.0.1", 'PORT' : 30012}  # Local UNITY client, arbitrary non-privileged port
        self.unity_info = {'IP' : "127.0.0.1", 'PORT' : 30013}  # Local UNITY client, arbitrary non-privileged port
        self.unity_write_sk = {'IP' : "127.0.0.1", 'PORT' : 30000}  # Local UNITY client, arbitrary non-privileged port
        self.unity_write_sk_client = {'IP' : "127.0.0.1", 'PORT' : 26000}  # Local UNITY client, arbitrary non-privileged port
        
        self.unity_sk_client = {'IP' : "127.0.0.1", 'PORT' : 26000}  # Local UNITY client, arbitrary non-privileged port
        
        # OPEN
        
        self.read_unity_query = None
        self.write_unity_sk = None
        self.read_unity_control = None
        self.read_unity_info = None
        self.read_motive_sk = None
    
#####################################################