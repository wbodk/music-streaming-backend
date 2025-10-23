import json
import boto3
import os
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Update an artist's metadata.
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
                    'message': 'Only admins can update artists'
                })
            }
        
        # Get artist ID from path parameters
        artist_id = event.get('pathParameters', {}).get('artistId')
        
        if not artist_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Missing artist ID'
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
        
        # Check if artist exists
        response = table.get_item(
            Key={
                'pk': f'ARTIST#{artist_id}',
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
                    'message': 'Artist not found'
                })
            }
        
        artist = response['Item']
        
        # Build update expression
        update_expression_parts = []
        expression_attribute_values = {}
        
        # Updateable fields
        updateable_fields = ['name', 'biography', 'profile_image_url', 'genre', 'country']
        
        for field in updateable_fields:
            if field in body:
                update_expression_parts.append(f'{field} = :{field}')
                expression_attribute_values[f':{field}'] = body[field]
        
        if not update_expression_parts:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'No valid fields to update'
                })
            }
        
        # Add updated_at
        timestamp = datetime.utcnow().isoformat()
        update_expression_parts.append('updated_at = :updated_at')
        expression_attribute_values[':updated_at'] = timestamp
        
        # Update the item
        update_expression = 'SET ' + ', '.join(update_expression_parts)
        
        update_response = table.update_item(
            Key={
                'pk': f'ARTIST#{artist_id}',
                'sk': 'METADATA'
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        
        updated_artist = json.loads(json.dumps(update_response['Attributes'], default=str))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Artist updated successfully',
                'artist': updated_artist
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
                'message': 'Error updating artist',
                'error': str(e)
            })
        }
