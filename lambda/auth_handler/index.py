import json
import boto3
import os
from botocore.exceptions import ClientError

cognito = boto3.client('cognito-idp')

def handler(event, context):
    """
    Authentication handler for login and token refresh.
    Supports both login and token refresh operations.
    
    Request body:
    {
        "operation": "login",  # or "refresh"
        "username": "user@example.com",
        "password": "Password123!",
        "refresh_token": "<token>"  # only needed for refresh operation
    }
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        operation = body.get('operation', 'login')
        user_pool_id = os.environ.get('USER_POOL_ID')
        client_id = os.environ.get('CLIENT_ID')
        
        if operation == 'login':
            return handle_login(body, user_pool_id, client_id)
        elif operation == 'refresh':
            return handle_refresh(body, client_id)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid operation. Use "login" or "refresh"'})
            }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def handle_login(body, user_pool_id, client_id):
    """Handle user login"""
    try:
        username = body.get('username')
        password = body.get('password')
        
        if not username or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'username and password are required'})
            }
        
        # Authenticate user
        response = cognito.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        # Extract tokens
        auth_result = response.get('AuthenticationResult', {})
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Login successful',
                'access_token': auth_result.get('AccessToken'),
                'id_token': auth_result.get('IdToken'),
                'refresh_token': auth_result.get('RefreshToken'),
                'expires_in': auth_result.get('ExpiresIn'),
                'token_type': auth_result.get('TokenType', 'Bearer')
            })
        }
    
    except cognito.exceptions.NotAuthorizedException:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Invalid username or password'})
        }
    except cognito.exceptions.UserNotFoundException:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'User does not exist'})
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UserNotConfirmedException':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'User account is not confirmed'})
            }
        elif error_code == 'PasswordResetRequiredException':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Password reset is required'})
            }
        raise

def handle_refresh(body, client_id):
    """Handle token refresh"""
    try:
        refresh_token = body.get('refresh_token')
        
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
