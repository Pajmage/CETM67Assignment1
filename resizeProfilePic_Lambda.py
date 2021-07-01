import datetime
import json
import os
from io import BytesIO
import boto3
import PIL
from PIL import Image

def lambda_handler(event, context):
    print(event['pic'])
    
    s3 = boto3.client('s3')
    key = event['pic']
    obj = s3.get_object(Bucket="cetm67-profile-pic",Key=key)
    obj_body = obj['Body'].read()

    img = Image.open(BytesIO(obj_body))
    img = img.resize((100, 100))
    buffer = BytesIO()
    img.save(buffer, 'JPEG')
    buffer.seek(0)

    resized_key="Thumbnail" + str(key)
    s3.put_object(Body=buffer, ContentType='image/jpeg', Bucket="cetm67-profile-pic", Key=resized_key)
        #The 2 below lines of code will work but will not overwrite the file and will throw a timeout error message 
        #obj = s3.Object(bucket_name="cetm67-profile-pic", key=resized_key,)
        #obj.put(Body=buffer, ContentType='image/jpeg')
    response = "https://cetm67-profile-pic.s3.eu-west-2.amazonaws.com/"+resized_key
    
    return response