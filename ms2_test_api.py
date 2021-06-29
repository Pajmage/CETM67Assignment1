''' PJones Test_API File
    BH83DQ
    15/06/2021
    Test API script for Microservice 2 - File Management Service (Upload, Download and Delete with S3)
'''
import requests
import simplejson as json

BASE_URL = "https://dry-escarpment-18133.herokuapp.com:5000/"

# Issue a POST request to the API to upload the provided file
response = requests.post(BASE_URL + '/file/0001BPSS.docx', {"Employee_ID":"0001", "Forename":"Paul","Surname":"Jones", "Email":"pjones98@dxc.com"})
print(response.status_code)
print(response.text)

# Issue a GET request to the API to download the supplied filename
response = requests.get(BASE_URL + '/file/0001BPSS.docx')
print(response.status_code)
print(response.text)

print("Press any key to continue test and delete the uploaded file")
input()

# Issue a DELETE request to the API to delete the identified file
response = requests.delete(BASE_URL + '/file/0001BPSS.docx')
print(response.status_code)
print(response.text)