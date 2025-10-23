import json
import boto3
import os
import hmac
import hashlib
import base64
from botocore.exceptions import ClientError

cognito = boto3.client('cognito-idp')

def get_secret_hash(username, client_id, client_secret):
    """Generate SECRET_HASH for Cognito API calls when client has a secret"""
    message = bytes(username + client_id, 'utf-8')
    secret = bytes(client_secret, 'utf-8')
    dig = hmac.new(secret, msg=message, digestmod=hashlib.sha256).digest()
    return base64.b64encode(dig).decode()

def handler(event, context):
    """
    Confirm registration handler - confirms user email after sign up.
    
    Request body:
    {
        "username": "user@example.com",
        "confirmation_code": "123456"
    }
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        username = body.get('username')
        confirmation_code = body.get('confirmation_code')
        client_id = os.environ.get('CLIENT_ID')
        
        if not username or not confirmation_code:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'username and confirmation_code are required'})
            }
        
        # Get client secret if available
        client_secret = os.environ.get('CLIENT_SECRET')
        confirm_params = {
            'ClientId': client_id,
            'Username': username,
            'ConfirmationCode': confirmation_code
        }
        
        # Add SECRET_HASH if client has a secret
        if client_secret:
            confirm_params['SecretHash'] = get_secret_hash(username, client_id, client_secret)
        
        # Confirm sign up
        cognito.confirm_sign_up(**confirm_params)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Email confirmed successfully! You can now log in.',
                'username': username
            })
        }
    
    except cognito.exceptions.ExpiredCodeException:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Confirmation code has expired. Please request a new one.'})
        }
    except cognito.exceptions.CodeMismatchException:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid confirmation code'})
        }
    except cognito.exceptions.UserNotFoundException:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'User not found'})
        }
    except cognito.exceptions.NotAuthorizedException as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'User is already confirmed or error: {str(e)}'})
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"Cognito error: {error_code} - {error_msg}")
        
        # Return more detailed error info for debugging
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': f'Confirmation failed: {error_msg}',
                'error_code': error_code
            })
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
