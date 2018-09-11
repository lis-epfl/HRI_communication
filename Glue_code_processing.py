
from Glue_code import *



#########################################################

    
################# OPTITRACK CONVENTIONS #################

def close_all_connections(Read_unity_query, Read_unity_control, Read_unity_info, Read_motive_sk):

    # close unity write socket
    Read_unity_query.socket.close()
    
    # close unity control read socket
    Read_unity_control.socket.close()

    # close unity info read socket
    Read_unity_info.socket.close()
    
    # close motive read socket
    Read_motive_sk.socket.close()

def consume_motive_skeleton(Read_motive_sk):
    # consume skeleton
    skel_data_temp = udp_read(Read_motive_sk)
        
    return skel_data_temp

def get_unity_query(Read_unity_query):

    query = ''
    
    # read query
    query_data = udp_read(Read_unity_query)
    unity_query = udp_process(query_data, Read_unity_query)
         
    print ('UNITY query = ', unity_query)
    
    return unity_query

def acquisition_routine(skel, skel_data, unity_num, Read_unity_control, Read_unity_info):
        
    print('collecting data')

    # read unity calibration data
    udp_data = udp_read(Read_unity_control)
    unity_calib = np.array(udp_process(udp_data, Read_unity_control))
                    
    print('unity_calib = ', unity_calib)
    
    # read unity info
    udp_data = udp_read(Read_unity_info)
    unity_calib_info = np.array(udp_process(udp_data, Read_unity_info))
                    
    print('unity_calib_info = ', unity_calib_info)
    
#        # process skeleton
#        if skel_data_temp == 't':   
#            print ('using old skeleton')
#              use old skel
        
    # save skel_data in list
    if len(skel) == 0:
        skel = [skel_data]
    else:
        skel.append(skel_data)
                     
    
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
            
    return [skel, unity_num]

def control_routine(regress_data_list, count, first_skel, df_first, y_score_all, motive_indices, used_body_parts, N_RB_IN_SKEL, acquired_first_skel, EXAMPLE_DATA = False, in_data = 0, out_data = 0):
    
    # if query : read unity and skeleton, then save to csv
    
    start = time.clock()
        
    # process skel data and add headers
    
    if  EXAMPLE_DATA:
        skel_num = in_data[count:count+1].values
    else:
        skel = skel_data
        skel = udp_process(skel, Read_motive_sk)
        
    if USE_DF_METHOD:
    
        # not converting to df anymore
        df = pd.DataFrame(skel_num, columns = motive_indices)   
            # remove unused columns
            
        df = df[my_cols]
    else:
        skel = np.reshape(skel_num, (N_RB_IN_SKEL,-1))
        
        # used body parts
        skel = skel_keep_used_body_parts(skel, used_body_parts)
    
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

EXAMPLE_DATA = False
USE_DF_METHOD = True


mode = 'acquisition'

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


if mode=='avatar':

    sett.N_READS = 1000
    sett.READ_MOTIVE_SK = 1
    sett.READ_QUERY_FROM_UNITY = 1
    sett.WRITE_SK_TO_UNITY = 1
    sett.OPEN_CLOSE_CONTINUOUS = 1
    sett.DUMMY_READ = False


if mode=='acquisition':

    sett.N_READS = math.inf
    sett.READ_MOTIVE_SK = 1
    sett.READ_QUERY_FROM_UNITY = 1
    sett.WRITE_SK_TO_UNITY = 1
    sett.OPEN_CLOSE_CONTINUOUS = 1
    sett.DUMMY_READ = False


if mode=='control':

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


regressor_filename = subject + '_best_mapping'
parameters_filename = subject + '_PARAM' + '.txt'

if mode=='control':
    data_folder = settings.data_folder
    interface_folder = data_folder + 'interfaces/'
    # load interface to fileaaaa
    best_mapping = load_obj(interface_folder + regressor_filename)
    parameters = pd.read_csv(data_folder + parameters_filename)
    
    
##################      IMPLEMENTATION      ##################


start = date_t.now()


if sett.WRITE_SK_TO_UNITY:
    unity_sk_client = Socket_info()

    unity_sk_client.IP = UDP_sett.IP_UNITY
    unity_sk_client.PORT = UDP_sett.PORT_UNITY_WRITE_SK_CLIENT

count = 0

query = ''

# define data structure and headers

        
motive_indices = np.array([])

motive_indices_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w'])

regression_indices = np.array([])

regression_indices_base = np.char.array([ 'ID', 'pos_x', 'pos_y', 'pos_z', 'quat_x', 'quat_y', 'quat_z', 'quat_w', 'roll', 'pitch', 'yaw'])

for i in range(N_RB_IN_SKEL):

    n = np.char.array([('_' + str(i+1))])

    if i==0:
        motive_indices = motive_indices_base + (n)
        if i+1 in used_body_parts:
            regression_indices = regression_indices_base + (n)
    else:
        motive_indices = np.r_[motive_indices, motive_indices_base + (n)]
        if i+1 in used_body_parts:
            regression_indices = np.r_[regression_indices, regression_indices_base + (n)]


        
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

if not EXAMPLE_DATA:
    skel = []

used_str = ['_' + str(x) for x in used_body_parts]
my_cols = [col for col in motive_indices if any(y in col for y in used_str)]

