"""
Optional presigned URL generator for S3 files.
This can be used to create secure download links that expire after a certain time.

Usage:
1. Create a new API endpoint that calls this function
2. Pass the song_id as a parameter
3. Receive a presigned URL that can be used for direct S3 downloads
"""

import boto3
import json
import os
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def generate_presigned_url_handler(event, context):
    """
    Generates a presigned URL for downloading a song from S3.
    
    Expected event body:
    {
        "song_id": "<song-id>",
        "expiration_seconds": 3600  # optional, default 1 hour
    }
    """
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        if 'song_id' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'song_id is required'})
            }
        
        song_id = body['song_id']
        expiration = int(body.get('expiration_seconds', 3600))  # Default 1 hour
        bucket_name = os.environ.get('BUCKET_NAME')
        
        s3_prefix = f"songs/{song_id}/"
        
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)
        
        if 'Contents' not in response or len(response['Contents']) == 0:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Song file not found in S3'})
            }
        
        s3_key = response['Contents'][0]['Key']
        
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=expiration
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'presigned_url': presigned_url,
                'expires_in_seconds': expiration,
                's3_key': s3_key
            })
        }
    
    except ClientError as e:
        print(f"AWS Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to generate download URL',
                'message': str(e)
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
