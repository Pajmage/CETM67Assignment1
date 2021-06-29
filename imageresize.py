import datetime
import json
import os
from io import BytesIO
import boto3
import PIL
from PIL import Image


s3 = boto3.resource('s3')
#key = event['pic']
key = "TestPic.jpg"
print(key)
obj = s3.Object(bucket_name="cetm67-profile-pic",key=key,)
obj_body = obj.get()['Body'].read()

img = Image.open(BytesIO(obj_body))
img.show()
img = img.resize((100, 100))
buffer = BytesIO()
img.save(buffer, 'JPEG')
buffer.seek(0)

resized_key="Thumbnail" + str(key)
obj = s3.Object(bucket_name="cetm67-profile-pic", key=resized_key,)
obj.put(Body=buffer, ContentType='image/jpeg')
response = "https://cetm67-profile-pic.s3.eu-west-2.amazonaws.com/"+resized_key
print(response)
#return response