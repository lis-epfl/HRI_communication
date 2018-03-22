
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

IP = " "    # Symbolic name meaning all available interfaces
PORT = 9000    # Arbitrary non-privileged port

UNITY_IP = "127.0.0.1"
# UNITY_PORT = 26000

if (READ_XSENS or READ_FROM_UNITY or WRITE_TO_UNITY or READ_REPLY_UNITY):
    # Datagram (udp) socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Socket created')
    except (socket.error, msg):
        print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    # Bind socket to local IP and port
    try:
        s.bind((IP, PORT))
    except (socket.error, msg):
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('Socket MOTIVE bind complete')

# if READ_XSENS:
#     subprocess.Popen(["C:\Users\matteoPC\Documents\GitHub\Python_acquisition\StreamFromXSENS/release/StreamFromXSENS.exe"])

# now keep talking with the client
count = float(0)

start = timeit.timeit()
while count < 10:
    # sleep(1e-3)
    if READ_XSENS:
        print('READING FROM SENSORS')
        # receive data from client (data, addr)
        data, addr = s.recvfrom(4096)

        if not data:
            break

        print("Byte Length of Message :", len(data), "\n")
        strs = ""

        # THIS IS A int_32

        for i in range(0, 1):
            strs += "i"

        # THIS IS A float

        for i in range(1, len(data) // 4):
            strs += "f"

        print(strs)

        print("Message Data (float):", struct.unpack(strs, data), "\n")

    count = count + 1;

end = timeit.timeit()
print(end - start)

s.close()
