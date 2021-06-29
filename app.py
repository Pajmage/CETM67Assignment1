''' PJones API File
    BH83DQ
    15/06/2021
'''

from flask import Flask, request, current_app, Response, jsonify
from flask_restful import Api, Resource, reqparse, abort
from os import environ
import simplejson as json
import requests

#Boto3 Imports.  This is the AWS SDK for Python and must be imported to communicate with AWS services
import boto3
import boto3.exceptions
from boto3.dynamodb.conditions import Key, Attr

BASE_URL = "http://127.0.0.1:5000"

#AWS Resources required by the API
dynamodb = boto3.resource('dynamodb', region_name='eu-west-2', aws_access_key_id="AKIA5T6FDNPSL77LDAEO", aws_secret_access_key="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")
lambdaresize = boto3.client('lambda', region_name='eu-west-2', aws_access_key_id="AKIA5T6FDNPSL77LDAEO", aws_secret_access_key="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")
lambdasecurity = boto3.client('lambda', region_name='eu-west-2', aws_access_key_id="AKIA5T6FDNPSL77LDAEO", aws_secret_access_key="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")
s3 = boto3.client('s3')

app = Flask(__name__) # creates a flask App and stores it as 'app'
api = Api(app) # creates an API interface for the 'app'

parser = reqparse.RequestParser() # Parser for use with dynamodb arguments
# required/mandatory arguments 
parser.add_argument('Employee_ID', type=str, help='Employee ID Number', required=True)
parser.add_argument('Surname', type=str, help='Employees Surname', required=True)
parser.add_argument('Forename', type=str, help='Employees Forename', required=True)
parser.add_argument('Email', type=str, help='Employees DXC Email', required=True)
parser.add_argument('BPSS', type=bool, help='Is the employee BPSS Cleared?', required=False, default=False)
parser.add_argument('SC', type=bool, help='Is the employee SC Cleared?', required=False, default=False)
parser.add_argument('DV', type=bool, help='Is the employee DV Cleared?', required=False, default=False)
parser.add_argument('ProfilePic', type=str, help='Profile Picture', required=False, default="None")
parser.add_argument('BPSSFile', type=str, help='BPSS File address', required=False, default="None")
parser.add_argument('SCFile', type=str, help='SC File address', required=False, default="None")
parser.add_argument('DVFile', type=str, help='DV File address', required=False, default="None")

## Resources ##
# Classes that inherit from Resource to define our resources for the app

class HomeRoute(Resource): # HomeRoute Class to ensure connectivity.  In a real world scenario this would return the login page/homepage for the app.
    def get(self): # GET function to connect to the app and return the route data
        return {"Message":"Welcome to the Homepage"}, 200 


class FileOperation(Resource): # FileOperation class that handles uploading and downloading of the files associated with each employee in the system, i.e. Security Clearance Documentation.
    def get(self, file_name): # GET Function to download the requested file.
        file = file_name
        downloadfilename = "DOWNLOAD_"+file
        try:
            s3.download_file('cetm67-sec-documents', file , downloadfilename)
            return {"Message":"File downloaded"}, 200
        except:
            return {"Message":"File not downloaded"}, 404

    def post(self, file_name):
        file = file_name
        try:
            args = parser.parse_args()
            s3.upload_file(file, 'cetm67-sec-documents', file)
            fileurl = "https://cetm67-sec-documents.s3.eu-west-2.amazonaws.com/"+file
            payload = {"Employee_ID":"0001", "Forename":"Paul","Surname":"Jones", "Email":"pjones98@dxc.com", "BPSSFile":fileurl}
            headers = {"content-type": "application/json"}
            requests.put(BASE_URL+"/users/"+args.get("Employee_ID"), data=json.dumps(payload),headers=headers)
            return {"Message":"File uploaded, user details uploaded"}, 200
        except Exception as e:
            print(e)

    def delete(self, file_name):
        file = file_name
        try:
            s3.delete_object(Bucket='cetm67-sec-documents', Key=file_name)
            return {"Message":"File Deleted"}, 200
        except:
            return{"Message":"File not found, user details not uploaded"}, 404


