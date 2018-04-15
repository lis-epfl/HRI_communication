import numpy as np
import socket
import struct
import subprocess
import sys

# from time import sleep
import timeit

##################      CONSTANTS      ##################

READ_XSENS = 0
WRITE_TO_UNITY = 0
READ_JOY_FROM_UNITY = 1
READ_REPLY_UNITY = 0

##################      SETTINGS      ##################

IP_ACQ = "127.0.0.1"    # Symbolic name meaning all available interfaces
PORT_ACQ = 27000    # Arbitrary non-privileged port

IP_UNITY = "127.0.0.1"
PORT_UNITY_READ_JOY = 28000
PORT_UNITY_READ_JOY_INFO = 29000

if (READ_XSENS or WRITE_TO_UNITY or READ_REPLY_UNITY):
    # Datagram (udp) socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Socket created')
    except socket.error as msg:
        print('Failed to create socket. Error : ', msg)
        sys.exit()
    # Bind socket to local IP and port
    try:
        s.bind((IP, PORT))
    except socket.error as msg:
        print('Bind failed. Error : ', msg)
        sys.exit()
    print('Socket XSENS bind complete')

if READ_JOY_FROM_UNITY:
    # Datagram (udp) socket
    try:
        s_readjoy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Socket created')
    except socket.error as msg:
        print('Failed to create socket. Error : ', msg)
        sys.exit()
    # Bind socket to local IP and port
    try:
        s_readjoy.bind((IP_UNITY, PORT_UNITY_READ_JOY))
    except socket.error as msg:
        print('Bind failed. Error : ', msg)
        sys.exit()
    print('Socket XSENS bind complete')

    # Datagram (udp) socket
    try:
        s_readjoy_info = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Socket created')
    except socket.error as msg:
        print('Failed to create socket. Error : ', msg)
        sys.exit()
    # Bind socket to local IP and port
    try:
        s_readjoy_info.bind((IP_UNITY, PORT_UNITY_READ_JOY_INFO))
    except socket.error as msg:
        print('Bind failed. Error : ', msg)
        sys.exit()
    print('Socket XSENS bind complete')

if READ_XSENS:
    1# subprocess.Popen(["C:\Users\matteoPC\Documents\GitHub\Python_acquisition\StreamFromXSENS/release/StreamFromXSENS.exe"])

# now keep talking with the client
count = float(0)

start = timeit.timeit()
while count < 1000:
    # sleep(1e-3)
    if READ_XSENS:()

    if WRITE_TO_UNITY:
        print('WRITING TO UNITY')

        arr = (count, count * 2, count * 3, count * 4)

        mes = arr
        print(mes)
        message = struct.pack('%sf' % len(mes), *mes)
        print(message)
        s.sendto(message, (UNITY_IP, UNITY_PORT))

        print('Sent', message, UNITY_IP, 'port', UNITY_PORT)

    if READ_JOY_FROM_UNITY:
        print('READING FROM UNITY')
        # receive data from client (data, addr)
        data, addr = s_readjoy.recvfrom(4096)

        if not data:
            break

        print("Byte Length of Message :", len(data), "\n")
        strs = ""
        for i in range(0, len(data)//4):
            strs += "f"
        print(strs)
        print(len(data))
        print("Message Data :", struct.unpack(strs, data), "\n")

        data, addr = s_readjoy_info.recvfrom(4096)

        if not data:
            break

        print("Byte Length of Message :", len(data), "\n")
        strs = ""
        for i in range(0, len(data)//4):
            strs += "i"
        print(strs)
        print(len(data))
        print("Message Data :", struct.unpack(strs, data), "\n")

    if READ_REPLY_UNITY:
        print('READING FROM UNITY')
        # receive data from client (data, addr)
        data, addr = s.recvfrom(8)

        print(data)

        if not data:
            break

        print("Byte Length of Message :", len(data), "\n")   # should be one!
        strs = None
        for i in range(0, len(data)/1):
            strs += "c"     # it's a char
        print("strs: ", strs)

        code = struct.unpack(strs, data)
        print("Message Data :", code, "\n")
        # print(code[0])

        if code[0] == '1':
            print("ORA RISPONDIAMO")
            arr = [float(10), float(10), float(10), float(0.0)]

            print(arr)
            print(len(arr))
            message = struct.pack('%sf' % len(arr), *arr)
            print(message)
            s.sendto(message, (UNITY_IP, UNITY_PORT))

            print('Sent', message, UNITY_IP, 'port', UNITY_PORT)

        if code[0] == '10':
            break

    count = count + 1
    print("count =", count)

end = timeit.timeit()
print('total acquisition time : ', end - start)

if (READ_XSENS or WRITE_TO_UNITY or READ_REPLY_UNITY):
    s.close()
if READ_JOY_FROM_UNITY:
    s_readjoy.close()
