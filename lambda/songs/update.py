import json
import boto3
import os
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Update a song's metadata.
    Requires admin authorization (checked by API Gateway authorizer).
    Path parameter: songId
    """
    try:
        # Get song ID from path parameters
        song_id = event['pathParameters']['songId']
        
        if not song_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Song ID is required'
                })
            }
        
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
                    'message': 'Only admins can update songs'
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
        
        # Verify song exists
        response = table.get_item(
            Key={
                'pk': f'SONG#{song_id}',
                'sk': 'METADATA'
            }
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Song not found'
                })
            }
        
        existing_song = response['Item']
        
        # Build update expression
        update_attrs = {}
        expression_parts = []
        
        # Allow updating these fields only
        allowed_fields = ['title', 'artist', 'album', 'genre', 'duration']
        
        for field in allowed_fields:
            if field in body:
                update_attrs[f':{field}'] = body[field]
                expression_parts.append(f'{field} = :{field}')
        
        if not expression_parts:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': f'No valid fields to update. Allowed fields: {", ".join(allowed_fields)}'
                })
            }
        
        # Add updated_at timestamp
        update_attrs[':updated_at'] = datetime.utcnow().isoformat()
        expression_parts.append('updated_at = :updated_at')
        
        update_expression = 'SET ' + ', '.join(expression_parts)
        
        # Update the item
        response = table.update_item(
            Key={
                'pk': f'SONG#{song_id}',
                'sk': 'METADATA'
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=update_attrs,
            ReturnValues='ALL_NEW'
        )
        
        updated_song = response['Attributes']
        song_dict = json.loads(json.dumps(updated_song, default=str))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Song updated successfully',
                'song': song_dict
            })
        }
    
    except KeyError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Song ID is required in path parameters'
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
                'message': 'Error updating song',
                'error': str(e)
            })
        }
