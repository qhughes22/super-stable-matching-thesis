# Script used to generate tiered preferences and upload them to s3. This was run by AWS EC2 instances.


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
core_count = max(int(os.cpu_count()/2),1)
def generate_and_upload(size, tiers, count):
    start = time.time()
    size, count = int(size), int(count)
    file_name = f"/{size}_{str(tiers)}_{count}"
    bucket_name = "lambda-test5"
    s3 = boto3.resource("s3")
    # s3.Bucket(bucket_name).put_object(Key=file_name)
    with Pool(core_count) as p:
        prefs = p.starmap(generate_prefs_with_indifference.generate_tiered_prefs, zip(repeat(size), repeat(tiers), range(count)))
    # for seed in range(count):
    #     print(seed)
    #     lists.append(generate_prefs_with_indifference.generate_k_range_one_side2(size, k, seed, num_swaps))

    print(tiers)
    preftime = time.time() - start
    encoded_prefs = str(prefs).encode("utf-8")
    s3.Bucket(bucket_name).put_object(Key=f'big/prefs/tiered/{file_name}', Body=encoded_prefs)
    print(preftime)
    start = time.time()
    pairs = [(prefs[i], prefs[(i+1)%count]) for i in range(count)]
    with Pool(core_count) as p:
        results = p.starmap(SuperStableMatchingInstance.run_example, pairs)
    resulttime = time.time() - start
    print(resulttime)

    encoded_results = str(results).encode("utf-8")
    s3.Bucket(bucket_name).put_object(Key=f'big/results/tiered/{file_name}', Body=encoded_results)


if __name__ == "__main__":
    generate_and_upload(100, [100], 100)

