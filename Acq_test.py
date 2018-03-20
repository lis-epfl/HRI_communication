import numpy as np
import socket
import struct
import subprocess
import sys

# from time import sleep
import timeit

##################      CONSTANTS      ##################

READ_XSENS = 1
WRITE_TO_UNITY = 0
READ_FROM_UNITY = 0
READ_REPLY_UNITY = 0

##################      SETTINGS      ##################

IP = "127.0.0.1"    # Symbolic name meaning all available interfaces
PORT = 26000    # Arbitrary non-privileged port

UNITY_IP = "127.0.0.1"
# UNITY_PORT = 26000

if (READ_XSENS or READ_FROM_UNITY or WRITE_TO_UNITY or READ_REPLY_UNITY):
    # Datagram (udp) socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print 'Socket created'
    except socket.error, msg:
        print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    # Bind socket to local IP and port
    try:
        s.bind((IP, PORT))
    except socket.error, msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    print 'Socket XSENS bind complete'

if READ_XSENS:
    subprocess.Popen(["C:\Users\matteoPC\Documents\GitHub\Python_acquisition\StreamFromXSENS/release/StreamFromXSENS.exe"])

# now keep talking with the client
count = float(0)

start = timeit.timeit()
while count < 1000:
    # sleep(1e-3)
    if READ_XSENS:
        print 'READING FROM SENSORS'
        # receive data from client (data, addr)
        data, addr = s.recvfrom(4096)

        if not data:
            break

        print "Byte Length of Message :", len(data), "\n"
        strs = ""
        for i in range(0, len(data) / 4):
            strs += "f"
        print strs
        print "Message Data :", struct.unpack(strs, data), "\n"

    if WRITE_TO_UNITY:
        print 'WRITING TO UNITY'

        arr = (count, count * 2, count * 3, count * 4)

        mes = arr
        print mes
        message = struct.pack('%sf' % len(mes), *mes)
        print message
        s.sendto(message, (UNITY_IP, UNITY_PORT))

        print 'Sent', message, UNITY_IP, 'port', UNITY_PORT

    if READ_FROM_UNITY:
        print 'READING FROM UNITY'
        # receive data from client (data, addr)
        data, addr = s.recvfrom(4096)

        if not data:
            break

        print "Byte Length of Message :", len(data), "\n"
        strs = ""
        for i in range(0, len(data)/1):
            strs += "c"
        print strs
        print "Message Data :", struct.unpack(strs, data), "\n"

    if READ_REPLY_UNITY:
        print 'READING FROM UNITY'
        # receive data from client (data, addr)
        data, addr = s.recvfrom(8)

        print data

        if not data:
            break

        print "Byte Length of Message :", len(data), "\n"   # should be one!
        strs = ""
        for i in range(0, len(data)/1):
            strs += "c"     # it's a char
        print "strs: ", strs

        code = struct.unpack(strs, data)
        print "Message Data :", code, "\n"
        # print code[0]

        if code[0] == '1':
            print "ORA RISPONDIAMO"
            arr = [float(10), float(10), float(10), float(0.0)]

            print arr
            print len(arr)
            message = struct.pack('%sf' % len(arr), *arr)
            print message
            s.sendto(message, (UNITY_IP, UNITY_PORT))

            print 'Sent', message, UNITY_IP, 'port', UNITY_PORT

        if code[0] == '10':
            break

    count = count + 1
    print "count =", count

end = timeit.timeit()
print end - start

s.close()
