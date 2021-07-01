''' PJones Test_API File
    BH83DQ
    30/06/2021
    Test API script for Microservice 4 - User Clearance Level (Using a Lambda to query a DynamoDB to check Security Clearance level)
'''
import requests
import simplejson as json

BASE_URL = "https://limitless-beyond-11781.herokuapp.com/"
#BASE_URL = "http://127.0.0.1:5000"

# Issue a POST request to the API to check the provided users Security Clearance level using a Lambda Function
response = requests.post(BASE_URL + "/securitycheck/0001")
print(response.status_code)
print(response.text)