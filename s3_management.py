#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 14:45:39 2019

@author: nickgallagher
"""
import json
import os
import pandas as pd
import boto
import boto.s3.connection
import boto3


class briskless_AWS_Management:
    '''This class has several utility functions for our S3 bucket
    '''

    
    def __init__(self, json_credentials_filepath =('/Users/nickgallagher/BRISKLESS/s3_credentials.json')):
        
        #this loads in the json credentials
        #this is the same credentials file that hosues the logion
        #informaiton for the CRM 
        with open(json_credentials_filepath,'r') as f:
            self.credentials = json.load(f)
            
        self.conn = None
            
     
    def create_s3_connection(self):
        '''this function creates the s3 connection using the JSON 
        credential that are loaded in at initialization
        '''
        
        ##this creates a connection attribute using the boto3 package
        self.conn = boto.s3.connect_to_region(
                region_name = 'us-east-2',
                aws_access_key_id = self.credentials['BRISKLESS']['AWS_Credentials']['access_key'],
                aws_secret_access_key = self.credentials['BRISKLESS']['AWS_Credentials']['secret_key']
                )
 
       
    def create_bucket_list(self):
        '''this fucntion will create a simple list of all s3 buckets
        '''
        
        #create a connection if one isn't made
        if self.conn == None:
            self.create_s3_connection()
        else:
            pass
        
        ##this creates a bucket
        self.list_of_buckets = [bucket.name for bucket in self.conn.get_all_buckets()]
    
    
        return self.list_of_buckets

    
    def create_key_list(self,
                bucket_name):
        '''this function will create a list of keys in a given bucket
        '''
        
        #create a connection if not already established
        if self.conn == None:
            self.create_s3_connection()
        else:
            pass
        
        #load in the bucket with the given bucket name
        bucket = boto.s3.bucket.Bucket(connection = self.conn,
                                       name = bucket_name)
        
        #set the self.keylist to the list of bucket keys
        self.key_list = [key.name for key in bucket.get_all_keys()]
        
        #return the list of keys in the bucket
        return self.key_list
    
    
    def create_df_s3(self,
                   bucket_name,
                   csv_name,
                   temp_file_path = 'temp_file.csv'):
        
        '''This function loads in a csv from the s3 bucket and returns the dataframe
        the file will be temporarily written to the given temp_file_path
        and then deleted after it is brought back into memeory in a pandas dataframe
        
        '''
        
        #create a connection if one does not already exist
        if self.conn == None:
            self.create_s3_connection()
        else:
            pass
        
        #load the bucket with csv you are looking to load
        bucket = boto.s3.bucket.Bucket(connection = self.conn,
                                       name = bucket_name)
        
        #this loads the file in the bucket--use the key
        key = boto.s3.key.Key(bucket = bucket,
                              name = csv_name)
        
        #create the temp file and write it out
        with open(temp_file_path,'wb') as f:
            key.get_contents_to_file(f)
        
        #read back in the temp file 
        data = pd.read_csv(temp_file_path,
                           sep = ',')
        
        #delte the temp file
        os.remove(temp_file_path)
        
        #return the dataframe
        return data
   
    
    def delete_df_s3(self,csv,
                     bucket_name = 'briskless'):
        '''
        This method will delete an item from our S3 Bucket
        '''
        
        #create connection if there was none
        if self.conn == None:
            self.create_s3_connection()
        else:
            pass
        
        #create an instance of the bucket
        bucket = boto.s3.bucket.Bucket(connection = self.conn,
                                       name = bucket_name)
        
        #delete the file from the bucket
        bucket.delete_key(csv)
        
        print('The file {} was deleted from {}'.format(csv,
                                                       bucket_name))
    
        
    def upload_csv_s3(self,
                         key_name,
                         file_name,
                         _bucket_name = 'briskless'):
        
        '''This function will upload a dataframe that is stored on the hard 
        drive onto the S3 Bucket
        '''
        #create an instance of the boto3 client
        s3 = boto3.client('s3',
                          aws_access_key_id = self.credentials['BRISKLESS']['AWS_Credentials']['access_key'],
                          aws_secret_access_key = self.credentials['BRISKLESS']['AWS_Credentials']['secret_key']
                          )
            
        #use the boto3 client upload method 
        s3.upload_file(file_name,_bucket_name,key_name)
        print('{} uploaded successfully to {}'.format(file_name,key_name))
                 



