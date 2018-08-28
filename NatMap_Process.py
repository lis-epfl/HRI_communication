#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  8 17:39:39 2018

@author: matteomacchini
"""

import matplotlib.pyplot as plt
import os
import pandas as pd

subject_name = 'pilot1'

file_list = os.listdir()

data_pd = []

for i in range(len(file_list)):
    if subject_name in file_list[i]:

        data_pd.append(pd.read_csv(file_list[i]))
