import json
import boto3
import os
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Get all songs from the database.
    Returns a paginated list of songs.
    """
    try:
        # Get query parameters for pagination
        limit = 20  # Default limit
        exclusive_start_key = None
        
        if event.get('queryStringParameters'):
            params = event['queryStringParameters']
            if params and params.get('limit'):
                try:
                    limit = int(params['limit'])
                    if limit > 100:
                        limit = 100  # Max limit of 100
                except ValueError:
                    pass
            
            if params and params.get('last_key'):
                try:
                    exclusive_start_key = json.loads(params['last_key'])
                except json.JSONDecodeError:
                    pass
        
        # Query all songs (those with pk starting with 'SONG#')
        query_params = {
            'IndexName': 'pk_gsi',  # Using GSI for efficient querying
            'KeyConditionExpression': 'pk = :pk',
            'ExpressionAttributeValues': {
                ':pk': 'SONG'
            },
            'Limit': limit
        }
        
        # Fallback to scan if GSI not available
        scan_params = {
            'FilterExpression': 'begins_with(pk, :pk_prefix)',
            'ExpressionAttributeValues': {
                ':pk_prefix': 'SONG'
            },
            'Limit': limit
        }
        
        if exclusive_start_key:
            scan_params['ExclusiveStartKey'] = exclusive_start_key
        
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
                'message': 'Songs retrieved successfully',
                'count': len(items),
                'songs': items,
                'last_key': response.get('LastEvaluatedKey')  # For pagination
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
                'message': 'Error retrieving songs',
                'error': str(e)
            })
        }
