import json
import boto3
import os

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Delete an album by ID.
    Requires admin authorization (checked by API Gateway authorizer).
    Path parameter: albumId
    """
    try:
        # Get album ID from path parameters
        album_id = event['pathParameters']['albumId']
        
        if not album_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Album ID is required'
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
                    'message': 'Only admins can delete albums'
                })
            }
        
        # Verify album exists
        response = table.get_item(
            Key={
                'pk': f'ALBUM#{album_id}',
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
                    'message': 'Album not found'
                })
            }
        
        # Delete from DynamoDB
        table.delete_item(
            Key={
                'pk': f'ALBUM#{album_id}',
                'sk': 'METADATA'
            }
        )
        
        return {
            'statusCode': 204,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
    
    except KeyError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Album ID is required in path parameters'
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
                'message': 'Error deleting album',
                'error': str(e)
            })
        }
