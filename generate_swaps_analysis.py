# Script used to generate the graphs in the final paper analyzing the swapping method of generating k-range preferences.

import boto3
import json
from collections import defaultdict
from matplotlib import pyplot as plt
session = boto3.Session(
    aws_access_key_id='lorem_ipsum',
    aws_secret_access_key='lorem_ipsum',
    region_name='us-east-1'
)
def get_prefs(path, size, k, iterations, ind):
    filename = f'prefs/{size}_{k}_{iterations}_ind:{ind}'
    bucket_name = "lambda-test5"
    s3 = session.resource('s3')
    obj = s3.Object(bucket_name, f'{path}{filename}')
    instances = json.loads(obj.get()['Body'].read())
    count = [0.] * size
    locdict = defaultdict(int)

    for l in instances:
        for sub in range(len(l)):
            for i in range(size):
                count[l[sub][i][0]] += i
                locdict[(l[sub][i][0], i)] += 1


    for i in range(size):
        count[i] = count[i] / iterations / size
    print(count)
    # fig = plt.figure()

    plt.bar(range(100), count, 1, align='center')
    # ax = fig.add_axes([0, 10, 0, 10])
    # ax.bar(range(10),count)
    plt.ylim([0, 100])
    plt.title(f'k={k}')
    plt.xlabel(f'Index')
    plt.ylabel(f'Average Value')
    plt.savefig(f'plots/swaps/swapsdistr{size}-{k}.png')
    plt.clf()

if __name__ == "__main__":
    for k in range(20, 101, 20):
        get_prefs('m/', 100, k, 100, 1)