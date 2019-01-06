#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 15:15:44 2019

@author: nickgallagher
"""

import os
os.chdir('/Users/nickgallagher/BRISKLESS/scripts')
from s3 import s3_management

# create aws instance
aws_instance = s3_management.briskless_AWS_Management()

# create s3 connection
aws_instance.create_s3_connection()

# show list of buckets
aws_instance.create_bucket_list()

# show list of keys
aws_instance.create_key_list('briskless')

# download csv as df from s3
data = aws_instance.create_df_s3('briskless', 'sample_data.csv')

# upload csv to s3
aws_instance.upload_csv_s3('sample_data.csv', 
                           file_name='/Users/nickgallagher/BRISKLESS/data/sample_data.csv', 
                           _bucket_name='briskless')