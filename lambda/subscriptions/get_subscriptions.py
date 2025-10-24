import json
import boto3
import os

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE_NAME'])

def handler(event, context):
    """
    Get all artist subscriptions for a user.
    No path parameters needed.
    User ID is automatically extracted from JWT claims.
    Query parameters: limit, last_key (for pagination)
    """
    try:
        # Extract user ID from JWT claims
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        user_id = claims.get('sub')  # 'sub' is the user ID in Cognito tokens
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Authentication required'
                })
            }
        
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
        
        # Query subscriptions by user ID
        query_params = {
            'KeyConditionExpression': 'user_id = :user_id',
            'ExpressionAttributeValues': {
                ':user_id': user_id
            },
            'Limit': limit
        }
        
        if exclusive_start_key:
            query_params['ExclusiveStartKey'] = exclusive_start_key
        
        response = subscriptions_table.query(**query_params)
        
        # Convert Decimal to string for JSON serialization
        subscriptions = []
        for item in response.get('Items', []):
            item_dict = json.loads(json.dumps(item, default=str))
            subscriptions.append(item_dict)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Subscriptions retrieved successfully',
                'user_id': user_id,
                'count': len(subscriptions),
                'subscriptions': subscriptions,
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
                'error': 'Error retrieving subscriptions',
                'message': str(e)
            })
        }
