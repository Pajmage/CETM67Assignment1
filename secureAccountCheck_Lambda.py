import boto3
import boto3.exceptions
from boto3.dynamodb.conditions import Key, Attr
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    TABLE = dynamodb.Table('Employee')
    resp = TABLE.scan(FilterExpression=Attr('Employee_ID').eq('0001'))
    items = resp['Items']
    bpss = items[0]['BPSS']
    sc = items[0]['SC']
    dv = items[0]['DV']
    clearancelevel = 0
    projectlevel = ""
    
    if bpss == True:
        clearancelevel = clearancelevel + 1
    if sc == True:
        clearancelevel = clearancelevel + 2
    if dv == True:
        clearancelevel = clearancelevel + 5
    
    
    if clearancelevel == 1:
        projectlevel = "User " + items[0]['Employee_ID'] + " is cleared for BPSS accounts only"
    elif clearancelevel == 3:
        projectlevel = "User " + items[0]['Employee_ID'] + " is cleared for BPSS and SC accounts only"
    elif clearancelevel == 8:
        projectlevel = "User " + items[0]['Employee_ID'] + " is cleared for all accounts"
    else:
        projectlevel = "User " + items[0]['Employee_ID'] + " is not cleared for secure accounts"
    
    return projectlevel
    
    