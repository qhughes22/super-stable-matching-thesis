# Script used to generate k-range preferences and upload them to s3. This was run by AWS EC2 instances.

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
session = boto3.Session(
    aws_access_key_id='lorem_ipsum',
    aws_secret_access_key='lorem_ipsum',
    region_name='us-east-1'
)
core_count = os.cpu_count()
def generate_and_upload(size, k, count, path):
    start = time.time()
    size, k, count = int(size), int(k), int(count)
    file_name = f"{size}_{k}_{count}_ind:1"
    full_path = f'{path}/prefs/{file_name}'
    bucket_name = "lambda-test5"
    s3 = session.resource('s3')
    my_bucket = s3.Bucket("lambda-test5")
    keys = [ob.key for ob in my_bucket.objects.all()]
    if full_path not in keys:
        with Pool(core_count) as p:
            prefs = p.starmap(generate_prefs_with_indifference.generate_k_range_one_side2, zip(repeat(size), repeat(k), range(count)))
        # for seed in range(count):
        #     print(seed)
        #     lists.append(generate_prefs_with_indifference.generate_k_range_one_side2(size, k, seed, num_swaps))


        preftime = time.time() - start
        encoded_prefs = str(prefs).encode("utf-8")
        s3.Bucket(bucket_name).put_object(Key=full_path, Body=encoded_prefs)
    else:
        print('prefs exist')
    full_path = f'{path}/results/{file_name}'

    if full_path not in keys:

        start = time.time()
        pairs = [(prefs[i], prefs[(i+1)%count]) for i in range(count)]
        with Pool(core_count) as p:
            results = p.starmap(SuperStableMatchingInstance.run_example, pairs)
        resulttime = time.time() - start

        encoded_results = str(results).encode("utf-8")
        s3.Bucket(bucket_name).put_object(Key=full_path, Body=encoded_results)
    else:
        print('results exist')

if __name__ == "__main__":
    generate_and_upload(*sys.argv[1:])