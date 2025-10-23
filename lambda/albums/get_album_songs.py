import json
import boto3
import os

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Get all songs in an album by album ID.
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
        
        # First, verify the album exists
        album_response = table.get_item(
            Key={
                'pk': f'ALBUM#{album_id}',
                'sk': 'METADATA'
            }
        )
        
        if 'Item' not in album_response:
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
        
        album = album_response['Item']
        
        # Query for all songs with this album ID
        scan_params = {
            'FilterExpression': 'album = :album_id',
            'ExpressionAttributeValues': {
                ':album_id': album_id
            }
        }
        
        response = table.scan(**scan_params)
        
        # Convert Decimal to float for JSON serialization
        items = []
        for item in response.get('Items', []):
            item_dict = json.loads(json.dumps(item, default=str))
            items.append(item_dict)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Album songs retrieved successfully',
                'album': json.loads(json.dumps(album, default=str)),
                'songs_count': len(items),
                'songs': items
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
                'message': 'Error retrieving album songs',
                'error': str(e)
            })
        }
