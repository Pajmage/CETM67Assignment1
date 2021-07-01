import json
import boto3

def lambda_handler(event, context):
        s3 = boto3.client("s3")
        key = event['file_name']
        try:
            s3.delete_object(Bucket='cetm67-sec-documents', Key=key)
            return {"Message":"File Deleted"}, 200
        except Exception as e:
            return{"Message":"File not found",}, 404
