''' PJones Test_API File
    BH83DQ
    15/06/2021
    Test API script for Microservice 3 - Image resize service (Using a Lambda to resize an image in an S3 bucket)
'''
import requests
import simplejson as json

BASE_URL = "http://127.0.0.1:5000"

# Issue a POST request to the API to resize the provided image from an S3 bucket using a Lambda Function
response = requests.post(BASE_URL + '/image/TestPic.jpg')
print(response.status_code)
print(response.text)