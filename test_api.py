''' PJones Test_API File
    BH83DQ
    15/06/2021
'''
import requests
import simplejson as json

BASE_URL = "http://127.0.0.1:5000"

# Issue a GET Request to the Homepage
response = requests.get(BASE_URL)
print(response.text) # Check response is as expected
print("Response code: " + str(response.status_code))

response = requests.get(BASE_URL + '/users/all')
print("Showing all users:")
print(response.text)
print("Response code: " + str(response.status_code))

response = requests.get(BASE_URL + '/users/FakeUser')
print("Showing user: FakeUser")
print(response.text)
print("Response code: " + str(response.status_code))

response = requests.get(BASE_URL + '/users/Paul')
print("Showing user: Paul")
print(response.text)
print("Response code: " + str(response.status_code))

response = requests.post(
    BASE_URL + '/users/Bob', {"Employee_ID":"0002", "Forename":"Bob","Surname":"Bloggs", "Email":"bbloggs@dxc.com"})
print(response.text)
print("Response code: " + str(response.status_code))

response = requests.get(BASE_URL + '/users/Bob')
print("Showing user: Bob")
print(response.text)
print("Response code: " + str(response.status_code))

response = requests.delete(BASE_URL + '/users/0002')
print(response.text)
print("Response code: " + str(response.status_code))

response = requests.delete(BASE_URL + '/users/0003')
print(response.text)
print("Response code: " + str(response.status_code))

payload = {"Employee_ID":"0001", "Forename":"Paul","Surname":"Jones", "Email":"pjones98@dxc.com", "BPSS": True}
headers = {"content-type": "application/json"}
response = requests.put(
    BASE_URL + '/users/0001', data=json.dumps(payload),headers=headers)
print(response.text)
print("Response code: " + str(response.status_code))

response = requests.get(BASE_URL + '/file/0001BPSS.docx')
print(response.status_code)
print(response.text)

response = requests.post(BASE_URL + '/file/0001BPSS.docx', {"Employee_ID":"0001", "Forename":"Paul","Surname":"Jones", "Email":"pjones98@dxc.com"})
print("Response code: " + str(response.status_code))
print(response.text)

response = requests.post(BASE_URL + '/securitycheck/0001')
print("Response code: " + str(response.status_code))
print(response.text)

response = requests.post(BASE_URL + '/image/TestPic.jpg')
print("Response code: " + str(response.status_code))
print(response.text)