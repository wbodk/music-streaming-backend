import json
import boto3
import uuid
import os
import base64
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

def handler(event, context):
    claims = event['requestContext']['authorizer']['claims']
    groups = claims.get('cognito:groups', [])
    
    if 'admin' not in groups:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Forbidden: Admin access required'})
        }

    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        required_fields = ['title', 'artist', 'duration']
        if not all(field in body for field in required_fields):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required fields',
                    'required': required_fields
                })
            }
        
        song_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        table_name = os.environ.get('TABLE_NAME')
        bucket_name = os.environ.get('BUCKET_NAME')
        table = dynamodb.Table(table_name)
        
        s3_key = None
        if 'audio_file' in body:
            try:
                audio_data = base64.b64decode(body['audio_file'])
                file_extension = body.get('file_extension', 'mp3')
                s3_key = f"songs/{song_id}/audio.{file_extension}"
                
                s3.put_object(
                    Bucket=bucket_name,
                    Key=s3_key,
                    Body=audio_data,
                    ContentType=f'audio/{file_extension}',
                    Metadata={
                        'song_id': song_id,
                        'title': body['title'],
                        'artist': body['artist']
                    }
                )
                print(f"Successfully uploaded audio file to s3://{bucket_name}/{s3_key}")
            except Exception as e:
                print(f"Warning: Failed to upload audio file: {str(e)}")
        
        item = {
            'pk': f'SONG#{song_id}',
            'sk': 'METADATA',
            'song_id': song_id,
            'title': body['title'],
            'artist': body['artist'],
            'duration': int(body['duration']),
            'album': body.get('album', ''),
            'genre': body.get('genre', ''),
            'created_at': now,
            'updated_at': now
        }
        
        if s3_key:
            item['s3_key'] = s3_key
            item['audio_url'] = f"s3://{bucket_name}/{s3_key}"
        
        table.put_item(Item=item)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Song created successfully',
                'song': item
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
