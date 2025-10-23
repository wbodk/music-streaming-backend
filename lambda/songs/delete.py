import json
import boto3
import os

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
        groups = authorizer.get('claims', {}).get('cognito:groups', [])
        
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
                    'message': 'Only admins can delete songs'
                })
            }
        
        # Get the song to find S3 key
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
