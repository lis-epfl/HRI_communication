
import numpy as np
import socket as soc
from socket import timeout
import struct
import subprocess
import sys

from time import sleep
from datetime import datetime

import PSpincalc as sp

import matplotlib.pyplot as plt

from enum import Enum


# code to speed test

tend = datetime.now()


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
    avatar = 1
    acquisition = 2
    control = 3

mode = Mode_enum(1)

##################      SETTINGS      ##################



N_RB_IN_SKEL = 21

sett.N_READS = 0

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
UDP_sett.PORT_UNITY_READ_CONTROL = 28000
UDP_sett.PORT_UNITY_READ_CONTROL_INFO = 29000

UDP_sett.PORT_UNITY_QUERY = 30000

UDP_sett.PORT_UNITY_WRITE_SK = 30000

UDP_sett.PORT_UNITY_WRITE_SK_CLIENT = 26000


if mode.name=='avatar':

    sett.N_READS = 1000

    sett.READ_MOTIVE_SK = 1

    sett.READ_QUERY_FROM_UNITY = 1

    sett.WRITE_SK_TO_UNITY = 1

    sett.OPEN_CLOSE_CONTINUOUS = 1

    sett.DUMMY_READ = False


##################      FUNCTIONS      ##################


def setup(IP, PORT, ID, timeout = 0.1):
    # Datagram (udp) socket
    try:
        socket = soc.socket(soc.AF_INET, soc.SOCK_DGRAM)
        # print('socket created')
    except socket.error as msg:
        print('Failed to create socket. Error : ', msg)
        sys.exit()
    # Bind socket to local IP and port
    try:
        socket.bind((IP, PORT))
    except soc.error as msg:
        print('Bind failed. Error Code : ', msg)
        sys.exit()
    # print('socket ', ID, ' bind complete')

    # set timeout
    socket.settimeout(timeout)

    read_s = Socket_struct() # Create an empty socket structure

    read_s.socket = socket
    read_s.ID = ID

    return read_s


