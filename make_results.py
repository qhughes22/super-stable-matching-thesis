# Script used to get preferences from s3 and run through stable matching algorithms, pushing the results back to s3.

import boto3
import SuperStableMatchingInstance
import generate_prefs_with_indifference
import random
import math
from itertools import repeat
import os
import sys
import time
import json
from multiprocessing import Pool
session = boto3.Session(
    aws_access_key_id='lorem_ipsum',
    aws_secret_access_key='lorem_ipsum',
    region_name='us-east-1'
)
core_count = os.cpu_count()

def get_results(n, k, count, indiff, pref_file, done, path):
    # n, k, count, _ = pref_file.split('_')
    new_file = f"{n}_{k}_{count}_ind:{indiff}"

    new_path = f'{path}/results/{new_file}'

    if new_path in done:
        print('results exist')
        return
    bucket_name = "lambda-test5"
    s3 = session.resource('s3')
    obj = s3.Object(bucket_name, pref_file)
    instances = json.loads(obj.get()['Body'].read())

    start = time.time()
    results = []
    for i in range(len(instances)):
        print(i)
        done = False
        j = (i+1)%len(instances)
        while(not done):
            try:
                results.append(SuperStableMatchingInstance.run_example(instances[i], instances[j]))
                done = True
            except AssertionError:
                j= (j+1)%len(instances)
    # with Pool(int(core_count/2)) as p:
    #
    #     results = p.starmap(SuperStableMatchingInstance.run_example, pairs)
    encoded_results = str(results).encode("utf-8")
    print(time.time() - start)
    s3.Bucket(bucket_name).put_object(Key=new_path, Body=encoded_results)

def get_results_mixed(prefs1, prefs2, done, path):
    n1, k1, count1, indiff1, pref_file1 = prefs1
    n2, k2, count2, indiff2, pref_file2 = prefs1
    assert count1 == count2, "count mismatch" + prefs1 + prefs2

    # n, k, count, _ = pref_file.split('_')
    new_file = f"{n1}_{k1}_{count1}_ind:{indiff1}x{n2}_{k2}_{count2}_ind:{indiff2}"

    new_path = f'{path}/results/mixed/{new_file}'

    if new_path in done:
        print('a')
        return
    bucket_name = "lambda-test5"
    s3 = session.resource('s3')
    obj1 = s3.Object(bucket_name, pref_file1)
    instances1 = json.loads(obj1.get()['Body'].read())
    obj2 = s3.Object(bucket_name, pref_file1)
    instances2 = json.loads(obj2.get()['Body'].read())
    start = time.time()
    pairs = [(instances1[i], instances2[i]) for i in range(count1)]
    results = []
    for i in range(len(instances1)):
        done = False
        j = i
        while (not done):
            try:
                results.append(SuperStableMatchingInstance.run_example(instances1[i], instances2[j]))
                done = True
            except AssertionError:
                j = (j + 1) % len(instances1)
    # with Pool(int(core_count/2)) as p:
    #
    #     results = p.starmap(SuperStableMatchingInstance.run_example, pairs)
    encoded_results = str(results).encode("utf-8")
    print(time.time() - start)
    s3.Bucket(bucket_name).put_object(Key=new_path, Body=encoded_results)
def get_results_against_uniform(n, tiers, count, indiff, pref_file, done, path):

    new_file = f"{n}_{tiers}_{count}_ind:{indiff}x_uni_ind:1"
    uniform = f'{path}/prefs/tiered/100_[100]_100'
    new_path = f'{path}/results/uniform2/{new_file}'

    # if new_path in done:
    #     print('a')
    #     return
    bucket_name = "lambda-test5"
    s3 = session.resource('s3')
    obj = s3.Object(bucket_name, pref_file)
    instances = json.loads(obj.get()['Body'].read())
    obj_uniform = s3.Object(bucket_name, uniform)
    instances_uniform = json.loads(obj_uniform.get()['Body'].read())
    start = time.time()
    results = []
    for i in range(len(instances)):
        done = False
        j = i
        while(not done):
            try:
                a = SuperStableMatchingInstance.run_example(instances[i], instances_uniform[j])
                if a == ([], [], []):
                    print('FAILURE')
                results.append(a)
                print(i, j)
                print(a)
                done = True
            except AssertionError:
                j= (j+1)%len(instances)
    # with Pool(int(core_count/2)) as p:
    #
    #     results = p.starmap(SuperStableMatchingInstance.run_example, pairs)
    encoded_results = str(results).encode("utf-8")
    print(time.time() - start)
    s3.Bucket(bucket_name).put_object(Key=new_path, Body=encoded_results)

if __name__ == "__main__":
    s3 = session.resource('s3')
    my_bucket = s3.Bucket("lambda-test5")
    keys = [ob.key for ob in my_bucket.objects.all() if ob.key.startswith('m/prefs/tiered')]
    result_keys = [ob.key for ob in my_bucket.objects.all() if ob.key.startswith('m/results/')]
    # keys = [k for k in keys if k.startswith('big/prefs/tiered')]
    keys.reverse()
    for key in keys:
        print(key)

        info = key.split('/')[-1]
        n, k, count = info.split('_')
        if k == '[100]':
            get_results_against_uniform(int(n), k, int(count), 1, key, result_keys, 'm')
    # key = 'big/prefs//300_5_100_311.46'
    # info = key.split('/')[-1]
    # n, k, count, _ = info.split('_')
    # get_results(300, 5, 100,1, 'm/prefs/300_5_100_ind:1', result_keys,'m')

