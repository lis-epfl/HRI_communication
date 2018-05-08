import datetime 
from datetime import datetime
from enum import Enum
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import PSpincalc as sp
import socket as soc
from socket import timeout
import struct
import subprocess
import sys
from time import sleep


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

        # print("Byte Length of Message :", len(data), "\n")
        strs = ""

        # one int and 7 floats, '21' times

        for i in range(0, len(data) // 4):
            if i % 8 == 0:
                strs += "i"
            else:
                strs += "f"

        # print("Message Data (skeletal bone):", struct.unpack(strs, data), "\n")

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
                euler = sp.Q2EA(np.array(quaternion), EulerOrder="zyx", ignoreAllChk=True)[0]
            else:
                ID = ID + [(int(bin(bone[0])[-8:], 2))]
                position = np.vstack((position, bone[1:4]))
                quaternion_t = bone[4:]
                quaternion = np.vstack((quaternion, [quaternion_t[j] for j in Q_ORDER]))
                euler = np.vstack((euler, (sp.Q2EA(np.array(quaternion), EulerOrder="zyx", ignoreAllChk=True)[0])))
            
        ID = np.array(ID)
        
        data = np.c_[ID, position, quaternion, euler]
        
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



##################      SETTINGS      ##################


mode = Mode_enum(2)

filename = datetime.now().strftime("%Y_%b_%d_%I_%M_%S%p")
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


SUBJECTS = {'MatteoM' : 'pilot1', 'StefanoM' : 'pilot2'}

subject = SUBJECTS['MatteoM']

##################      IMPLEMENTATION      ##################


start = datetime.now()


if sett.WRITE_SK_TO_UNITY:
    unity_sk_client = Socket_info()

    unity_sk_client.IP = UDP_sett.IP_UNITY
    unity_sk_client.PORT = UDP_sett.PORT_UNITY_WRITE_SK_CLIENT

count = 0

query = ''

# define data structure and headers

        
motive_indices = np.array([])

motive_indices_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w', 'yaw', 'pitch', 'roll' ])

for i in range(N_RB_IN_SKEL):

    n = np.char.array([('_' + str(i+1))])

    if i==0:
        motive_indices = motive_indices_base + (n)
    else:
        motive_indices = np.r_[motive_indices, motive_indices_base + (n)]

        
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

skel = []

# create unity read query / write skeleton socket
Read_unity_query = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_QUERY, 'UNITY_QUERY', timeout = 0.001)
Write_unity_sk = Read_unity_query

# create unity control read socket
Read_unity_control = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_READ_CALIB, 'UNITY_CALIB',  timeout = 0.001)

# create unity info read socket
Read_unity_info = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_READ_CALIB_INFO, 'UNITY_INFO',  timeout = 0.001)

# create motive read socket
Read_motive_sk = setup(UDP_sett.IP_MOTIVE, UDP_sett.PORT_MOTIVE, 'MOTIVE_SK',  timeout = 0.001) #1ms to read everything
    
