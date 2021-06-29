''' PJones Test_API File
    BH83DQ
    15/06/2021
    Test API script for Microservice 3 - Image resize service (Using a Lambda to resize an image in an S3 bucket)
'''
import requests
import simplejson as json

BASE_URL = "http://127.0.0.1:5000"

response = requests.post(BASE_URL + '/securitycheck/0001')
print("Response code: " + str(response.status_code))
print(response.text)

response = requests.post(BASE_URL + '/image/TestPic.jpg')
print("Response code: " + str(response.status_code))
print(response.text)