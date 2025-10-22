import json
import boto3
import uuid
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')

def handler(event, context):
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
        table = dynamodb.Table(table_name)
        
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
