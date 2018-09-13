#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 15:43:19 2018

@author: matteomacchini
"""


#####################################################



#import matplotlib.pyplot as plt
#import os
#import pandas as pd
#from sklearn import metrics
#import time
import numpy as np
import pandas as pd
import socket as soc
from socket import timeout
import struct
import sys
import datetime
#
from HRI_communication_add import *
#import quaternion_operations as quat_op

    
        
import os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

if os.path.normpath(os.path.join(parentdir, 'HRI_mapping/')) not in sys.path:
    sys.path.insert(0, os.path.normpath(os.path.join(parentdir, 'HRI_mapping/')))

import HRI
import HRI_mapping
import motive_skeleton



# NEEDS TO BE SOLVED
class Socket_struct:
    pass


#####################################################

class HRI_communication():
    
    
    ### CLASS FUNCTIONS ###
    
    def __init__(self):
            
        self.param = HRI_communication_param()
        self.settings = HRI_communication_settings()
        self.user = HRI_communication_user()
        self.sockets = HRI_communication_sockets()
        
    
    
    
        self.motive_header = np.array([])
        
        self.motive_header_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w'])
        
        self.regression_header = np.array([])
        
        self.regression_header_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w', 'roll', 'pitch', 'yaw'])
        
        for i in range(self.settings.n_rigid_bodies_in_skeleton):
        
            n = np.char.array([('_' + str(i+1))])
        
            if i==0:
                self.motive_header = self.motive_header_base + (n)
                if i+1 in self.settings.used_body_parts:
                    self.regression_header = self.regression_header_base + (n)
            else:
                self.motive_header = np.r_[self.motive_header, self.motive_header_base + (n)]
                if i+1 in self.settings.used_body_parts:
                    self.regression_header = np.r_[self.regression_header, self.regression_header_base + (n)]
        
        
        self.unity_header_calib = np.char.array([ 'input1', 'input2', 'input3', 'input4', 'roll', 'pitch', 'yaw', 'roll_rate', 'pitch_rate', 'yaw_rate', 'vel_x', 'vel_y', 'vel_z', 'vel_semiloc_x', 'vel_semiloc_y', 'vel_semiloc_z', 'corr_roll', 'corr_pitch', 'pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z', 'rot_w', 'timestamp' ])
        self.unity_header_info = np.char.array([ 'calib_type', 'calib_info_1', 'calib_info_2', 'is_input_not_zero', 'instance', 'loop counter' ])
        
        # calib_info_1 : axis or roll
        # calib_info_2 : phase or pitch
        
        self.motive_header = np.array(self.motive_header)
        self.unity_header_calib = np.array(self.unity_header_calib)
        self.unity_header_info = np.array(self.unity_header_info)
        self.unity_header = np.r_[self.unity_header_calib, self.unity_header_info]
        
        self.calib_header = np.r_[self.motive_header, self.unity_header]
        
        self.data = self.calib_header
        self.data = self.data.reshape(1, self.data.size)
    
    
    
        self.SUBJECTS = {'MatteoM' : 'pilot1', 
                    'StefanoM' : 'pilot2', 
                    'DavideZ' : 'pilot3'}
        
        self.subject = ''
        
        
        self.count = 0
        
        self.query = ''
        
        # define data structure and headers
        
        self.data_num = np.array([])
        
        self.skel_num = np.array([])
        
        self.unity_num = np.array([])
        
        self.skel = []
        
        self.regress_data_list = []
        
        self.acquired_first_skel = False
        
        self.feats = None
        self.rms_list = None
        
        self._debug_control = []
        self._debug_control_on = False
        
        self.y_true_all = np.empty((1000000, 2))

        self.y_score_all = np.empty((1000000, 2))
        
        
        
        self.calib_type_dict = {1 : 'sin',
                      2 : 'cos_NEW'}
        
        self.calib_info_1_dict = {1 : {0 : 'roll', 
                                       1 : 'pitch'},
                                  2 : {0 : 'straight', 
                                       1 : 'right', 
                                       2 : 'left'}}
        
        self.calib_info_2_dict = {1 : {0 : {0 : 'straight', 
                                            1 : 'up', 
                                            2 : 'down'},
                                       1 : {0 : 'straight', 
                                            1 : 'right', 
                                            2 : 'left'}},
                                  2 : {0 : {0 : 'straight', 
                                            1 : 'up', 
                                            2 : 'down'},
                                       1 : {0 : 'straight', 
                                            1 : 'up', 
                                            2 : 'down'},
                                       2 : {0 : 'straight', 
                                            1 : 'up', 
                                            2 : 'down'}}}
        
    
    ### PRIVATE FUNCTIONS ###
    

    def _setup_sockets(self, IP, PORT, ID, timeout = 0.001):
        # Datagram (udp) socket
        try:
            socket = soc.socket(soc.AF_INET, soc.SOCK_DGRAM)
            print('socket ', ID, ' created')
        except socket.error as msg:
            print('Failed to create socket. Error : ', msg)
            sys.exit()
        # Bind socket to local IP and port
        try:
            socket.bind((IP, PORT))
        except soc.error as msg:
            print('Bind failed. Error Code : ', msg)
            sys.exit()
        print('socket ', ID, ' bind complete')
    
        # set timeout
        socket.settimeout(timeout)
    
        read_s = Socket_struct() # Create an empty socket structure
    
        read_s.socket = socket
        read_s.ID = ID
    
        return read_s
        
        
    #########################


    def _udp_read(self, Read_struct):
        # print('\nREADING FROM', Read_struct.type, '\n')
        # receive data from client (data, addr)
    
        try:
            data, addr = Read_struct.socket.recvfrom(4096)
        except timeout:
            
            if self.settings.dummy_read:
                if Read_struct.ID == 'MOTIVE_SK':
                    data = []
                    one_rb = b'\x01\x00\x04\x00\xd0hG?\xe7sp?.\xbf\x93\xc0\\f\xbf=$\xd9j?]\xa9\x94=~\x92\xc2>'
                    for i in range(self.settings.n_rigid_bodies_in_skeleton):
                        data = data + one_rb if len(data) else one_rb
                else:
                    return 't'
            else:
                return 't'
            
        return data
        
        
    #########################
        
        
    def _udp_write(self, msg):
        self.sockets.write_unity_sk.socket.sendto(msg, (self.sockets.unity_write_sk_client['IP'], self.sockets.unity_write_sk_client['PORT']))
        
        
    #########################
    

    def _udp_process(self, data, Read_struct):
    
        if data == 't':
            return 't'
        
        if Read_struct.ID == 'MOTIVE_RB':
    
            if not data:
                return None
    
            # print("Byte Length of Message :", len(data), "\n")
            strs = ""
    
            # THIS IS A int_32
    
            for i in range(0, 1):
                strs += "i"
    
            # THIS IS A float
    
            for i in range(1, len(data) // 4):
                strs += "f"
    
            # print(strs)
    
            # print("Message Data (skeletal bone):", struct.unpack(strs, data), "\n")
    
            data_ump = struct.unpack(strs, data)
    
            bone_s = Bone_struct()
        #         print(int(bin(data[0])[-8:], 2))
            bone_s.ID = int(bin(data_ump[0])[-8:], 2)
            bone_s.position = data_ump[1:4]
            quaternion_t = data_ump[4:]
            order = [3, 0, 1, 2]
    
            bone_s.quaternion = [quaternion_t[i] for i in order]
    
            # print(bone_s.quaternion)
            bone_s.euler = sp.Q2EA(np.array(bone_s.quaternion), EulerOrder="zyx", ignoreAllChk=True)[0]
    
        elif Read_struct.ID == 'MOTIVE_SK':
    
            if not data:
                return None
    
            strs = ""
    
            # one int and 7 floats, '21' times
    
            for i in range(0, len(data) // 4):
                if i % 8 == 0:
                    strs += "i"
                else:
                    strs += "f"
    
            data_ump = struct.unpack(strs, data)
    
            Q_ORDER = [3, 0, 1, 2]
            
            self.data_ump = data_ump
    
            for i in range(0, len(data_ump) // self.settings.n_data_per_rigid_body):
                bone = list(data_ump[i*self.settings.n_data_per_rigid_body : (1+i)*self.settings.n_data_per_rigid_body])
                
                self.bone = bone
                self.i = i
                
                # print bone
    
                if i == 0:
                    ID = [(int(bin(bone[0])[-8:], 2))]
                    position = np.array(bone[1:4])
                    quaternion_t = np.array(bone[4:])
                    quaternion = np.array([quaternion_t[j] for j in Q_ORDER])
                else:
                    ID = ID + [(int(bin(bone[0])[-8:], 2))]
                    position = np.vstack((position, bone[1:4]))
                    quaternion_t = bone[4:]
                    quaternion = np.vstack((quaternion, [quaternion_t[j] for j in Q_ORDER]))
                
            ID = np.array(ID)
            
            self._debug_udp_process = [ID, position, quaternion]
            
            data = np.c_[ID, position, quaternion]
            
            # sort by ID
            data = data[data[:, 0].argsort()]
    
            return data
    
        elif Read_struct.ID == 'UNITY_CALIB':
    
            if not data:
                return None
    
    #         print("Byte Length of Message :", len(data), "\n")
            strs = ""
            for i in range(0, len(data)//4):
                strs += "f"
    
            # print(strs)
            # print(len(data))
    
            unity_control = struct.unpack(strs, data)
            # print("Message Data :", unity_control, "\n")
            return unity_control
    
        elif Read_struct.ID == 'UNITY_INFO':
    
            if not data:
                return None
    
    #         print("Byte Length of Message :", len(data), "\n")
            strs = ""
            for i in range(0, len(data)//4):
                strs += "i"
    
            # print(strs)
            # print(len(data))
    
            unity_info = struct.unpack(strs, data)
            # print("Message Data :", unity_control, "\n")
            return unity_info
    
        elif Read_struct.ID == 'UNITY_QUERY':
    
            if not data:
                return None
    
            # we receive a char
    
            unity_query = data.decode("utf-8") 
    #         print("Message Data :", unity_query, "\n")
            return unity_query
        
        
    #########################
    
    
    def _consume_motive_skeleton(self):
        # consume skeleton
        skel_data_temp = self._udp_read(self.sockets.read_motive_sk)
            
        return skel_data_temp
        
        
    #########################
    

    def _get_unity_query(self):
        
        # read query
        query_data = self._udp_read(self.sockets.read_unity_query)
        unity_query = self._udp_process(query_data, self.sockets.read_unity_query)
             
        print ('UNITY query = ', unity_query)
        
        return unity_query
        
        
    #########################
    
    
    def _run_avatar(self):
        
        count = 0
            
        while count<self.settings.n_readings:
            
            count += 1
            
            # create motive read socket
            # update skeleton
            # close motive read socket
            (skel) = self._consume_motive_skeleton()

            query = ''

            # check if unity query
            unity_query = self._get_unity_query()

            # close unity read socket
            # Write_unity_sk.socket.close()

            # if query : send skeleton
            if unity_query=='r':

                print('sending skeleton to UNITY')

                # send skeleton
                write_sk_to_unity(Write_unity_sk, unity_sk_client, skel)

            elif unity_query=='q':

                # close unity write socket
                Read_unity_query.socket.close()
                
                break
        
        
    #########################
    
    
    def _run_acquisition(self):
        
        count = 0
            
        while count<self.settings.n_readings:
            
            count += 1
        
            skel_data_temp = self._consume_motive_skeleton()
            
            if skel_data_temp == 't':
                print ('skel = ', skel_data_temp)
            else:
                print ('skel = full skeleton')
                self._skel_data = skel_data_temp
        
            unity_query = self._get_unity_query()
            
            if self.settings.simulate_query:
                unity_query = 'a'
        
            # if query : read unity and skeleton, then save to csv
            if unity_query=='a':
            
                self._acquisition_routine()
            
            elif unity_query=='q':
            
                # store to file
                
                self._store_subject_to_file()
        
                self.close_sockets()
                
                break
            
        
    #########################
    
    
    def _acquisition_routine(self):
            
        print('collecting data')
    
        # read unity calibration data
        udp_data = self._udp_read(self.sockets.read_unity_control)
        unity_calib = np.array(self._udp_process(udp_data, self.sockets.read_unity_control))
                        
        print('unity_calib = ', unity_calib)
        
        # read unity info
        udp_data = self._udp_read(self.sockets.read_unity_info)
        unity_calib_info = np.array(self._udp_process(udp_data, self.sockets.read_unity_info))
                        
        print('unity_calib_info = ', unity_calib_info)
            
        # save skel_data in list
        if len(self.skel) == 0:
            self.skel = [self._skel_data]
        else:
            self.skel.append(self._skel_data)
                             
        # reshape all to 1D array    
        unity_calib = unity_calib.reshape(1, unity_calib.size)
        unity_calib_info = unity_calib_info.reshape(1, unity_calib_info.size)
        
        unity_row = np.c_[unity_calib, unity_calib_info]
        
        if self.unity_num.size:
            if unity_row.shape[1] == self.unity_header.size:
                self.unity_num = np.vstack([self.unity_num, unity_row])
            else:
                print('lost frame')
        else:
            self.unity_num =  unity_row
            
        
    #########################
        
    
    def _run_control(self):
        
        if self.settings.example_data:
            self.y_true_all = np.empty((len(self.dummy_data), 2))
            self.y_score_all = np.empty((len(self.dummy_data), 2))
            if self.settings.n_readings == np.inf:
                self.settings.n_readings = len(self.dummy_data-1)
            
        count = 0
            
        while count<self.settings.n_readings:
        
            if self.settings.example_data:
                
                # import dummy data
                a = 0
                
            else:
            
                skel_data_temp = self._consume_motive_skeleton()
                
                if skel_data_temp == 't':
                    print ('skel = ', skel_data_temp)
                else:
                    print ('skel = full skeleton')
                    skel_data = skel_data_temp
            
            unity_query = self._get_unity_query()
            
            if self.settings.simulate_query:
                unity_query = 'c'
                
            # if query : read unity and skeleton, then save to csv
            if unity_query=='c':
                
                self._control_routine(count)
            
                count += 1
                
            elif unity_query=='q':
                
                self.close_sockets()
                    
                break
            
                
    #########################
    
    
    def _control_routine(self, count = 0):
        
        # if query : read unity and skeleton, then save to csv
        
    #    start = time.clock()
            
        # process skel data and add headers
        
        if  self.settings.example_data:
            skel_num = self.dummy_data[count:count+1]
        else:
            skel = skel_data
            skel = self._udp_process(skel)
            
        if self.settings.control_preproc_pandas:
            
            print('processing (pandas method)')
        
            mapp = HRI_mapping.HRI_mapping()
            
            # create df
            df = pd.DataFrame(skel_num, columns = self.regression_header)   
            
            # first skel
            if not self.acquired_first_skel:
                
                # create df
                self.first_skel = pd.DataFrame(skel_num, columns = self.regression_header) 
                
                # remove unused columns
                self.first_skel = self.first_skel[self.regression_header]
                
                # compute relative angles
                self.first_skel = mapp._relativize_df(self.first_skel)
                
                self.acquired_first_skel = True
            
            if self._debug_control_on:
                skel_first = self.first_skel[self.feats]
            
            # remove unused columns
            df = df[self.regression_header]
                
            if self._debug_control_on:
                skel_base = df[self.feats]
            
            # compute relative angles
            df = mapp._relativize_df(df)
                
            if self._debug_control_on:
                skel_rel = df[self.feats]
            
            # concatenate first and current skel
            df_combined = pd.concat([self.first_skel,df])
            
            # unbias angles
            df_combined = mapp._remove_bias_df(df_combined)
            df = df_combined[1:2]
                
            if self._debug_control_on:
                skel_unb = df[self.feats]
            
            # compute euler angles
            df = mapp._compute_ea_df(df)
            
            # save input data
            self.regress_data_list.append(df)
            
            
            if self._debug_control_on:
                skel_eul = df[self.feats]
            
            # normalize
            for j in list(df):
                # do not normalize quaternion components and outputs
                if 'pos' in j or 'pitch_' in j or 'roll_' in j or 'yaw_' in j :
                    [array_norm, norm_param_t] = mapp._normalize(df[j], self.param.normalization_values[j])
                    df[j] = array_norm
                    
                
            # regression
            skel_fake = df[self.feats]
            
            y_score = self.best_mapping.predict(skel_fake)
            
            
            if self._debug_control_on:
                self._debug_control.append({'skel_num' : skel_num,
                                        'skel_base' : skel_base,
                                        'skel_first' : skel_first,
                                        'skel_rel' : skel_rel,
                                        'skel_unb' : skel_unb,
                                        'skel_eul' : skel_eul,
                                        'skel' : skel_fake,
                                        'score' : y_score})
            
            if self.rms_list == None:
                self.rms_list = []
                
            self.rms_list = self.rms_list.append(y_score.T)
            
        else:
            
#            print('processing (numpy method)')
            
            skel = motive_skeleton.skeleton(np.reshape(skel_num[self.motive_header].values, (self.settings.n_rigid_bodies_in_skeleton,-1)))
            
            skel_base = skel.values
            
            ### USING MOTIVE_SKELETON CLASS ###
            
            # used body parts
            skel.keep_used_body_parts()
        
            skel_bodyparts = np.copy(skel.values)
        
            # compute relative angles
            skel.relativize_skeleton()
        
            skel_rel= np.copy(skel.values)
        
            
            # first skel
            if not self.acquired_first_skel:
                
                self.first_skel = motive_skeleton.skeleton(np.copy(skel.values))
        
                self.acquired_first_skel = True
        
            skel_first = np.copy(self.first_skel.values)
                
                
            # unbias angles
            skel.unbias_skeleton(self.first_skel)
        
            skel_unb = np.copy(skel.values)
            
            # compute euler angles
            skel.compute_ea()
        
            # save input data
            self.regress_data_list.append(skel)
            
            skel_eul = np.copy(skel.values)
        
            # normalize
            skel.normalize(self.param.norm_av, self.param.norm_std)
            
            skel_norm = np.copy(skel.values)
            
            # regression
            skel.keep_features(self.settings.features_used)
            
            skel_reg = np.copy(skel.values.reshape(1, -1))
            
            y_score = self.best_mapping.predict(skel_reg)
            
            
            
            self._debug_control.append({'skel_num' : skel_num,
                                        'skel_bodyparts' : skel_bodyparts,
                                        'skel_base' : skel_base,
                                        'skel_first' : skel_first,
                                        'skel_rel' : skel_rel,
                                        'skel_unb' : skel_unb,
                                        'skel_eul' : skel_eul,
                                        'skel_norm' : skel_norm ,
                                        'skel' : skel_reg,
                                        'score' : y_score})
    
            
    
            if self.rms_list == None:
                self.rms_list = []
                
            self.rms_list = self.rms_list.append(y_score.T)
                
                
        print('')
        print(count)
        print('')
        
        #            
        
        y_true = self.dummy_data[self.settings.outputs][count:count+1].values
        
        self.y_true_all[count] = y_true
        self.y_score_all[count] = y_score
        
        self.res_all = {"reg":self.best_mapping,
                    "reg_type":str(self.best_mapping),
                    "y_true":self.y_true_all,
                    "y_score":self.y_score_all
                    }
        
        # send commands to 
        
        Y_score_scaled = y_score/90.0
        
        controls = Y_score_scaled.tolist()[0] + [0, 0, 0]
        
        self._write_commands_to_unity(controls)
        
        
    #########################
    
    
    def _import_dummy(self):
        
        self.import_mapping()
        
        self.mapp.import_data(which_user = 'test', clean = False)
        self.dummy_data = HRI.merge_data_df(self.mapp.motion_data_unprocessed['test'])[self.mapp.settings.init_values_to_remove:]
        self.param.normalization_values = self.mapp.param.normalization_values
        
        self.param.normalization_values = self.param.normalization_values.iloc[:,:-2]
        self.param.normalization_values = self.param.normalization_values[self.regression_header]
        
        parameters_val = self.param.normalization_values.values
        
        self.param.norm_av = parameters_val[0,:].reshape(len(self.settings.used_body_parts),-1)
        self.param.norm_std = parameters_val[1,:].reshape(len(self.settings.used_body_parts),-1)
    
        self.best_mapping = self.mapp.test_results[self.mapp.best_idx]['reg']
        
        
    #########################
    
    
    def _store_subject_to_file(self):
        
        # process motive skeleton data
        self.skel_num = self._udp_process(self.skel[0],self.sockets.read_motive_sk)  
        self.skel_num.resize(1, self.skel_num.size)
        
        for i in range(1, len(self.skel)):
            skel_np_t = self._udp_process(self.skel[i], self.sockets.read_motive_sk)    
            skel_np_t.resize(1, skel_np_t.size)
            self.skel_num = np.vstack([self.skel_num, skel_np_t])
        
            
        calib_data = np.c_[self.skel_num, self.unity_num]
        self.acquired_data = np.vstack([self.data, calib_data])
        
        calib_type = int(calib_data[-1, -6])
        calib_info_1 = int(calib_data[-1, -5])
        calib_info_2 = int(calib_data[-1, -4])
        
        end_of_filename = self.calib_type_dict[calib_type] + '_' + self.calib_info_1_dict[calib_type][calib_info_1] + '_' + self.calib_info_2_dict[calib_type][calib_info_1][calib_info_2]
        
        # create folders in case they don't exist
        self._create_hri_folders()
        
        # save data to txt file
        if calib_data.shape[0]>1 and calib_data.shape[1]>3:
            filename = self.subject + '_' + end_of_filename + '_' + datetime.datetime.now().strftime("%Y_%b_%d_%I_%M_%S%p")
        elif self.data.shape[0]==1:
            print('no data acquired')
        else:
            print('problem with data size')
            
        np.savetxt(os.path.join(self.settings.data_folder, filename + '.txt'), (self.acquired_data), delimiter=",", fmt="%s")
        
    
    #########################
        
    
    def _create_hri_folders(self):
    
        HRI.create_dir_safe(self.settings.data_folder)
        HRI.create_dir_safe(self.settings.interface_folder)
    
    
    #########################
    
    
    ### PUBLIC  FUNCTIONS ###
    
    
    #########################
    
    
    def select_features(self):
        
        in_data = self.settings.features_used
                
        if in_data == 'full':
            feats = [col for col in list(self.regression_header) if '_' in col]
        elif in_data == 'angles':
            feats = [col for col in list(self.regression_header) if 'quat' in col or 'roll_' in col or 'pitch_' in col or 'yaw_' in col]
        elif in_data == 'euler':
            feats = [col for col in list(self.regression_header) if 'roll_' in col or 'pitch_' in col or 'yaw_' in col]
        elif in_data == 'quaternions':
            feats = [col for col in list(self.regression_header) if 'quat' in col]
    
        self.feats = feats
    
    
    #########################
    
    
    def import_mapping(self):
        
        self.mapp = HRI_mapping.HRI_mapping()
        
        # point to the same interface folder
        self.mapp.settings.interface_folder = self.settings.interface_folder
        
        self.mapp = HRI_mapping.load_last_for_this_subject(self.mapp)
        
        
    #########################
    
    
    def setup_sockets(self):
    
        # create unity read query / write skeleton socket
        self.sockets.read_unity_query = self._setup_sockets(self.sockets.unity['IP'], self.sockets.unity['PORT'], 'UNITY_QUERY', timeout = self.settings.timeout)
        self.sockets.write_unity_sk = self.sockets.read_unity_query
        
        # create unity control read socket
        self.sockets.read_unity_control = self._setup_sockets(self.sockets.unity_calib['IP'], self.sockets.unity_calib['PORT'], 'UNITY_CALIB',  timeout = self.settings.timeout)
        
        # create unity info read socket
        self.sockets.read_unity_info = self._setup_sockets(self.sockets.unity_info['IP'], self.sockets.unity_info['PORT'], 'UNITY_INFO',  timeout = self.settings.timeout)
        
        # create motive read socket
        self.sockets.read_motive_sk = self._setup_sockets(self.sockets.motive['IP'], self.sockets.motive['PORT'], 'MOTIVE_SK',  timeout = self.settings.timeout) 
    
        
        
    #########################
    
    
    def close_sockets(self):

        if self.sockets.read_unity_query is None:
            print('unity read query socket not open')
        else:
            # close unity read query socket 
            self.sockets.read_unity_query.socket.close()
            self.sockets.read_unity_query = None
        
        if self.sockets.read_unity_control is None:
            print('unity control read socket not open')
        else:
            # close unity control read socket
            self.sockets.read_unity_control.socket.close()
            self.sockets.read_unity_control = None
    
        if self.sockets.read_unity_info is None:
            print('unity unity info read socket not open')
        else:
            # close unity info read socket
            self.sockets.read_unity_info.socket.close()
            self.sockets.read_unity_info = None
        
        if self.sockets.read_motive_sk is None:
            print('motive read socket not open')
        else:
            # close motive read socket
            self.sockets.read_motive_sk.socket.close()
            self.sockets.read_motive_sk = None
        
        if self.sockets.write_unity_sk is None:
            print('unity write skeleton socket not open')
        else:
            # close unity write skeleton socket
            self.sockets.write_unity_sk.socket.close()
            self.sockets.write_unity_sk = None
        
        
    #########################
    
    
    def run(self, mode = None):
        
        if self.settings.control_from_dummy_data:
            self._import_dummy()
            
        self.acquired_first_skel = False
        self.regress_data_list = []
        self._debug_control = []
        
        self.select_features()
        
        if self.settings.n_readings == None:
            self.settings.n_readings = np.inf
        
        ###
        
        if mode == None:
            mode = self.settings.mode
        
        if mode == 'avatar':
            
            self._run_avatar()
        
        if mode == 'acquisition':
            
            self._run_acquisition()
        
        if mode == 'control':
            
            self._run_control()
        
        
    #########################
        
    
    def _write_sk_to_unity(self, skel):
    
        skel_msg = np.reshape(skel[: , :-3], 21 * 8)
        arr = skel_msg.tolist()
    
        arr = arr + [float(count)]
    
        strs = ""
        # one int and 7 floats, '21' times
    
        for i in range(0, len(arr) // 4):
            if i % 8 == 0:
                strs += "i"
            else:
                strs += "f"
    
        print(arr)
        # print(len(arr))
        message = struct.pack('%sf' % len(arr), *arr)
    
        # print(message)
        self._udp_write(message)
        
        
    #########################
        
    
    def _write_commands_to_unity(self, commands):
    
        arr = commands
    
        strs = ""
        
        # 4 floats
    
        for i in range(0, len(arr) // 4):
                strs += "f"
    
        print(arr)
        # print(len(arr))
        message = struct.pack('%sf' % len(arr), *arr)
    
        # print(message)
        self._udp_write(message)
        
        
    #########################
        
    
    def write_controls_to_unity(self, controls):
    
        arr = controls.tolist()
    
        strs = ""
        
        # pars into floats
    
        for i in range(0, len(arr) // 4):
                strs += "f"
                
        message = struct.pack('%sf' % len(arr), *arr)
    
        self._udp_write(message)
    
    
    
    
    
    
    
#    def open_some_comm
#        unity_sk_client = Socket_info()
#    
#        unity_sk_client.IP = UDP_sett.IP_UNITY
#        unity_sk_client.PORT = UDP_sett.PORT_UNITY_WRITE_SK_CLIENT
#    
#    if not EXAMPLE_DATA:
#        skel = []
#    
#    def open_comm
#        # create unity read query / write skeleton socket
#        Read_unity_query = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_QUERY, 'UNITY_QUERY', timeout = 0.001)
#        Write_unity_sk = Read_unity_query
#        
#        # create unity control read socket
#        Read_unity_control = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_READ_CALIB, 'UNITY_CALIB',  timeout = 0.001)
#        
#        # create unity info read socket
#        Read_unity_info = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_READ_CALIB_INFO, 'UNITY_INFO',  timeout = 0.001)
#        
#        # create motive read socket
#        Read_motive_sk = setup(UDP_sett.IP_MOTIVE, UDP_sett.PORT_MOTIVE, 'MOTIVE_SK',  timeout = 0.001) #1ms to read everything
#            
#        
#    def should_be_a_function_or_better_an_option_for_control_function
#        if EXAMPLE_DATA:
#        
#            ###################        TEST        ###################
#            
#            test_data = pd.read_csv(data_folder + 'pilot3_inst_1_2018_Jun_22_06_53_03PM_roll_straight.txt')
#            
#            in_data = test_data.iloc[:,:231]
#            
#            out_data = test_data.iloc[:,231:]
#            
#            col_no_eul = [x for x in in_data if any(y in x for y in motive_indices_base)]
#            
#            in_data = in_data[col_no_eul]
#            
#            parameters = parameters.iloc[:,:-2]   
#            parameters_val = parameters.values
#            
#            param_av = parameters_val[0,:].reshape(len(used_body_parts),-1)
#            param_std = parameters_val[1,:].reshape(len(used_body_parts),-1)
#        
#            # limit loop duration for test
#            
#            sett.N_READS = 10 # len(test_data)
#        #    sett.N_READS = len(test_data)
#        
#            # don't wait for query
#            unity_query = 'c'
#            
#            y_score_all = []
#        
#        #    plt.ion()
#        #    fig = plt.figure()
#        #    ax1 = fig.add_subplot(211)
#        #    ax2 = fig.add_subplot(212)
#                     
#            regress_data_list = []
#            
#            df_first = []
#            first_skel = []
#            
#            
#    def avatar_function
#            
#    while count<sett.N_READS:
#        if mode.name=='avatar':
#    
#            while count<sett.N_READS:
#                # create motive read socket
#                # update skeleton
#                # close motive read socket
#                (skel) = read_sk_motive(UDP_sett)
#    
#                query = ''
#    
#                # check if unity query
#                unity_query = read(Read_unity_query)
#    
#                # close unity read socket
#                # Write_unity_sk.socket.close()
#    
#                # if query : send skeleton
#                if unity_query=='r':
#    
#                    print('sending skeleton to UNITY')
#    
#                    # send skeleton
#                    write_sk_to_unity(Write_unity_sk, unity_sk_client, skel)
#    
#                elif unity_query=='q':
#    
#                    # close unity write socket
#                    Read_unity_query.socket.close()
#                    
#                    break