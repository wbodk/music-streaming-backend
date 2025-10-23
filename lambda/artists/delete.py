import json
import boto3
import os
from datetime import datetime

# Initialize DynamoDB and S3
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table(os.environ['TABLE_NAME'])
bucket_name = os.environ.get('BUCKET_NAME')

def handler(event, context):
    """
    Delete an artist.
    Requires admin authorization (checked by API Gateway authorizer).
    """
    try:
        # Verify user is admin
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        
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
        
        if 'admin' not in groups:
            return {
                'statusCode': 403,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Only admins can delete artists'
                })
            }
        
        # Get artist ID from path parameters
        artist_id = event.get('pathParameters', {}).get('artistId')
        
        if not artist_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Missing artist ID'
                })
            }
        
        # Check if artist exists
        response = table.get_item(
            Key={
                'pk': f'ARTIST#{artist_id}',
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
                    'message': 'Artist not found'
                })
            }
        
        # Query all albums by this artist using artist-id-index
        albums_response = table.query(
            IndexName='artist-id-index',
            KeyConditionExpression='artist_id = :artist_id',
            FilterExpression='begins_with(pk, :album_prefix)',
            ExpressionAttributeValues={
                ':artist_id': artist_id,
                ':album_prefix': 'ALBUM#'
            }
        )
        
        albums = albums_response.get('Items', [])
        
        # Delete all songs from all albums of this artist
        for album in albums:
            album_id = album.get('album_id')
            
            # Query all songs in this album
            songs_response = table.query(
                IndexName='album-index',
                KeyConditionExpression='album_id = :album_id',
                ExpressionAttributeValues={
                    ':album_id': album_id
                }
            )
            
            songs = [item for item in songs_response.get('Items', []) if item['pk'].startswith('SONG#')]
            
            # Delete each song and its S3 file
            for song in songs:
                song_id = song.get('song_id')
                s3_key = song.get('s3_key')
                
                # Delete from S3 if key exists
                if s3_key:
                    try:
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
        
        # Delete all albums by this artist
        for album in albums:
            album_id = album.get('album_id')
            table.delete_item(
                Key={
                    'pk': f'ALBUM#{album_id}',
                    'sk': 'METADATA'
                }
            )
        
        # Delete the artist
        table.delete_item(
            Key={
                'pk': f'ARTIST#{artist_id}',
                'sk': 'METADATA'
            }
        )
        
        return {
            'statusCode': 204,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
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
                'message': 'Error deleting artist',
                'error': str(e)
            })
        }
