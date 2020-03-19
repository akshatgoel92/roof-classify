# Import packages
import os 
import json
import boto3
import argparse
import numpy as np
import pandas as pd

    
def make_folder(name = './../Image Folder'):

    try:
        os.makedirs(name)
    except Exception as e:
        print(e)
        pass


def make_folders(source, root = "Image Folder",):
    
    make_folder('./' + root)
    make_folder(source) 


def get_paths(root, image_type, image_name):
    
    path = './' + root + '/' + image_type + '/'
    image_path = path + image_name
    
    return(path, image_path)


def get_paths_old(destination, root = "Image Folder"):
    
    source = "./" + root + '/' + destination
    pre = root + '/' + destination
    
    return(source, pre)


def get_credentials():
    
    with open('./secrets.json') as secrets:
        s3_access = json.load(secrets)['s3']
        
    return(s3_access['default_bucket'], 
           s3_access['access_key_id'],
           s3_access['secret_access_key'])


def get_s3_client():

    _, access_key_id, secret_access_key = get_credentials()
    s3 = boto3.client("s3", 
                      aws_access_key_id = access_key_id, 
                      aws_secret_access_key = secret_access_key)
    return(s3)


def get_s3_resource():

    _, access_key_id, secret_access_key = get_credentials()
    s3 = boto3.resource('s3', 
                        aws_access_key_id = access_key_id, 
                        aws_secret_access_key = secret_access_key)
    return(s3)


def get_bucket_name():
    
    bucket_name, _, _ = get_credentials()
    return(bucket_name)

    
def get_matching_s3_objects(prefix="", suffix=""):
    """
    Generate objects in an S3 bucket.
    :param prefix: Only fetch objects whose key starts with this prefix (optional).
    :param suffix: Only fetch objects whose keys end with this suffix (optional).
    Taken from: https://alexwlchan.net/2019/07/listing-s3-keys/
    Copyright © 2012–19 Alex Chan. Prose is CC-BY licensed, code is MIT.
    """
    s3 = get_s3_client()
    kwargs = {'Bucket': get_bucket_name()} 
    paginator = s3.get_paginator("list_objects_v2")
       	
    if isinstance(prefix, str): 
        prefixes = (prefix, )
    else: 
        prefixes = prefix
    
    for key_prefix in prefixes: 
        kwargs["Prefix"] = key_prefix
        
        for page in paginator.paginate(**kwargs):
            try: contents = page["Contents"]
            except Exception as e: print(e) 
            
            for obj in contents:
                key = obj["Key"]
                if key.endswith(suffix):
                    yield obj
    
    
def get_matching_s3_keys(prefix="", suffix=""):
    """
    Generate the keys in an S3 bucket.
    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    Taken from: https://alexwlchan.net/2019/07/listing-s3-keys/
    Copyright © 2012–19 Alex Chan. Prose is CC-BY licensed, code is MIT.
    """
    for obj in get_matching_s3_objects(prefix, suffix): 
        yield obj["Key"]


def get_object_s3(key):
    
    s3 = get_s3_client()
    bucket_name = get_bucket_name()
    f = s3.get_object(bucket_name, key)["Body"]
    
    return(f)
    
        
def download_s3(file_from = 'Raw Data/NRSC_Raw/198124711/ACC_REP.txt',
                file_to = './test.txt'):
    
    s3 = get_s3_resource()
    bucket_name = get_bucket_name()
    try:
        s3.Bucket(bucket_name).download_file(file_from, file_to)
    except Exception as e: 
        print(e)


def upload_s3(file_from = './test.txt', 
              file_to = 'Raw Data/NRSC_Raw/198124711/test.txt' ):
    
    s3 = get_s3_client()
    bucket_name = get_bucket_name()
    s3.upload_file(file_from, bucket_name, file_to)