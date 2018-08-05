#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 20:06:53 2018

@author: matteomacchini
"""


    
################# OPTITRACK CONVENTIONS #################
    
    # 1 : hips         
    # 2 : abdomen      
    # 3 : torso         *
    # 4 : neck
    # 5 : head
    # 6 : l shoulder    *
    # 7 : l arm         *
    # 8 : l forearm     *
    # 9 : l hand        *
    # 10 : r shoulder   *
    # 11 : r arm        *
    # 12 : r forearm    *
    # 13 : r hand       *
        
    # 14+ : lower body

used_body_parts = [3, 6, 7, 8, 9, 10, 11, 12, 13]


##################      IMPLEMENTATION      ##################


if mode.name=='control':
    interface_folder = 'interfaces/'
    
    # load interface to file
    best_nl = load_obj(interface_folder + subject + '_' + '_best_nl')
    

start = date_t.now()


if sett.WRITE_SK_TO_UNITY:
    unity_sk_client = Socket_info()

    unity_sk_client.IP = UDP_sett.IP_UNITY
    unity_sk_client.PORT = UDP_sett.PORT_UNITY_WRITE_SK_CLIENT

count = 0

query = ''

# define data structure and headers

        
motive_indices = np.array([])

motive_indices_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w' , 'r' , 'p' , 'y' ])

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
    

used_str = ['_' + str(x) for x in used_body_parts]
my_cols = [col for col in df[0].columns if any(y in col for y in used_str)]

acquired_first_skel = False


###################        TEST        ###################

test_data = pd.read_csv(data_folder + 'pilot1_inst_1_2018_Jun_09_01_29_32PM_pitch_straight.txt')



for i in range(0,len(test_data)):
            
            # acquire skeleton (FICTIONAL FROM PREVIOUS DATA)
            
            skel_num = test_data[i:i+1]
            
            if not acquired_first_skel:
                first_skel = skel_num
                df_first = pd.DataFrame(first_skel, index = motive_indices) 
            
                acquired_first_skel = True
            
            df = pd.DataFrame(skel_num, index = motive_indices)        
            
            # remove unused columns
            
            df = df[my_cols]
            
            # compute relative angles
            
            df = relativize_df(df)
            
            # concatenate first and current skel
            df_combined = pd.concat([df_first,df])
            
            # unbias angles
            df_combined = remove_bias_df(df_combined, used_body_parts)
            
            df = df_combined[1:2]
            
            # compute euler angles
            
            df = compute_ea_df(df, used_body_parts)
        
            # normalize
            
            
        
            timesk2 = date_t.now();
            print ('time to process control skeleton =', timesk2 - timeun)

            # send commands to unity (TOBEDONE)