#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 17:46:13 2018

@author: matteomacchini
"""


#####################################################

import numpy as np
import quaternion_operations as quat_op

from HRI_communication_add import *

#####################################################

class skeleton():
    
    
    ### INIT FUNCTION ###
    

    def __init__(self, values):
        
        self.values = values
    
        self.settings = HRI_communication_settings()
    
        self.settings.quat_loc = 4
        self.settings.quat_len = 4
    
    
    ### PRIVATE FUNCTIONS ###
    

    def _quat_idx(self):
        
        return range(self.settings.quat_loc, self.settings.quat_loc + self.settings.quat_len)


    def keep_used_body_parts(self, parts = None):
        
        if parts is None:
            parts = self.settings.used_body_parts
        
        a = self._search_bone_per_index(parts)
                
        self.values = self.values[a,:]
    
    
    def keep_features(self, feats):
        
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
                
        self.values = self.values[:,mask]
        
    def relativize_skeleton(self):
        
        self._relativize_bone(9, 8)
        self._relativize_bone(8, 7)
        self._relativize_bone(7, 6)
        self._relativize_bone(6, 3)
        self._relativize_bone(13, 12)
        self._relativize_bone(12, 11)
        self._relativize_bone(11, 10)
        self._relativize_bone(10, 3)
        
    
    def _values_to_quaternion(self, quat_val):
        
        quat = np.quaternion(quat_val[3], quat_val[0], quat_val[1], quat_val[2])
        
        return quat
    
    def _quaternion_to_values(self, quat):
        
        quat_val = np.array([quat.x, quat.y, quat.z, quat.w])
        
        return quat_val
        
    def unbias_skeleton(self, first_skel):
        
        for i in range(np.size(self.values, 0)):
            bias_quat = self.values[i,:][self._quat_idx()]
            ref_quat = first_skel.values[i,:][self._quat_idx()]
            
#            print ('biased = ',  bias_quat, ', ref = ', ref_quat)
            
            #unbias
            self.values[i][self._quat_idx()] = self._quaternion_to_values(self._values_to_quaternion(bias_quat)/self._values_to_quaternion(ref_quat))
        
    def _search_bone_per_index(self, idx):
        
        arr = self.values[:,0]
        
        i = np.where(idx==arr[:,None])[0]
    
        return i
    
    
    def compute_ea(self):
        
        def compute_ea_bone(a, str):
            # compute eul
            
            quat_val = a[self._quat_idx()]
            
            eul = quat_op.Q2EA((quat_val[3], quat_val[0], quat_val[1], quat_val[2]), EulerOrder="zyx", ignoreAllChk=True)[0]
            
#            print(eul)
            
            # right order [xzy] : due to Motive settings
            return np.array([eul[2], eul[0], eul[1]])
    
    
        # pre-allocation
        eul_skel = np.zeros([np.size(self.values, 0), np.size(self.values, 1) + 3])
        
        eul_skel[:, :np.size(self.values, 1)] = self.values
        
        tot_t = 0
        
        eul = np.apply_along_axis(compute_ea_bone, 1, self.values, self)
        
        eul_skel[:,-3:] = eul
            
        self.values = eul_skel
    
    
    def _relativize_bone(self, angles_to_correct, with_respect_to):
        
        ref_idx = self._search_bone_per_index(with_respect_to)
        abs_idx = self._search_bone_per_index(angles_to_correct)
        
        # extract rows
        ref_row = self.values[ref_idx].reshape(-1)
        abs_row = self.values[abs_idx].reshape(-1)
        
        # extract quaternions
        ref_quat = ref_row[self._quat_idx()]
        abs_quat = abs_row[self._quat_idx()]
        
        ref_quat_q = self._values_to_quaternion(ref_quat)
        abs_quat_q = self._values_to_quaternion(abs_quat)
        
        # compute difference
        rel_quat_q = abs_quat_q/ref_quat_q
        
        # stick back in array
        abs_row[self._quat_idx()] = self._quaternion_to_values(rel_quat_q)
        
        self.values[abs_idx] = abs_row
    
    
    def normalize(self, av, std):
        
        self.values = self.values - av
        self.values = self.values / std