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
    Registration handler - allows users to sign up.
    
    Request body:
    {
        "username": "user@example.com",
        "password": "Password123!",
        "email": "user@example.com",
        "given_name": "John",
        "family_name": "Doe",
        "birthdate": "1990-01-15"
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
        email = body.get('email')
        given_name = body.get('given_name')
        family_name = body.get('family_name')
        birthdate = body.get('birthdate')
        
        user_pool_id = os.environ.get('USER_POOL_ID')
        
        # Validate required fields
        required_fields = ['username', 'password', 'email', 'given_name', 'family_name', 'birthdate']
        missing_fields = [field for field in required_fields if not body.get(field)]
        
        if missing_fields:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required fields',
                    'required': required_fields,
                    'missing': missing_fields
                })
            }
        
        # Get client secret if available
        client_secret = os.environ.get('CLIENT_SECRET')
        sign_up_params = {
            'ClientId': os.environ.get('CLIENT_ID'),
            'Username': username,
            'Password': password,
            'UserAttributes': [
                {'Name': 'email', 'Value': email},
                {'Name': 'given_name', 'Value': given_name},
                {'Name': 'family_name', 'Value': family_name},
                {'Name': 'birthdate', 'Value': birthdate}
            ]
        }
        
        # Add SECRET_HASH if client has a secret
        if client_secret:
            sign_up_params['SecretHash'] = get_secret_hash(username, os.environ.get('CLIENT_ID'), client_secret)
        
        # Sign up user
        response = cognito.sign_up(**sign_up_params)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Registration successful! Please check your email to confirm your account.',
                'user_sub': response.get('UserSub'),
                'username': username,
                'email': email
            })
        }
    
    except cognito.exceptions.UsernameExistsException:
        return {
            'statusCode': 409,
            'body': json.dumps({'error': 'Username already exists'})
        }
    except cognito.exceptions.InvalidPasswordException as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Invalid password',
                'message': str(e)
            })
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'UserLambdaValidationException':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Validation failed: ' + str(e)})
            }
        elif error_code == 'InvalidParameterException':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid parameter: ' + str(e)})
            }
        
        print(f"Cognito error: {error_code} - {str(e)}")
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
