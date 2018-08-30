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
            
            if sett.DUMMY_READ:
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
        self.sockets.write_unity_sk = Read_unity_query
        
        # create unity control read socket
        self.sockets.read_unity_control = self._setup_sockets(self.sockets.unity_calib['IP'], self.sockets.unity_calib['PORT'], 'UNITY_CALIB',  timeout = self.settings.timeout)
        
        # create unity info read socket
        self.sockets.read_unity_info = self._setup_sockets(self.sockets.unity_info['IP'], self.sockets.unity_info['PORT'], 'UNITY_INFO',  timeout = self.settings.timeout)
        
        # create motive read socket
        self.sockets.read_motive_sk = self._setup_sockets(self.sockets.motive['IP'], self.sockets.motive['PORT'], 'MOTIVE_SK',  timeout = self.settings.timeout) 
    
        
    #########################
    
    
    def run(self):
        
        count = 0
        
        if self.settings.mode == 'avatar':
            
            while count<self.settings.n_readings:
                
                count += 1
                
                # create motive read socket
                # update skeleton
                # close motive read socket
                (skel) = self._consume_motive_skeleton()
    
                query = ''
    
                # check if unity query
                unity_query = get_unity_query(Read_unity_query)
    
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