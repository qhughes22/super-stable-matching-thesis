# Script to spin up an AWS EC2 instance and run whatever work needed to be run.

import boto3
session = boto3.Session(
    aws_access_key_id='lorem_ipsum',
    aws_secret_access_key='lorem_ipsum',
    region_name='us-east-1'
)

ec2 = session.resource('ec2')
conn = ec2.create_instances(InstanceType="c6g.8xlarge",
                         MaxCount=1,
                         MinCount=1,
                         ImageId="ami-0b6539181920009de",
                            UserData = f'''#!/bin/bash
yum -y install git
# git clone https://github.com/NThakur20/beir-ColBERT.git
pip3 install networkx
pip3 install numpy
pip3 install matplotlib
pip3 install boto3
pip3 install pandas
git clone https://quincy2112:lorem_ipsum@github.com/quincy2112/StableMarriage.git
# cd /StableMarriage
python3 250n.py
# python3 generate_and_upload_tiered.py 
# python3 add_indifference.py 90 100
# for N in 100
# do
    # python3 generate_and_upload.py $N 5 100 "m"
    # python3 add_indifference.py 100 $K 100 "m"
# done
# python3 generate_tiered_df.py 10 20 25 50
sudo shutdown now -h
''',
                            InstanceInitiatedShutdownBehavior= 'terminate',
                KeyName='test',
                            SecurityGroupIds = ['sg-03d49cb50e2a8c8f0'],
IamInstanceProfile = {
                            'Name': 'ec2-s3'
                     },
TagSpecifications = [
                        {
                            'ResourceType': 'instance',
                            'Tags': [
                                {
                                    'Key': 'k',
                                    'Value': '10 20 25 50'
                                }
                            ]
                        },
                    ])

print(conn, '140 145')
