#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 20:06:53 2018

@author: matteomacchini
"""

from Glue_code import *

os.chdir('../HRI_Mapping')

from Mapping import *

    
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


##################       SETTINGS       ##################


mode = Mode_enum(3)

filename = date_t.now().strftime("%Y_%b_%d_%I_%M_%S%p")
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


if mode.name=='control':

    sett.N_READS = math.inf

    sett.READ_MOTIVE_SK = 1

    sett.READ_QUERY_FROM_UNITY = 1

    sett.WRITE_SK_TO_UNITY = 1

    sett.OPEN_CLOSE_CONTINUOUS = 1

    sett.DUMMY_READ = False


SUBJECTS = {'MatteoM' : 'pilot1', 'StefanoM' : 'pilot2', 'DavideZ' : 'pilot3'}

subject = SUBJECTS['DavideZ']

###################       IMPORT DATA      ###################

regressor_filename = subject + '_best_mapping'
parameters_filename = subject + '_PARAM' + '.txt'


##################      IMPLEMENTATION      ##################

regressor_filename = subject + '_best_mapping'
parameters_filename = subject + '_PARAM' + '.txt'

if mode.name=='control':
    data_folder = '/Users/matteomacchini/Google Drive/Matteo/EPFL/LIS/PhD/Natural_Mapping/DATA/acquired_data/'
    interface_folder = data_folder + 'interfaces/'
    # load interface to file
    best_mapping = load_obj(interface_folder + regressor_filename)
    parameters = pd.read_csv(data_folder + parameters_filename)
    

start = date_t.now()

# define data structure and headers

        
motive_indices = np.array([])

motive_indices_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w' , 'roll' , 'pitch' , 'yaw' ])

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


used_str = ['_' + str(x) for x in used_body_parts]
my_cols = [col for col in motive_indices if any(y in col for y in used_str)]

acquired_first_skel = False

input_data = 'angles'

outputs = ['roll', 'pitch']

# select features

if input_data == 'all':
    feats = [col for col in my_cols if '_' in col]
elif input_data == 'angles':
    feats = [col for col in my_cols if 'quat' in col or 'roll_' in col or 'pitch_' in col or 'yaw_' in col]
elif input_data == 'euler':
    feats = [col for col in my_cols if 'roll_' in col or 'pitch_' in col or 'yaw_' in col]
elif input_data == 'quaternions':
    feats = [col for col in my_cols if 'quat' in col]
    
###################        TEST        ###################

test_data = pd.read_csv(data_folder + 'pilot3_inst_1_2018_Jun_22_06_53_03PM_roll_straight.txt')

in_data = test_data.iloc[:,:231]

out_data = test_data.iloc[:,231:]


y_score_all = []


for i in list(parameters):
    parameters[i][1] = 1/parameters[i][1]

for i in range(0,len(test_data)):
#for i in range(0,20):
            
    # acquire skeleton (EXAMPLE FROM PREVIOUS DATA)
    
    timeun = date_t.now();
    
    skel_num = in_data[i:i+1].values
    
    if not acquired_first_skel:
        first_skel = skel_num
        df_first = pd.DataFrame(first_skel, columns = motive_indices) 
        # remove unused columns
        
        df_first = df_first[my_cols]
        
        # compute relative angles
        
        df_first = relativize_df(df_first)
    
        acquired_first_skel = True
    
    df = pd.DataFrame(skel_num, columns = motive_indices)        
    
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
    
    
    start = time.clock()

    # normalize
    
    for j in list(df):
        # do not normalize quaternion components and outputs
        if 'pitch_' in j or 'roll_' in j or 'yaw_' in j :
#            [array_norm, norm_param_t] = normalize(df[j], parameters[j])
#            df[j] = array_norm
            
            df[j][0] -= parameters[j][0]
            df[j][0] *= parameters[j][1]
           
    end = time.clock()
    print("time to process control skeleton = " + str(end-start))
    


    # send commands to unity (TOBEDONE)