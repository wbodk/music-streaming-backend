import json
import boto3
import os

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Get all albums from the database.
    Returns a paginated list of albums.
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
        
        # Scan for all albums
        scan_params = {
            'FilterExpression': 'begins_with(pk, :pk_prefix)',
            'ExpressionAttributeValues': {
                ':pk_prefix': 'ALBUM'
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
                'message': 'Albums retrieved successfully',
                'count': len(items),
                'albums': items,
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
                'message': 'Error retrieving albums',
                'error': str(e)
            })
        }
