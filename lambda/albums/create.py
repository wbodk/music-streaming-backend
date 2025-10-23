import json
import boto3
import os
import uuid
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Create a new album.
    Requires admin authorization (checked by API Gateway authorizer).
    """
    try:
        # Verify user is admin
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        groups = authorizer.get('claims', {}).get('cognito:groups', [])
        
        if isinstance(groups, str):
            groups = [groups]
        
        if 'admin' not in groups:
            return {
                'statusCode': 403,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Only admins can create albums'
                })
            }
        
        # Parse request body
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Invalid JSON in request body'
                })
            }
        
        # Validate required fields
        required_fields = ['title', 'artist']
        for field in required_fields:
            if field not in body or not body[field]:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'message': f'Missing required field: {field}'
                    })
                }
        
        # Generate album ID
        album_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare album item
        album_item = {
            'pk': f'ALBUM#{album_id}',
            'sk': 'METADATA',
            'album_id': album_id,
            'title': body['title'],
            'artist': body['artist'],
            'release_date': body.get('release_date', ''),
            'genre': body.get('genre', ''),
            'description': body.get('description', ''),
            'cover_image_url': body.get('cover_image_url', ''),
            'total_songs': 0,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        # Save to DynamoDB
        table.put_item(Item=album_item)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Album created successfully',
                'album': json.loads(json.dumps(album_item, default=str))
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Error creating album',
                'error': str(e)
            })
        }
