import json
import boto3
import os

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE_NAME'])

def handler(event, context):
    """
    Unsubscribe a user from an artist.
    Path parameters: userId, artistId
    """
    try:
        # Get user ID and artist ID from path parameters
        user_id = event.get('pathParameters', {}).get('userId')
        artist_id = event.get('pathParameters', {}).get('artistId')
        
        if not user_id or not artist_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing userId or artistId'
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
