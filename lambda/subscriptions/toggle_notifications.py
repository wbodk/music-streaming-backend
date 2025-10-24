import json
import boto3
import os

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE_NAME'])

def handler(event, context):
    """
    Toggle notification preferences for a user's subscription to an artist.
    Path parameters: artistId
    User ID is automatically extracted from JWT claims.
    Request body: { "notification_enabled": true/false }
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
        
        # Get notification preference from request body
        try:
            if isinstance(event.get('body'), str):
                body = json.loads(event['body'])
            else:
                body = event.get('body', {})
        except:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid request body'
                })
            }
        
        notification_enabled = body.get('notification_enabled')
        
        if notification_enabled is None:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing notification_enabled field'
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
        
        # Update notification preference
        subscriptions_table.update_item(
            Key={
                'user_id': user_id,
                'artist_id': artist_id
            },
            UpdateExpression='SET notification_enabled = :notification_enabled',
            ExpressionAttributeValues={
                ':notification_enabled': bool(notification_enabled)
            }
        )
        
        status = "enabled" if notification_enabled else "disabled"
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Notifications {status}',
                'user_id': user_id,
                'artist_id': artist_id,
                'notification_enabled': bool(notification_enabled)
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
                'error': 'Error updating notification preferences',
                'message': str(e)
            })
        }
