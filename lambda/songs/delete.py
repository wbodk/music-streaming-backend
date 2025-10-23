import json
import boto3
import os
from datetime import datetime

# Initialize DynamoDB and S3
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table(os.environ['TABLE_NAME'])
bucket_name = os.environ['BUCKET_NAME']

def handler(event, context):
    """
    Delete a song by ID.
    Requires admin authorization (checked by API Gateway authorizer).
    Path parameter: songId
    """
    try:
        print(f"Delete song event: {json.dumps(event, default=str)}")
        
        # Get song ID from path parameters
        song_id = event['pathParameters']['songId']
        
        if not song_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Song ID is required'
                })
            }
        
        # Verify user is admin
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        print(f"Authorizer context: {json.dumps(authorizer, default=str)}")
        
        # Try to get groups from different possible locations
        groups = []
        
        # First try from claims (standard Cognito)
        if 'claims' in authorizer:
            groups = authorizer.get('claims', {}).get('cognito:groups', [])
        
        # If not found, check if groups are at top level
        if not groups and 'cognito:groups' in authorizer:
            groups = authorizer.get('cognito:groups', [])
        
        # Handle case where groups is a string instead of list
        if isinstance(groups, str):
            groups = [groups]
        
        print(f"User groups: {groups}")
        
        if 'admin' not in groups:
            return {
                'statusCode': 403,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Only admins can delete songs'
                })
            }
        
        # Get the song to find S3 key and album_id
        response = table.get_item(
            Key={
                'pk': f'SONG#{song_id}',
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
                    'message': 'Song not found'
                })
            }
        
        song = response['Item']
        s3_key = song.get('s3_key')
        album_id = song.get('album_id')
        
        # Delete from S3 if key exists
        if s3_key:
            try:
                s3.delete_object(
                    Bucket=bucket_name,
                    Key=s3_key
                )
                print(f"Deleted S3 object: {s3_key}")
            except Exception as s3_error:
                print(f"Error deleting S3 object: {str(s3_error)}")
                # Don't fail if S3 deletion fails, still delete from DB
        
        # Delete from DynamoDB
        table.delete_item(
            Key={
                'pk': f'SONG#{song_id}',
                'sk': 'METADATA'
            }
        )
        
        # Decrement album total_songs counter if song belonged to an album
        if album_id:
            try:
                table.update_item(
                    Key={
                        'pk': f'ALBUM#{album_id}',
                        'sk': 'METADATA'
                    },
                    UpdateExpression='SET total_songs = if_not_exists(total_songs, :one) - :dec, updated_at = :now',
                    ExpressionAttributeValues={
                        ':one': 1,
                        ':dec': 1,
                        ':now': datetime.utcnow().isoformat()
                    }
                )
            except Exception as update_error:
                print(f"Warning: Failed to decrement album counter: {str(update_error)}")
        
        # Decrement artist total_songs counter
        artist_id = song.get('artist_id')
        if artist_id:
            try:
                table.update_item(
                    Key={
                        'pk': f'ARTIST#{artist_id}',
                        'sk': 'METADATA'
                    },
                    UpdateExpression='SET total_songs = if_not_exists(total_songs, :one) - :dec, updated_at = :now',
                    ExpressionAttributeValues={
                        ':one': 1,
                        ':dec': 1,
                        ':now': datetime.utcnow().isoformat()
                    }
                )
            except Exception as update_error:
                print(f"Warning: Failed to decrement artist counter: {str(update_error)}")
        
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
                'message': 'Song ID is required in path parameters'
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
                'message': 'Error deleting song',
                'error': str(e)
            })
        }
