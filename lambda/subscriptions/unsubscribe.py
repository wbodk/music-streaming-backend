import json
import boto3
import os

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE_NAME'])

def handler(event, context):
    """
    Unsubscribe a user from an artist.
    Path parameters: artistId
    User ID is automatically extracted from JWT claims.
    """
    try:
        # Extract user ID from JWT claims
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        user_id = claims.get('sub')  # 'sub' is the user ID in Cognito tokens
        
        # Get artist ID from path parameters
        artist_id = event.get('pathParameters', {}).get('artistId')
        
        if not user_id or not artist_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing artistId or authentication claims'
                })
            }
        
        # Check if subscription exists
        subscription_response = subscriptions_table.get_item(
            Key={
                'user_id': user_id,
                'artist_id': artist_id
            }
        )
        
        if 'Item' not in subscription_response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Subscription not found'
                })
            }
        
        # Delete subscription
        subscriptions_table.delete_item(
            Key={
                'user_id': user_id,
                'artist_id': artist_id
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Successfully unsubscribed from artist',
                'user_id': user_id,
                'artist_id': artist_id
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
                'error': 'Error deleting subscription',
                'message': str(e)
            })
        }