class UserProfile(Resource): # Class that deals with any requests around user data (CRUD operations)
    def get(self, name_of_user): # GET function to connect to the DynamoDB Table and return the data.
        if name_of_user != "all":
            try:
                TABLE = dynamodb.Table('Employee')
                resp = TABLE.scan(FilterExpression=Attr('Forename').eq(name_of_user))
                items = resp['Items']
                if not items:
                    raise ValueError("Record not found or does not exist!")
                return jsonify(json.dumps(resp['Items']))
            except:
                return {"Error": "Record not found or does not exist!"}, 404
        
        elif name_of_user == "all":
            try:
                TABLE = dynamodb.Table('Employee')
                USERS = TABLE.scan()
                return jsonify(json.dumps(USERS['Items']))
            except:
                return {"Error": "Table not found or does not exist!"}, 404       

    def post(self, name_of_user): # POST Function to add users to the table.
        args = parser.parse_args()        
        try:
            TABLE = dynamodb.Table('Employee')
            TABLE.put_item(
                Item={
                    'Employee_ID': args['Employee_ID'],
                    'Surname': args['Surname'],
                    'Forename': args['Forename'],
                    'Email': args['Email'],
                    'BPSS': args['BPSS'],
                    'SC': args['SC'],
                    'DV': args['DV'],
                    'ProfilePic': args['ProfilePic'],
                    'BPSSFile': args['BPSSFile'], 
                    'DVFile': args['DVFile'],
                    'SCFile': args['SCFile'],
                }
            )
            return {"Message":'New User registered'}, 200
        except Exception as e:
            print("Exception is: ")
            print (e)

    def delete(self, name_of_user): # DELETE Function to delete users from the table.
        try:
            TABLE = dynamodb.Table('Employee')
            key = {
                'Employee_ID' : name_of_user
            }
            resp = TABLE.scan(FilterExpression=Attr('Employee_ID').eq(name_of_user))
            items = resp['Items']
            if not items:
                raise ValueError()
            TABLE.delete_item(
                Key=key,)           
            return {"Message":"Record " + name_of_user + " Deleted"}, 200
        except ValueError as er:
            return {"Message":"Record " + name_of_user + " Not found or does not exist!"}, 404
            
    def put(self, name_of_user): # PUT function to Update a Employee
        data = request.get_json()
        args = parser.parse_args()
        datakey = {
                'Employee_ID' : name_of_user
            }
        try:
            TABLE = dynamodb.Table('Employee')
            update_expression = ["set "]
            update_values = {}
            for key, val in data.items():
                if key == "Employee_ID":
                    continue
                else:
                    update_expression.append(f" {key} = :{key},")
                    update_values[f":{key}"] = val
            expression = "".join(update_expression)[:-1]
            TABLE.update_item(
                Key = datakey,
                ExpressionAttributeValues = update_values,
                UpdateExpression = expression
            )
            return {"Message":"User Details Updated"}, 200
        except Exception as e:
            print("Exception is: ")
            print (e)
            return {"Message":"Error: Record NOT updated"}, 404


class ImageResize(Resource): # Class that deals with any requests around resizing files stored in S3 buckets
    def post(self, file_name): # POST function to send the Employee_ID to the Lambda function. 
        print(file_name)
        try:
            payload = {"pic":file_name}
            result = lambdasecurity.invoke(FunctionName='resizeProfilePic', InvocationType='RequestResponse', Payload=json.dumps(payload))
            range = result['Payload'].read()      
            api_response = json.loads(range)               
            return {"Message":api_response}, 200
        except:
            return {"Message":"No lambda function found!"}, 404


class SecurityCheck(Resource): # Class that deals with the SecurityCheck Lambda file to check if a user can work on secure accounts
    def post(self, name_of_user): # POST function to send the Employee_ID to the Lambda function. 
        try:
            payload = {"Employee_ID":name_of_user}
            result = lambdasecurity.invoke(FunctionName='secureAccountCheck', InvocationType='RequestResponse', Payload=json.dumps(payload))
            range = result['Payload'].read()      
            api_response = json.loads(range)               
            print(api_response)
            return {"Message":api_response}, 200
        except:
            return {"Message":"No lambda function found!"}, 404

## API Routing ##
api.add_resource(HomeRoute, '/')
api.add_resource(UserProfile, '/users/<string:name_of_user>')
api.add_resource(FileOperation, '/file/<string:file_name>')
api.add_resource(SecurityCheck, '/securitycheck/<string:name_of_user>')
api.add_resource(ImageResize, '/image/<string:file_name>')

if __name__ == "__main__":
    app.run(debug=True)