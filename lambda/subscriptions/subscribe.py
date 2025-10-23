import json
import boto3
import os
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE_NAME'])
db_table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Subscribe a user to an artist.
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
        
        # Verify artist exists
        artist_response = db_table.get_item(
            Key={
                'pk': f'ARTIST#{artist_id}',
                'sk': 'METADATA'
            }
        )
        
        if 'Item' not in artist_response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Artist not found'
                })
            }
        
        artist = artist_response['Item']
        
        # Check if already subscribed
        subscription_response = subscriptions_table.get_item(
            Key={
                'user_id': user_id,
                'artist_id': artist_id
            }
        )
        
        if 'Item' in subscription_response:
            return {
                'statusCode': 409,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'User is already subscribed to this artist'
                })
            }
        
        # Create subscription
        subscription_date = datetime.utcnow().isoformat()
        subscriptions_table.put_item(
            Item={
                'user_id': user_id,
                'artist_id': artist_id,
                'artist_name': artist.get('name', ''),
                'subscription_date': subscription_date,
                'notification_enabled': True
            }
        )
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Successfully subscribed to artist',
                'user_id': user_id,
                'artist_id': artist_id,
                'artist_name': artist.get('name', ''),
                'subscription_date': subscription_date
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
                'error': 'Error creating subscription',
                'message': str(e)
            })
        }
