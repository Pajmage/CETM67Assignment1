''' PJones API File
    BH83DQ
    30/06/2021
'''
# Library imports as required for the application and API calls
from flask import Flask, request, current_app, Response, jsonify
from flask_restful import Api, Resource, reqparse, abort
from os import environ
import simplejson as json
import base64
import requests

#Boto3 Imports.  This is the AWS SDK for Python and must be imported to communicate with AWS services
import boto3
import boto3.exceptions
from boto3.dynamodb.conditions import Key, Attr

#BASE_URL = "https://limitless-beyond-11781.herokuapp.com/"
BASE_URL = "http://127.0.0.1:5000"

#AWS Resources required by the API
dynamodb = boto3.resource('dynamodb', region_name='eu-west-2', aws_access_key_id="", aws_secret_access_key="")
lambdaresize = boto3.client('lambda', region_name='eu-west-2', aws_access_key_id="", aws_secret_access_key="")
lambdasecurity = boto3.client('lambda', region_name='eu-west-2', aws_access_key_id="", aws_secret_access_key="")
s3 = boto3.client('s3', region_name='eu-west-2', aws_access_key_id="", aws_secret_access_key="")

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
        try:
            response = s3.get_object(Bucket='cetm67-sec-documents', Key=file,) # collect the object from the S3 bucket and store its contents in the response variable
            download_file = response['Body'].read() # get the body of the response (which is the file) and store it in the variable
            filereturn = base64.b64encode(download_file).decode('utf-8') # encode the file into a binary format for passing to the users computer
            return { # return the below information in JSON Format
            'headers': { "Content-Type": "application/json" },
            'statusCode': 200,
            'body': json.dumps(filereturn),
            'isBase64Encoded': True,
            "File Downloaded": "File Downloaded successfully"
            }
        except Exception as e:
            return str(e)
    
    def post(self, file_name):
        file = file_name
        try:
            data = request.get_json()
            file_content = base64.b64decode(data['file']) # Get the file from the payload and decode it from binary back into its file type
            response = s3.put_object(Bucket='cetm67-sec-documents', Key=data['name'], Body=file_content) # Take the decoded file and put it in the bucket with the supplied name from the payload
            fileurl = "https://cetm67-sec-documents.s3.eu-west-2.amazonaws.com/"+file # set the file URL into a variable for use calling the CRUD API
            payload = {"Employee_ID":"0001", "Forename":"Paul","Surname":"Jones", "Email":"pjones98@dxc.com", "BPSSFile":fileurl}
            headers = {"content-type": "application/json"}
            requests.put(BASE_URL+"/users/"+data["Employee_ID"], data=json.dumps(payload),headers=headers) # call the 1st Microservices functions, specifically the Update function to update the user details
            return {"Message":"File uploaded, user details uploaded",}, 200
        except Exception as e:
            print(e)

    def delete(self, file_name):
        file = file_name
        try:
            #s3.delete_object(Bucket='cetm67-sec-documents', Key=file)
            payload = {"file_name":file} # set a payload to send to the lambda function consisting of the name of the file to be deleted
            result = lambdasecurity.invoke(FunctionName='deleteObject', InvocationType='RequestResponse', Payload=json.dumps(payload)) # call the deleteObject Lambda passing the name of the file to it
            range = result['Payload'].read() # read the return from the Lambda     
            api_response = json.loads(range)               
            return {"Message":api_response}, 200
            return {"Message":"File Deleted"}, 200
        except Exception as e:
            return{"Message":"File not found", "file": str(file), "e":str(e)}, 404


class UserProfile(Resource): # Class that deals with any requests around user data (CRUD operations)
    def get(self, name_of_user): # GET function to connect to the DynamoDB Table and return the data.
        if name_of_user != "all": # will trigger if a username is passed to the function
            try:
                TABLE = dynamodb.Table('Employee')
                resp = TABLE.scan(FilterExpression=Attr('Forename').eq(name_of_user)) # scans through the table looking for the record with the supplied value and store that record in a variable
                items = resp['Items'] # take the data of the record and store it in a variable, no headers etc.
                if not items: # if the variable is empty return an error
                    raise ValueError("Record not found or does not exist!")
                return jsonify(json.dumps(resp['Items'])) # return the record details
            except:
                return {"Error": "Record not found or does not exist!"}, 404
        
        elif name_of_user == "all": # if all data from the table is requested
            try:
                TABLE = dynamodb.Table('Employee')
                USERS = TABLE.scan() # store the contents of the table in a variable
                return jsonify(json.dumps(USERS['Items'])) # return the data inside that variable
            except:
                return {"Error": "Table not found or does not exist!"}, 404       

    def post(self, name_of_user): # POST Function to add users to the table.
        args = parser.parse_args() # store the contents of the supplied arguments in a variable
        try:
            TABLE = dynamodb.Table('Employee') # set the table the record will be added to
            TABLE.put_item( # add a new item to the table
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
            TABLE = dynamodb.Table('Employee') # set the table the record will be deleted from
            key = {
                'Employee_ID' : name_of_user # set the key required by the delete_item function to the passed Employee_ID
            }
            resp = TABLE.scan(FilterExpression=Attr('Employee_ID').eq(name_of_user)) # search the table for the supplied user
            items = resp['Items']
            if not items: # if the user is not found, raise an error
                raise ValueError()
            TABLE.delete_item( # selete the item with primary key passed to the function
                Key=key,)           
            return {"Message":"Record " + name_of_user + " Deleted"}, 200
        except ValueError as er:
            return {"Message":"Record " + name_of_user + " Not found or does not exist!"}, 404
            
    def put(self, name_of_user): # PUT function to Update a Employee
        data = request.get_json() # collect the information sent in the payload
        args = parser.parse_args()
        datakey = {
                'Employee_ID' : name_of_user # set the key for the update_item function
            }
        try:
            TABLE = dynamodb.Table('Employee')
            update_expression = ["set "]
            update_values = {}
            for key, val in data.items():
                if key == "Employee_ID":
                    continue
                else:
                    update_expression.append(f" {key} = :{key},") # Build the update JSON expression by adding each of the passed arguments from the payload, one at a time until they are all added
                    update_values[f":{key}"] = val
            expression = "".join(update_expression)[:-1]
            TABLE.update_item( # update the selected record with the values supplied in the UpdateExpression
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
            payload = {"Employee_ID":name_of_user} # set the payload to send to the Lambda, this will be same as the 
            result = lambdasecurity.invoke(FunctionName='secureAccountCheck', InvocationType='RequestResponse', Payload=json.dumps(payload)) # call the lambda function and store the returned response in a variable
            range = result['Payload'].read() # read the return from the Lambda         
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