while count<sett.N_READS:
    if mode.name=='avatar':

        while count<sett.N_READS:
            # create motive read socket
            # update skeleton
            # close motive read socket
            (skel) = read_sk_motive(UDP_sett)

            query = ''

            # check if unity query
            unity_query = read(Read_unity_query)

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

    elif mode.name=='acquisition':
        
        startloop = datetime.now()

        # consume skeleton
        skel_data_temp = udp_read(Read_motive_sk)
        
        if skel_data_temp == 't':
            print ('skel = ', skel_data_temp)
        else:
            print ('skel = full skeleton')
            skel_data = skel_data_temp
        
        timesk = datetime.now();
        print ('time to read skeleton =', timesk - startloop)

        query = ''
        
        # read query
        query_data = udp_read(Read_unity_query)
        unity_query = udp_process(query_data, Read_unity_query)
             
        print ('UNITY query = ', unity_query)

        timequ = datetime.now();
        print ('time to read query =', timequ - timesk)
        
        # if query : read unity and skeleton, then save to csv
        if unity_query=='a':

            print('collecting data')
        
            # read unity calibration data
            udp_data = udp_read(Read_unity_control)
            unity_calib = np.array(udp_process(udp_data, Read_unity_control))
                            
            print('unity_calib = ', unity_calib)
            
            # read unity info
            udp_data = udp_read(Read_unity_info)
            unity_calib_info = np.array(udp_process(udp_data, Read_unity_info))
                            
            print('unity_calib_info = ', unity_calib_info)
            
            timeun = datetime.now();
            print ('time to read UNITY data =', timeun - timequ)
            
            # process skeleton
            if skel_data_temp == 't':   
                print ('using old skeleton')
                 # use old skel
                
            # save skel_data in list
            if len(skel) == 0:
                skel = [skel_data]
            else:
                skel.append(skel_data)
                
            timesk2 = datetime.now();
            print ('time to process second skeleton =', timesk2 - timeun)
                             
            
            # reshape all to 1D array    
            unity_calib = unity_calib.reshape(1, unity_calib.size)
            unity_calib_info = unity_calib_info.reshape(1, unity_calib_info.size)

#             print(skel.size)
#             print(unity_calib.size)
#             print(unity_calib_info.size)
            
            unity_row = np.c_[unity_calib, unity_calib_info]
            
            if unity_num.size:
                if unity_row.shape[1] == unity_data.size:
                    unity_num = np.vstack([unity_num, unity_row])
                else:
                    print('lost frame')
            else:
                unity_num =  unity_row
                
                
        elif unity_query=='q':

            # close unity write socket
            Read_unity_query.socket.close()
            
            # close unity control read socket
            Read_unity_control.socket.close()

            # close unity info read socket
            Read_unity_info.socket.close()
            
            # close motive read socket
            Read_motive_sk.socket.close()

            break

    if mode.name=='control':
        
        while True:
            # create motive read socket
            # update skeleton
            # close motive read socket
            (skel, skel_all) = read_sk_motive(sett, UDP_sett, skel_all)

            query = ''

            # check if unity query
            unity_query = read(Read_unity_query)

            # close unity read socket
            # Write_unity_sk.socket.close()

            # if query : send skeleton
            if unity_query=='r':

                print('sending skeleton to UNITY')

                # process skeleton (TOBEDONE)

                # send commands to unity (TOBEDONE)

            elif unity_query=='q':

                # close unity write socket
                Write_unity_sk.socket.close()

                break
            
    count = count + 1
    

# process motive skeleton data
skel_num = udp_process(skel[0], Read_motive_sk)    
skel_num.resize(1, skel_num.size)

for i in range(1, len(skel)):
    skel_np_t = udp_process(skel[i], Read_motive_sk)    
    skel_np_t.resize(1, skel_np_t.size)
    skel_num = np.vstack([skel_num, skel_np_t])

    
calib_data = np.c_[skel_num, unity_num]
data = np.vstack([data, calib_data])

if not os.path.isdir(foldername):
    os.mkdir(foldername)
    
home_fol = os.getcwd()
os.chdir(foldername)

if calib_data.shape[0]>1 and calib_data.shape[1]>3:
    filename = subject + '_' + filename + '_' + AXIS[calib_data[-1, -5]] + '_' + PHASE[AXIS[calib_data[-1, -5]]][calib_data[-1, -4]]
elif data.shape[0]==1:
    print('no data acquired')
else:
    print('problem with data size')
    
np.savetxt((filename + '.txt'), (data), delimiter=",", fmt="%s")
# np.savetxt('test_skelall_eul.txt', (skel_eul_all), delimiter=",", fmt="%s")
# np.savetxt('test_boneall.txt', (motive_data), delimiter=",", fmt="%s")
# np.savetxt('test.txt', (motive_data), delimiter=",", fmt="%s")
# np.savetxt('test_1.txt', (motive_data_full), delimiter=",", fmt="%s")

os.chdir(home_fol)

end = datetime.now()
print('total time = ', end - start)

data_pd = pd.read_csv(foldername + '/' + filename + '.txt')