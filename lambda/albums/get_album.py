import json
import boto3
import os

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Get a specific album by ID.
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
        
        # Query DynamoDB for the album
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
        
        album = response['Item']
        
        # Convert to proper JSON format
        album_dict = json.loads(json.dumps(album, default=str))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Album retrieved successfully',
                'album': album_dict
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
                'message': 'Error retrieving album',
                'error': str(e)
            })
        }
