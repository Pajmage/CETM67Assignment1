''' PJones Test_API File
    BH83DQ
    30/06/2021
    Test API script for Microservice 2 - File Management Service (Upload, Download and Delete with S3)
'''
import requests
import simplejson as json
import base64

BASE_URL = "https://limitless-beyond-11781.herokuapp.com/"
#BASE_URL = "http://127.0.0.1:5000"

# Issue a POST request to upload a file
with open("0001BPSS.docx", "rb") as f: # opens the file in the same directory as the ms2_test.py file
    file_bytes = base64.b64encode(f.read()) # encodes the file to a binary filetype
payload = {"name": "0001BPSS.docx","bucket" : "cetm67-sec-documents", "file": file_bytes.decode("utf-8"),"Employee_ID":"0001", "Forename":"Paul","Surname":"Jones", "Email":"pjones98@dxc.com"} # construct the payload to send to the API call, including the encoded file
response = requests.post(BASE_URL + "/file/0001BPSS.docx", data = json.dumps(payload), headers = {'Content-type': 'application/json'})
print(response.status_code)
print(response.text)

# Issue a GET request to the API to download the supplied filename
response = requests.get(BASE_URL + "/file/0001BPSS.docx")
rawfiledata = response.json() # dump the contents of the response json into a variable
filedata = base64.b64decode(rawfiledata["body"]) # pull out the encoded binary file from the response and decode it back into its correct type
filename = "DOWNLOAD_0001BPSS.docx" # set the filename to store the downloaded file as
with open(filename, "wb") as f: # open the file now stored in the variable
    f.write(filedata) # write the file to the users computer using the set filename
print(response.status_code)
print(response.text)

print("Press any key to continue test and delete the uploaded file")
input()

# Issue a DELETE request to the API to delete the identified file
response = requests.delete(BASE_URL + "/file/0001BPSS.docx")
print(response.status_code)
print(response.text)