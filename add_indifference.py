# Script used to iterate over preference lists already generated and pushed to s3 and upload versions with indifference added.
# This was run by ec2 instances.

import boto3
import SuperStableMatchingInstance
import generate_prefs_with_indifference
import random
import math
from itertools import repeat
import os
import sys
import time
from multiprocessing import Pool
from generate_prefs_with_indifference import add_indifference_iteratively
import json
import make_results
core_count = os.cpu_count()

session = boto3.Session(
    aws_access_key_id='lorem_ipsum',
    aws_secret_access_key='lorem_ipsum',
    region_name='us-east-1'
)
def add_indifference(filename, n, k, count, indiff, done, path):
    new_file = f"{n}_{k}_{count}_ind:{indiff}"
    new_path = f'{path}/prefs/{new_file}'
    if new_path not in done:

        bucket_name = "lambda-test5"
        s3 = session.resource('s3')
        obj = s3.Object(bucket_name, filename)
        instances = json.loads(obj.get()['Body'].read())
        for i in range(len(instances)):
            add_indifference_iteratively(instances[i], indiff, i, k, len(instances[i]))
        encoded_results = str(instances).encode("utf-8")

        s3.Bucket(bucket_name).put_object(Key=new_path, Body=encoded_results)
    else:
        print('prefs exist')
    make_results.get_results(n, k, count, indiff, new_path, done, path)



if __name__ == "__main__":
    n, k, count, path = sys.argv[1:]
    s3 = session.resource('s3')
    my_bucket = s3.Bucket("lambda-test5")
    keys = [ob.key for ob in my_bucket.objects.all() if ob.key.startswith(f'{path}/prefs/{n}_{k}_100')]
    done_keys = [ob.key for ob in my_bucket.objects.all() if ob.key.startswith(f'{path}/')]

    for ind in range(90, 100, 1):
        print(ind)
        start = time.time()
        add_indifference(keys[0], int(n),int(k), 100, float(ind)/100, done_keys, path)
        print(time.time() - start)
    # for key in keys:
    #     info = key.split('/')[-1]
    #     n, k, count, time = info.split('_')
    #     add_indifference(key, int(n),int(k), int(count), 0.95, ind_keys)
    # for key in keys:
    #     info = key.split('/')[-1]
    #     n, k, count, time = info.split('_')
    #     add_indifference(key, int(n),int(k), int(count), 0.94, ind_keys)
    # for key in keys:
    #     info = key.split('/')[-1]
    #     n, k, count, time = info.split('_')
    #     add_indifference(key, int(n),int(k), int(count), 0.93, ind_keys)
    # for key in keys:
    #     info = key.split('/')[-1]
    #     n, k, count, time = info.split('_')
    #     add_indifference(key, int(n),int(k), int(count), 0.92, ind_keys)
    # for key in keys:
    #     info = key.split('/')[-1]
    #     n, k, count, time = info.split('_')
    #     add_indifference(key, int(n),int(k), int(count), 0.91, ind_keys)
    # for key in keys:
    #     info = key.split('/')[-1]
    #     n, k, count, time = info.split('_')
    #     add_indifference(key, int(n),int(k), int(count), 0.9, ind_keys)
