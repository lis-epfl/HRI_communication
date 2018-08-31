#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 15:43:19 2018

@author: matteomacchini
"""


#####################################################


import datetime

#import matplotlib.pyplot as plt
#import numpy as np
#import os
#import pandas as pd
#from sklearn import metrics
#import time
import socket as soc
from socket import timeout
import sys
#
from HRI_communication_add import *
#import quaternion_operations as quat_op



# NEEDS TO BE SOLVED
class Socket_struct:
    pass


#####################################################

class HRI_communication():
    
    
    param = HRI_communication_param()
    settings = HRI_communication_settings()
    user = HRI_communication_user()
    sockets = HRI_communication_sockets()
    
    
    SUBJECTS = {'MatteoM' : 'pilot1', 
                'StefanoM' : 'pilot2', 
                'DavideZ' : 'pilot3'}
    
    subject = SUBJECTS['DavideZ']
    
    
    count = 0
    
    query = ''
    
    # define data structure and headers
    
    data_num = np.array([])
    
    skel_num = np.array([])
    
    unity_num = np.array([])
    
    skel = []
    
    
    
    
    motive_header = np.array([])
    
    motive_header_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w'])
    
    regression_header = np.array([])
    
    regression_header_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w', 'roll', 'pitch', 'yaw'])
    
    for i in range(settings.n_rigid_bodies_in_skeleton):
    
        n = np.char.array([('_' + str(i+1))])
    
        if i==0:
            motive_header = motive_header_base + (n)
            if i+1 in settings.used_body_parts:
                regression_header = regression_header_base + (n)
        else:
            motive_header = np.r_[motive_header, motive_header_base + (n)]
            if i+1 in settings.used_body_parts:
                regression_header = np.r_[regression_header, regression_header_base + (n)]
    
    
    unity_header_calib = np.char.array([ 'input1', 'input2', 'input3', 'input4', 'roll', 'pitch', 'yaw', 'roll_rate', 'pitch_rate', 'yaw_rate', 'vel_x', 'vel_y', 'vel_z', 'vel_semiloc_x', 'vel_semiloc_y', 'vel_semiloc_z', 'corr_roll', 'corr_pitch', 'pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z', 'rot_w', 'timestamp' ])
    unity_header_info = np.char.array([ 'calib_axis', 'calib_phase', 'is_input_not_zero', 'instance', 'loop counter' ])
    
    motive_header = np.array(motive_header)
    unity_header_calib = np.array(unity_header_calib)
    unity_header_info = np.array(unity_header_info)
    unity_header = np.r_[unity_header_calib, unity_header_info]
    
    calib_header = np.r_[motive_header, unity_header]
    
    data = calib_header
    data = data.reshape(1, data.size)
    
    
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
                    for i in range(21):
                        data = data + one_rb if len(data) else one_rb
                else:
                    return 't'
            else:
                return 't'
            
        return data
        
        
    #########################
        
        
    def _udp_write(self, msg):
        self.sockets.unity_write_sk.socket.sendto(msg, (self.sockets.unity_write_sk_client['IP'], self.sockets.unity_write_sk_client['PORT']))
        # print('Sent', msg, towhom.IP, 'port', towhom.PORT)
        
        
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
    
            for i in range(0, len(data_ump) // BONE_S_SIZE):
                bone = list(data_ump[i*BONE_S_SIZE : (1+i)*BONE_S_SIZE])
    
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
    
        query = ''
        
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
                skel_data = skel_data_temp
        
            unity_query = self._get_unity_query()
            
            unity_query = 'a'
            
        
            # if query : read unity and skeleton, then save to csv
            if unity_query=='a':
                
                skel_data = 1
            
                self._acquisition_routine(skel_data)
            
            elif unity_query=='q':
        
                self.close_sockets()
                
                break
            
        
    #########################
    
    
    def _acquisition_routine(self, skel_data):
            
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
            self.skel = [skel_data]
        else:
            self.skel.append(skel_data)
                             
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
        
        count = 0
            
        while count<self.settings.n_readings:
            
            count += 1
        
            if not self.example_data:
            
                skel_data_temp = self._consume_motive_skeleton()
                
                if skel_data_temp == 't':
                    print ('skel = ', skel_data_temp)
                else:
                    print ('skel = full skeleton')
                    skel_data = skel_data_temp
            
                unity_query = self._get_unity_query()
            
        
            # if query : read unity and skeleton, then save to csv
            if unity_query=='c':
            
                [regress_data_list, acquired_first_skel, first_skel, df_first, y_score_all, debug_info] = self._control_routine(regress_data_list, count, first_skel, df_first, y_score_all, motive_indices, used_body_parts, N_RB_IN_SKEL, acquired_first_skel, EXAMPLE_DATA, in_data, out_data)
        
            elif unity_query=='q':
        
                self.close_sockets()
                
                break
            

    #########################
    
    
    def _control_routine(self, regress_data_list, count, first_skel, df_first, y_score_all, motive_indices, used_body_parts, N_RB_IN_SKEL, acquired_first_skel, EXAMPLE_DATA = False, in_data = 0, out_data = 0):
        
        # if query : read unity and skeleton, then save to csv
        
    #    start = time.clock()
            
        # process skel data and add headers
        
        if  self.example_data:
            skel_num = in_data[count:count+1].values
        else:
            skel = skel_data
            skel = self._udp_process(skel)
            
        if self.control_preproc_pandas:
        
            # not converting to df anymore
            df = pd.DataFrame(skel_num, columns = self.motive_header)   
                # remove unused columns
                
            df = df[my_cols]
        else:
            skel = np.reshape(skel_num, (self.n_rigid_bodies_in_skel,-1))
            
            # used body parts
            skel = nskel_keep_used_body_parts(skel, used_body_parts)
        
        if not acquired_first_skel:
                     
            if USE_DF_METHOD:   
                # not converting to df anymore
                df_first = pd.DataFrame(skel_num, columns = motive_indices) 
                
                # remove unused columns
                
                df_first = df_first[my_cols]
                
                # compute relative angles
                
                df_first = relativize_df(df_first)
            else:
                
                first_skel = np.copy(skel)
                
                first_skel = relativize_skeleton(first_skel)
        
            acquired_first_skel = True
            
        
        # compute relative angles
        
        if USE_DF_METHOD:
            # df style
    #        start = time.clock()
            df = relativize_df(df)
    #        end = time.clock()
    #        print("time to rel (old) = " + str(end-start))
        else:
            # np style
    #        start = time.clock()
            skel = relativize_skeleton(skel)
    #        end = time.clock()
    #        print("time to rel (new) = " + str(end-start))
        
        
        # unbias angles
        
        if USE_DF_METHOD:
            # df style
            start = time.clock()
            # concatenate first and current skel
            df_combined = pd.concat([df_first,df])
            
            # unbias angles
    #        start = time.clock()
            df_combined = remove_bias_df(df_combined, used_body_parts)
    #        end = time.clock()
    #        print("time to bias (old) = " + str(end-start))
            
            df = df_combined[1:2]
        else:
            # np style
    #        start = time.clock()
            skel = unbias_skeleton(skel, first_skel)
    #        end = time.clock()
    #        print("time to bias (new) = " + str(end-start))
        
        # compute euler angles
        
        if USE_DF_METHOD:
            # df style
    #        start = time.clock()
            df = compute_ea_df(df, used_body_parts)
    #        end = time.clock()
    #        print("time to eul (old) = " + str(end-start))
        else:
            # np style
    #        start = time.clock()
            skel = compute_ea_skel(skel)
    #        end = time.clock()
    #        print("time to eul (new) = " + str(end-start))
        
        
        # save input data
        
        if USE_DF_METHOD:
            regress_data_list.append(df)
        else:
            regress_data_list.append(skel)
        
    #            if count == 9:
    #                print('breaking')
            
    #                break
        
        # normalize
        
        if USE_DF_METHOD:
            # df style
    #        start = time.clock()
            
            for j in list(df):
                # do not normalize quaternion components and outputs
                if 'pos' in j or 'pitch_' in j or 'roll_' in j or 'yaw_' in j :
                    [array_norm, norm_param_t] = normalize(df[j], parameters[j])
                    df[j] = array_norm
                    
    #        end = time.clock()
    #        print("time to norm (old) = " + str(end-start))
        else:
            # np style
    #        start = time.clock()
            
            skel = skel - param_av
            skel = skel / param_std
                    
    #        end = time.clock()
    #        print("time to norm (new) = " + str(end-start))
        
    
    #     regression
        
        if USE_DF_METHOD:
            # df style
            skel_fake = df[feats]
            
            y_score = best_mapping.predict(skel_fake)
            
            if not len(y_score_all):
                y_score_all = y_score.T
            else:
                y_score_all = np.column_stack((y_score_all,y_score.T))
        else:
            
            skel_f = skel_keep_features(skel, input_data)
            
            skel_r = skel_f.reshape(1, -1)
            
            y_score = best_mapping.predict(skel_r)
            
            if not len(y_score_all):
                y_score_all = y_score.T
            else:
                y_score_all = np.column_stack((y_score_all,y_score.T))
                
                
        print('')
        print(count)
        print('')
    #            
        end = time.clock()
        print("time to process control skeleton = " + str(end-start))
        
        y_true = out_data[outputs].values
        
        res = {"reg":best_mapping,
                    "reg_type":str(best_mapping),
                    "y_true":y_true,
                    "y_score":y_score
                    }
        
        plot_fit_performance(res)
        
        
        print(count)
    
        # send commands to unity (TOBEDONE)
        
        if USE_DF_METHOD:
            debug_info = {'df' : df,
                          'skel' : skel_fake,
                          'y_score' : y_score,
                          }
        else:
            debug_info = {'skel' : skel,
                          'y_score' : y_score,
                          }
                
            
            
    
        return [regress_data_list, acquired_first_skel, first_skel, df_first, y_score_all, debug_info]
    
    
    ### PUBLIC FUNCTIONS ###
    
    
    def import_mapping(self):
    
        
        import os,sys,inspect
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)
        sys.path.insert(0, os.path.normpath(os.path.join(parentdir, 'HRI_Mapping/')))
    
        import HRI_mapping
        
        mapp = HRI_mapping.HRI_mapping()
        
        mapp.load_last_for_this_subject()
        
        return mapp
        
        
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
        
        if mode == None:
            mode = self.settings.mode
        
        if mode == 'avatar':
            
            self._run_avatar()
        
        if mode == 'acquisition':
            
            self._run_acquisition()
        
        
    #########################
        
    
    def write_sk_to_unity(self, skel):
    
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
    
        if 0:
            plt.axis()
            plt.scatter(count, arr[8*2+1], c = 1)
            plt.pause(0.0001)
    

    
    
    
    
    
    
    
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