acquired_first_skel = False

input_data = 'angles'

outputs = ['roll', 'pitch']

# select features

if input_data == 'all':
    feats = [col for col in regression_indices if '_' in col]
elif input_data == 'angles':
    feats = [col for col in regression_indices if 'quat' in col or 'roll_' in col or 'pitch_' in col or 'yaw_' in col]
elif input_data == 'euler':
    feats = [col for col in regression_indices if 'roll_' in col or 'pitch_' in col or 'yaw_' in col]
elif input_data == 'quaternions':
    feats = [col for col in regression_indices if 'quat' in col]
    

#if not EXAMPLE_DATA:
    
# create unity read query / write skeleton socket
Read_unity_query = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_QUERY, 'UNITY_QUERY', timeout = 0.001)
Write_unity_sk = Read_unity_query

# create unity control read socket
Read_unity_control = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_READ_CALIB, 'UNITY_CALIB',  timeout = 0.001)

# create unity info read socket
Read_unity_info = setup(UDP_sett.IP_UNITY, UDP_sett.PORT_UNITY_READ_CALIB_INFO, 'UNITY_INFO',  timeout = 0.001)

# create motive read socket
Read_motive_sk = setup(UDP_sett.IP_MOTIVE, UDP_sett.PORT_MOTIVE, 'MOTIVE_SK',  timeout = 0.001) #1ms to read everything
        
if EXAMPLE_DATA:

    ###################        TEST        ###################
    
    test_data = pd.read_csv(data_folder + 'pilot3_inst_1_2018_Jun_22_06_53_03PM_roll_straight.txt')
    
    in_data = test_data.iloc[:,:231]
    
    out_data = test_data.iloc[:,231:]
    
    col_no_eul = [x for x in in_data if any(y in x for y in motive_indices_base)]
    
    in_data = in_data[col_no_eul]
    
    parameters = parameters.iloc[:,:-2]   
    parameters_val = parameters.values
    
    param_av = parameters_val[0,:].reshape(len(used_body_parts),-1)
    param_std = parameters_val[1,:].reshape(len(used_body_parts),-1)

    # limit loop duration
    
    sett.N_READS = 10 # len(test_data)
#    sett.N_READS = len(test_data)

    # don't wait for query
    unity_query = 'c'
    
    y_score_all = []
    
#    plt.ion()
#    fig = plt.figure()
#    ax1 = fig.add_subplot(211)
#    ax2 = fig.add_subplot(212)
             
    regress_data_list = []
    
    df_first = []
    first_skel = []
    

start_proc = time.clock()    

while count<sett.N_READS:
    if mode=='avatar':

        while count<sett.N_READS:
            # create motive read socket
            # update skeleton
            # close motive read socket
            (skel) = consume_motive_skeleton(Read_motive_sk)

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

    elif mode =='acquisition':
        
        skel_data_temp = consume_motive_skeleton(Read_motive_sk)
        
        if skel_data_temp == 't':
            print ('skel = ', skel_data_temp)
        else:
            print ('skel = full skeleton')
            skel_data = skel_data_temp
    
        unity_query = get_unity_query(Read_unity_query)
        
        unity_query = 'a'
    
        # if query : read unity and skeleton, then save to csv
        if unity_query=='a':
        
            skel_data = 1
            
            [skel, unity_num] = acquisition_routine(skel, skel_data, unity_num, Read_unity_control, Read_unity_info)
        
        elif unity_query=='q':
    
            close_all_connections(Read_unity_query, Read_unity_control, Read_unity_info, Read_motive_sk)
            
            break
        
    if mode == 'control':
        
        if not EXAMPLE_DATA:
        
            skel_data_temp = consume_motive_skeleton(Read_motive_sk)
            
            if skel_data_temp == 't':
                print ('skel = ', skel_data_temp)
            else:
                print ('skel = full skeleton')
                skel_data = skel_data_temp
        
            unity_query = get_unity_query(Read_unity_query)
        
    
        # if query : read unity and skeleton, then save to csv
        if unity_query=='c':
        
            [regress_data_list, acquired_first_skel, first_skel, df_first, y_score_all, debug_info] = control_routine(regress_data_list, count, first_skel, df_first, y_score_all, motive_indices, used_body_parts, N_RB_IN_SKEL, acquired_first_skel, EXAMPLE_DATA, in_data, out_data)
    
        elif unity_query=='q':
    
            close_all_connections(Read_unity_query, Read_unity_control, Read_unity_info, Read_motive_sk)
            
            break
        
            
    count = count + 1
    
end_proc = time.clock()

close_all_connections(Read_unity_query, Read_unity_control, Read_unity_info, Read_motive_sk)

if USE_DF_METHOD:
    meth = 'using pandas'
else:
    meth = 'using numpy'
    
print('')
print('')
print('')
print('')
print('')
print('Total processing time ' + meth + ' (' + str(sett.N_READS) + ' samples) = ' + "{:.3f}".format(end_proc - start_proc) + ' seconds' )
print('')
print('')
print('')
print('')
print('')

if mode == 'acquisition':

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
    
    end = date_t.now()
    print('total time = ', end - start)
    
    #data_pd = pd.read_csv(foldername + '/' + filename + '.txt')