import json
import boto3
import os
import hmac
import hashlib
import base64
from botocore.exceptions import ClientError

cognito = boto3.client('cognito-idp')

# CORS headers that must be included in every response
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Credentials': 'true'
}

def get_secret_hash(username, client_id, client_secret):
    """Generate SECRET_HASH for Cognito API calls when client has a secret"""
    message = bytes(username + client_id, 'utf-8')
    secret = bytes(client_secret, 'utf-8')
    dig = hmac.new(secret, msg=message, digestmod=hashlib.sha256).digest()
    return base64.b64encode(dig).decode()

def handler(event, context):
    """
    Login handler - authenticates user and returns tokens.
    
    Request body:
    {
        "username": "user@example.com",
        "password": "Password123!"
    }
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        username = body.get('username')
        password = body.get('password')        
        user_pool_id = os.environ.get('USER_POOL_ID')
        client_id = os.environ.get('CLIENT_ID')
        
        if not username or not password:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'username and password are required'})
            }
        
        # Get client secret if available
        client_secret = os.environ.get('CLIENT_SECRET')
        auth_params = {
            'USERNAME': username,
            'PASSWORD': password
        }
        
        # Add SECRET_HASH if client has a secret
        if client_secret:
            auth_params['SECRET_HASH'] = get_secret_hash(username, client_id, client_secret)
        
        # Authenticate user
        response = cognito.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters=auth_params
        )
          # Extract tokens
        auth_result = response.get('AuthenticationResult', {})
        
        return {
            'statusCode': 200,
            'headers': {
                **CORS_HEADERS,
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Login successful',
                'access_token': auth_result.get('AccessToken'),
                'id_token': auth_result.get('IdToken'),
                'refresh_token': auth_result.get('RefreshToken'),
                'expires_in': auth_result.get('ExpiresIn'),
                'token_type': auth_result.get('TokenType', 'Bearer')            })
        }
    
    except cognito.exceptions.NotAuthorizedException:
        return {
            'statusCode': 401,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Invalid username or password'})
        }
    except cognito.exceptions.UserNotFoundException:
        return {
            'statusCode': 401,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'User does not exist'})
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UserNotConfirmedException':
            return {
                'statusCode': 403,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'User account is not confirmed'})
            }
        elif error_code == 'PasswordResetRequiredException':
            return {
                'statusCode': 403,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Password reset is required'})
            }
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
