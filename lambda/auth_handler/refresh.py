import json
import boto3
import os
from botocore.exceptions import ClientError

cognito = boto3.client('cognito-idp')

def handler(event, context):
    """
    Refresh token handler - refreshes expired access tokens.
    
    Request body:
    {
        "refresh_token": "<refresh_token>"
    }
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        refresh_token = body.get('refresh_token')
        client_id = os.environ.get('CLIENT_ID')
        
        if not refresh_token:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'refresh_token is required'})
            }
        
        # Refresh tokens
        response = cognito.initiate_auth(
            ClientId=client_id,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token
            }
        )
        
        auth_result = response.get('AuthenticationResult', {})
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Token refreshed successfully',
                'access_token': auth_result.get('AccessToken'),
                'id_token': auth_result.get('IdToken'),
                'expires_in': auth_result.get('ExpiresIn'),
                'token_type': auth_result.get('TokenType', 'Bearer')
            })
        }
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NotAuthorizedException':
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid or expired refresh token'})
            }
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
