import json
import boto3
import os
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Delete an album by ID.
    Requires admin authorization (checked by API Gateway authorizer).
    Path parameter: albumId
    """
    try:
        print(f"Delete album event: {json.dumps(event, default=str)}")
        
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
                    'message': 'Only admins can delete albums'
                })
            }
        
        # Verify album exists
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
        artist_id = album.get('artist_id')
        
        # Find all songs in this album using the album-index GSI
        songs_in_album = []
        query_params = {
            'IndexName': 'album-index',
            'KeyConditionExpression': 'album_id = :album_id',
            'ExpressionAttributeValues': {
                ':album_id': album_id
            }
        }
        
        # Query to get all songs in the album
        response_songs = table.query(**query_params)
        songs_in_album = [item for item in response_songs.get('Items', []) if item['pk'].startswith('SONG#')]
        
        # Delete all songs in the album
        for song in songs_in_album:
            song_id = song['song_id']
            s3_key = song.get('s3_key')
            
            # Try to delete from S3 if key exists
            if s3_key:
                try:
                    s3 = boto3.client('s3')
                    bucket_name = os.environ.get('BUCKET_NAME')
                    s3.delete_object(
                        Bucket=bucket_name,
                        Key=s3_key
                    )
                    print(f"Deleted S3 object: {s3_key}")
                except Exception as s3_error:
                    print(f"Warning: Error deleting S3 object: {str(s3_error)}")
            
            # Delete song from DynamoDB
            table.delete_item(
                Key={
                    'pk': f'SONG#{song_id}',
                    'sk': 'METADATA'
                }
            )
        
        # Delete the album from DynamoDB
        table.delete_item(
            Key={
                'pk': f'ALBUM#{album_id}',
                'sk': 'METADATA'
            }
        )
        
        # Update artist counters
        if artist_id:
            try:
                # Decrement total_albums by 1
                # Decrement total_songs by number of songs in album
                table.update_item(
                    Key={
                        'pk': f'ARTIST#{artist_id}',
                        'sk': 'METADATA'
                    },
                    UpdateExpression='SET total_albums = if_not_exists(total_albums, :one) - :one, total_songs = if_not_exists(total_songs, :songs) - :song_count, updated_at = :now',
                    ExpressionAttributeValues={
                        ':one': 1,
                        ':songs': len(songs_in_album),
                        ':song_count': len(songs_in_album),
                        ':now': datetime.utcnow().isoformat()
                    }
                )
            except Exception as update_error:
                print(f"Warning: Failed to update artist counters: {str(update_error)}")
        
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
                'message': 'Error deleting album',
                'error': str(e)
            })
        }
