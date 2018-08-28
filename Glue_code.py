import datetime 
from datetime import datetime as date_t
from enum import Enum
import math
import matplotlib.pyplot as plt
import numpy as np
from numpy import size
import os
import pandas as pd
import PSpincalc as sp
import socket as soc
from socket import timeout
import struct
import subprocess
import sys
from time import sleep
import time

from builtins import any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'HRI_Mapping'))

from Mapping import *
import Mapping_settings as settings

# code to speed test


class Socket_struct:
    pass

class Socket_info:
    pass

class Bone_struct:
    pass

class Settings:
    pass

class UDP_Settings:
    pass

UDP_sett = UDP_Settings()

sett = Settings()


##################      MODE      ##################


class Mode_enum(Enum):
    custom = 0
    avatar = 1
    acquisition = 2
    control = 3
    
##################      CONSTANTS      ##################
        
global QUAT_LEN

QUAT_LEN = 4
    
# size of the BONE structure
BONE_S_SIZE = 8

# number of bones in skeleton
N_RB_IN_SKEL = 21

AXIS = {0 : 'roll', 1 : 'pitch'}
PHASE_ROLL = {0 : 'straight', 1 : 'up', 2 : 'down'}
PHASE_PITCH = {0 : 'straight', 1 : 'right', 2 : 'left'}

PHASE = {'roll' : PHASE_ROLL, 'pitch' : PHASE_ROLL}

##################      FUNCTIONS      ##################


def setup(IP, PORT, ID, timeout = 0.1):
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


def udp_read(Read_struct):
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

def udp_process(data, Read_struct):

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


def write(Write_struct, towhom, msg):
    Write_struct.socket.sendto(msg, (towhom.IP, towhom.PORT))
    # print('Sent', msg, towhom.IP, 'port', towhom.PORT)
    return

def read_rb_motive(UDP_sett):

    data = read(Read_motive)

    # ID = np.array(data.ID)
    # pos = np.array(data.position)
    # quat = np.array(data.quaternion)
    # euler = np.array(data.euler)

    # bone = np.append(ID, pos)
    # bone = np.append(bone, quat)
    # bone = np.append(bone, euler)

    # if i>1:
    #     bone_all = np.vstack((bone, bone_old))
    # else:
    #     bone_all = bone

    # bone_old = bone

    # # print (bone)
    # # print (bone_all)

    # motive_data = np.vstack((motive_data, bone))

    # motive_data_full_temp = [s + '_' for s in motive_indices]
    # motive_data_full_temp = [s + str(ID) for s in motive_data_full_temp]

    # motive_data_full = np.append(motive_data_full, motive_data_full_temp)

    # print(motive_data_full)

    return bone

def skel_keep_used_body_parts(skel, used_body_parts):
    
    i = search_bone_per_index(skel, np.array(used_body_parts))
            
    return skel[i,:]

def skel_keep_features(skel, feats):
    
    # size of mask : ID(1) + pos(3) + quat(3) + eul(3) = 11
    
    # mask depends on feats
    if feats == 'all':
        mask = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    elif feats == 'angles':
        mask = np.array([4, 5, 6, 7, 8, 9, 10])
    elif feats == 'euler':
        mask = np.array([8, 9, 10])
    elif feats == 'quaternions':
        mask = np.array([4, 5, 6, 7])
            
    return skel[:,mask]
    
def relativize_skeleton(skel):
    
    skel = relativize_bone(9, 8, skel)
    skel = relativize_bone(8, 7, skel)
    skel = relativize_bone(7, 6, skel)
    skel = relativize_bone(6, 3, skel)
    skel = relativize_bone(13, 12, skel)
    skel = relativize_bone(12, 11, skel)
    skel = relativize_bone(11, 10, skel)
    skel = relativize_bone(10, 3, skel)
    
    return skel

def values_to_quaternion(quat_val):
    
    quat = np.quaternion(quat_val[3], quat_val[0], quat_val[1], quat_val[2])
    
    return quat

def quaternion_to_values(quat):
    
    quat_val = np.array([quat.x, quat.y, quat.z, quat.w])
    
    return quat_val
    
def unbias_skeleton(skel, first_skel, quat_loc = 4):
    
    for i in range(size(skel, 0)):
        bias_quat = skel[i][quat_loc : quat_loc + QUAT_LEN]
        ref_quat = first_skel[i][quat_loc : quat_loc + QUAT_LEN]
        
        #unbiased
        skel[i][quat_loc : quat_loc + QUAT_LEN] = quaternion_to_values(values_to_quaternion(bias_quat)/values_to_quaternion(ref_quat))
        
    return skel
    
def search_bone_per_index(skel, idx):
    
    arr = skel[:,0]
    
    i = np.where(idx==arr[:,None])[0]

    return i

def compute_ea_skel(skel, quat_loc = 4):
    
    def compute_ea_bone(a, quat_loc = 4):
        # compute eul
        
        quat_val = a[quat_loc : quat_loc + QUAT_LEN]
        
        eul = Q2EA((quat_val[3], quat_val[0], quat_val[1], quat_val[2]), EulerOrder="zyx", ignoreAllChk=True)[0]
        
        print(eul)
        
        # right order [xzy] : due to Motive settings
        return np.array([eul[2], eul[0], eul[1]])


    # pre-allocation
    eul_skel = np.zeros([size(skel, 0), size(skel, 1) + 3])
    
    eul_skel[:, :size(skel, 1)] = skel
    
    tot_t = 0
    
    eul = np.apply_along_axis(compute_ea_bone, 1, skel)
    
    eul_skel[:,-3:] = eul
        
    return eul_skel


def relativize_bone(angles_to_correct, with_respect_to, skel, quat_loc = 4):
    
    global QUAT_LEN
    
    ref_idx = search_bone_per_index(skel, with_respect_to)
    abs_idx = search_bone_per_index(skel, angles_to_correct)
    
    # extract rows
    ref_row = skel[ref_idx].reshape(-1)
    abs_row = skel[abs_idx].reshape(-1)
    
    # extract quaternions
    ref_quat = ref_row[quat_loc : quat_loc + QUAT_LEN]
    abs_quat = abs_row[quat_loc : quat_loc + QUAT_LEN]
    
    ref_quat_q = values_to_quaternion(ref_quat)
    abs_quat_q = values_to_quaternion(abs_quat)
    
    # compute difference
    rel_quat_q = abs_quat_q/ref_quat_q
    
    # stick back in array
    abs_row[quat_loc : quat_loc + QUAT_LEN] = quaternion_to_values(rel_quat_q)
    
    skel[abs_idx] = abs_row
    
    return skel
    

def write_sk_to_unity(Write_unity_sk, client, skel):

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
    write(Write_unity_sk, client, message)

    if 0:
        plt.axis()
        plt.scatter(count, arr[8*2+1], c = 1)
        plt.pause(0.0001)

