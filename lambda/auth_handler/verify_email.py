import json
import boto3
import os

# Initialize Cognito client
cognito = boto3.client('cognito-idp')

def handler(event, context):
    """
    Diagnostic endpoint to check JWT claims and email availability.
    GET /auth/verify-email
    
    Helps troubleshoot if email is present in JWT tokens.
    """
    try:
        # Extract claims from authorizer
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        claims = authorizer.get('claims', {})
        
        # Check what we got
        email = claims.get('email')
        user_id = claims.get('sub')
        username = claims.get('cognito:username')
        
        if not email:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Email not found in JWT claims',
                    'debug_info': {
                        'user_id': user_id,
                        'username': username,
                        'available_claims': list(claims.keys()),
                        'solution': 'Email must be configured in Cognito User Pool read attributes'
                    }
                })
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Email verified successfully',
                'email': email,
                'user_id': user_id,
                'username': username,
                'all_claims': claims
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
                'error': 'Error checking JWT claims',
                'message': str(e)
            })
        }
