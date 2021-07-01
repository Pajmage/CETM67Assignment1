''' PJones Test_API File
    BH83DQ
    30/06/2021
    Test API script for Microservice 1 - User Registration and Maintenance (CRUD to a DynamoDB)
'''
import requests
import simplejson as json

BASE_URL = "https://limitless-beyond-11781.herokuapp.com/"
#BASE_URL = "http://127.0.0.1:5000"

# Issue a GET Request to the Homepage
response = requests.get(BASE_URL)
print(response.status_code)
print(response.text) # Check response is as expected

# Issue a GET request to display all users in the database
response = requests.get(BASE_URL + '/users/all')
print(response.status_code)
print(response.text)

# Issue a GET request to display specific user from the database, with a user that does not exist
response = requests.get(BASE_URL + '/users/FakeUser')
print(response.status_code)
print(response.text)

# Issue a GET request to display specific user from the database, with a user that does exist
response = requests.get(BASE_URL + '/users/Paul')
print(response.status_code)
print(response.text)

# Issue a POST request to add the supplied user to the DynamoDB table
response = requests.post(
    BASE_URL + '/users/Bob', {"Employee_ID":"0002", "Forename":"Bob","Surname":"Bloggs", "Email":"bbloggs@dxc.com"})
print(response.status_code)
print(response.text)

print("Press any key to continue test and delete the added record")
input()

# Issue a DELETE request to the table to delete the supplied user, using a user that exists in the table
response = requests.delete(BASE_URL + '/users/0002')
print(response.status_code)
print(response.text)

# Issue a DELETE request to the table to delete the supplied user, using a user that does not exist in the table
response = requests.delete(BASE_URL + '/users/0003')
print(response.status_code)
print(response.text)

# Issue a PUT request to update the provided user details, in this case, changing BPSS clearance to True from False
payload = {"Employee_ID":"0001", "Forename":"Paul","Surname":"Jones", "Email":"pjones98@dxc.com", "BPSS": True} # construct the payload to send to the API call, including the encoded file
headers = {"content-type": "application/json"}
response = requests.put(
    BASE_URL + '/users/0001', data=json.dumps(payload),headers=headers)
print(response.status_code)
print(response.text)