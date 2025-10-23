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
    Create a new artist.
    Requires admin authorization (checked by API Gateway authorizer).
    """
    try:
        # Verify user is admin
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        
        # Try to get groups from different possible locations
        groups = []
        
        # First try from claims (standard Cognito)
        if 'claims' in authorizer:
            groups = authorizer.get('claims', {}).get('cognito:groups', [])
        
        # If not found, check if groups are at top level
        if not groups and 'cognito:groups' in authorizer:
            groups = authorizer.get('cognito:groups', [])
        
        # Handle case where groups is a string instead of list
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
                    'message': 'Only admins can create artists'
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
        required_fields = ['name']
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
        
        # Generate artist ID
        artist_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare artist item
        artist_item = {
            'pk': f'ARTIST#{artist_id}',
            'sk': 'METADATA',
            'entity_type': 'ARTIST',
            'artist_id': artist_id,
            'name': body['name'],
            'biography': body.get('biography', ''),
            'profile_image_url': body.get('profile_image_url', ''),
            'genre': body.get('genre', ''),
            'country': body.get('country', ''),
            'total_albums': 0,
            'total_songs': 0,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        # Save to DynamoDB
        table.put_item(Item=artist_item)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Artist created successfully',
                'artist': json.loads(json.dumps(artist_item, default=str))
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
                'message': 'Error creating artist',
                'error': str(e)
            })
        }