def read(Read_struct):
    # print('\nREADING FROM', Read_struct.type, '\n')
    # receive data from client (data, addr)

    if Read_struct.ID == 'MOTIVE_RB':

        if DUMMY_READ:
            data = b'\x01\x00\x04\x00\xd0hG?\xe7sp?.\xbf\x93\xc0\\f\xbf=$\xd9j?]\xa9\x94=~\x92\xc2>'
        else:
            data, addr = Read_struct.socket.recvfrom(4096)

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

        if sett.DUMMY_READ:
            data = b'\x01\x00\x04\x00\xd0hG?\xe7sp?.\xbf\x93\xc0\\f\xbf=$\xd9j?]\xa9\x94=~\x92\xc2>'
        else:
            data, addr = Read_struct.socket.recvfrom(4096)

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
        
        BONE_S_SIZE = 8

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

    elif Read_struct.ID == 'UNITY_CONTROL':

        # receive data from client (data, addr)
        data, addr = Read_struct.socket.recvfrom(4096)

        if not data:
            return None

        print("Byte Length of Message :", len(data), "\n")
        strs = ""
        for i in range(0, len(data)//4):
            strs += "f"

        # print(strs)
        # print(len(data))

        unity_control = struct.unpack(strs, data)
        # print("Message Data :", unity_control, "\n")
        return unity_control

    elif Read_struct.ID == 'UNITY_INFO':

        data, addr = Read_struct.socket.recvfrom(4096)

        if not data:
            return None

        print("Byte Length of Message :", len(data), "\n")
        strs = ""
        for i in range(0, len(data)//4):
            strs += "i"

        # print(strs)
        # print(len(data))

        unity_info = struct.unpack(strs, data)
        # print("Message Data :", unity_control, "\n")
        return unity_info

    elif Read_struct.ID == 'UNITY_QUERY':

        try:
            data, addr = Read_struct.socket.recvfrom(4096)
        except timeout:
            return 't'

        if not data:
            return None

        # we receive a char

        unity_query = data.decode("utf-8") 
        print("Message Data :", unity_query, "\n")
        return unity_query


def write(Write_struct, towhom, msg):
    Write_struct.socket.sendto(msg, (towhom.IP, towhom.PORT))
    # print('Sent', msg, towhom.IP, 'port', towhom.PORT)
    return


def read_sk_motive(sett, UDP_sett, skel_all):
    if sett.OPEN_CLOSE_CONTINUOUS:
        Read_motive_sk = setup(UDP_sett.IP_MOTIVE, UDP_sett.PORT_MOTIVE, 'MOTIVE_SK')

    skel = read(Read_motive_sk)

    # # extract euler angles
    # skel_eul = np.reshape(skel[:,-3:], 21*3)
    # # make it horizontal
    # skel_eul = skel_eul[:, None].T

    # print(skel_eul)

    if skel_all.size == 0:
        skel_all = skel
        # skel_eul_all = skel_eul
    else:
        skel_all = np.r_[skel_all, skel]
        # skel_eul_all = np.r_[skel_eul_all, skel_eul_old]

    # skel_eul_old = skel_eul

    if sett.OPEN_CLOSE_CONTINUOUS:
        Read_motive_sk.socket.close()

    return (skel, skel_all)


def write_sk_to_unity(Write_unity_sk, client, skel):

    skel_msg = np.reshape(skel[:,:-3], 21*8)
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


##################      IMPLEMENTATION      ##################


# if (not OPEN_CLOSE_CONTINUOUS):
#     if (READ_MOTIVE_RB or READ_MOTIVE_SK):
#         Read_motive = setup(IP_MOTIVE, PORT_MOTIVE, 'MOTIVE_RB')
#         Read_motive_sk = Read_motive
#         Read_motive_sk.ID = 'MOTIVE_SK'

    # if READ_FROM_UNITY:
    #     1
    #     Read_unity_control = setup(IP_UNITY, PORT_UNITY_READ_CONTROL, 'UNITY_CONTROL')
    #     Read_unity_info = setup(IP_UNITY, PORT_UNITY_READ_CONTROL_INFO, 'UNITY_INFO')

skel_all = np.array([])

count = 0

if sett.WRITE_SK_TO_UNITY:
    unity_sk_client = Socket_info()

    unity_sk_client.IP = UDP_sett.IP_UNITY
    unity_sk_client.PORT = UDP_sett.PORT_UNITY_WRITE_SK_CLIENT

# create unity read socket
Read_unity_query = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_QUERY, 'UNITY_QUERY', timeout = 0.01)

Write_unity_sk = Read_unity_query

if mode.name=='avatar':
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

            # create unity write socket
            # Write_unity_sk = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_WRITE_SK, 'UNITY_WRITE_SK')

            # send skeleton
            write_sk_to_unity(Write_unity_sk, unity_sk_client, skel)
            
        elif unity_query=='q':

            break


        # else : skip
        count = count + 1
        print(count)

# close unity write socket
Write_unity_sk.socket.close()
# if READ_XSENS:
#     subprocess.Popen(["C:\Users\matteoPC\Documents\GitHub\Python_acquisition\StreamFromXSENS/release/StreamFromXSENS.exe"])


# now keep talking with the client
count = float(0)

start = datetime.now()


motive_indices = ['ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w', 'yaw', 'pitch', 'roll']
motive_data = np.array(motive_indices)
motive_data_full = np.array

# while count < sett.N_READS:

#     start_iter = datetime.now()
#     if sett.READ_FROM_UNITY:

#         if OPEN_CLOSE_CONTINUOUS:
#             Read_unity_control = setup(IP_UNITY, PORT_UNITY_READ_CONTROL, 'UNITY_CONTROL')

#         unity_control = read(Read_unity_control)

#         if OPEN_CLOSE_CONTINUOUS:
#             Read_unity_control.socket.close()

#         if OPEN_CLOSE_CONTINUOUS:
#             Read_unity_info = setup(IP_UNITY, PORT_UNITY_READ_CONTROL_INFO, 'UNITY_INFO')

#         unity_info = read(Read_unity_info)

#         if OPEN_CLOSE_CONTINUOUS:
#             Read_unity_info.socket.close()
#     if sett.READ_MOTIVE_RB:

#         for i in range(0, N_RB_IN_SKEL):

#             data = read(Read_motive)

#             # print('\n')
#             # print(data.ID)
#             # print(data.position)
#             # print(data.quaternion)
#             # print(data.euler)
#             # print('\n')

#             ID = np.array(data.ID)
#             pos = np.array(data.position)
#             quat = np.array(data.quaternion)
#             euler = np.array(data.euler)

#             bone = np.append(ID, pos)
#             bone = np.append(bone, quat)
#             bone = np.append(bone, euler)

#             if i>1:
#                 bone_all = np.vstack((bone, bone_old))
#             else:
#                 bone_all = bone

#             bone_old = bone

#             # print (bone)
#             # print (bone_all)

#             motive_data = np.vstack((motive_data, bone))

#             motive_data_full_temp = [s + '_' for s in motive_indices]
#             motive_data_full_temp = [s + str(ID) for s in motive_data_full_temp]

#             motive_data_full = np.append(motive_data_full, motive_data_full_temp)

#             # print(motive_data_full)

#     if sett.READ_MOTIVE_SK:

#         (skel, skel_all) = read_sk_motive(sett, UDP_sett, skel_all)

#     if sett.WRITE_SK_TO_UNITY:
#         write_sk_to_unity(sett, UDP_sett, skel)

#     end_iter = datetime.now()
#     count = count + 1

#     print('iter time = ', end_iter - start_iter)


# np.savetxt('test_skelall.txt', (skel_all), delimiter=",", fmt="%s")
# np.savetxt('test_skelall_eul.txt', (skel_eul_all), delimiter=",", fmt="%s")
# np.savetxt('test_boneall.txt', (motive_data), delimiter=",", fmt="%s")
# np.savetxt('test.txt', (motive_data), delimiter=",", fmt="%s")
# np.savetxt('test_1.txt', (motive_data_full), delimiter=",", fmt="%s")

end = datetime.now()
print('total time = ', end - start)
