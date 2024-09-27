import boto3
import time
from flask import Flask , request , render_template
import pandas as pd


##AWS access key , security key and region 
AWS_ACCESS_KEY_ID = "AKIAXWMA6OEDHA7RVAW2"
AWS_SECRET_ACCESS_KEY = "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"
REGION = 'us-east-1'
flag=False

# Initialize Boto3 EC2 client
ec2 = boto3.resource('ec2', region_name = REGION, 
                         aws_access_key_id = AWS_ACCESS_KEY_ID,
                         aws_secret_access_key = AWS_SECRET_ACCESS_KEY
                        )

ec2_client = boto3.client('ec2', region_name = REGION, 
                         aws_access_key_id = AWS_ACCESS_KEY_ID,
                         aws_secret_access_key = AWS_SECRET_ACCESS_KEY
                        )

def create_ec2_instance(ec2): # creating ec2 instance 
    instance = ec2.create_instances(
        ImageId = "ami-0e86e20dae9224db8", #got 22.04 ubuntu version ami id from aws console 
        InstanceType = 't2.micro', #selected micro instance type under free tier
        KeyName = 'vaibhavi_kundle_project2', #gave key-pair name by creating it on aws console 
        MinCount = 1,   #to create only one and one instance 
        MaxCount = 1,
        SecurityGroupIds=['sg-0bfea859c00abe1ec'],
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'web-instance'}]
        }]
    )
    instance_id = instance[0].id
    print(f"EC2 Instance Created: {instance_id}")
    return instance_id

def allocate_elastic_ip(instance_id):
    allocation = ec2_client.allocate_address(Domain = 'vpc')
    elastic_ip = allocation['PublicIp']
    allocation_id = allocation['AllocationId']

    ec2_client.associate_address(InstanceId = instance_id, AllocationId = allocation_id)
    print(f"Instance id {instance_id} has elastic ip {elastic_ip}")
    return elastic_ip

if __name__ == '__main__':
    if flag==False:
        instance_id = create_ec2_instance(ec2)
        flag=True
    time.sleep(60)
    elastic_ip = allocate_elastic_ip(instance_id)
    
    print(f"EC2 instance {instance_id} running with elastic ip {elastic_ip}")


app = Flask(__name__)

# Load CSV data into a pandas DataFrame
image_data = pd.read_csv('Classification Results on Face Dataset (1000 images).csv')


@app.route('/', methods=['POST'])
def image_find():
    if request.method == 'POST':

        input_file = request.files['inputFile']
        if not input_file:
            return "No File Availanle",400
    
        if not input_file.filename:
            return "No File selected",400
        
        image = input_file.filename[:-4]

        if image in image_data['Image'].values:
            ##output = image_data[image_data['Image'] == image].Results.iloc[0]
            output = image_data.loc[image_data['Image']== image , 'Results'].values[0]  
            return f"{image}:{output}"
        else:
            return "Image name not found in CSV",400
        
    
    
if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0',port= 8000)


