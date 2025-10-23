from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_cognito as cognito
)
from constructs import Construct

class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, db: dynamodb.TableV2, music_bucket: s3.Bucket, user_pool: cognito.UserPool, user_pool_client: cognito.UserPoolClient, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create Song Handler
        self.create_song_handler = lambda_.Function(
            self,
            "CreateSongHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda/create_song"),
            environment={
                "TABLE_NAME": db.table_name,
                "BUCKET_NAME": music_bucket.bucket_name
            }
        )

        db.grant_write_data(self.create_song_handler)
        music_bucket.grant_put(self.create_song_handler)
        music_bucket.grant_read(self.create_song_handler)
        
        # Login Handler
        self.login_handler = lambda_.Function(
            self,
            "LoginHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="login.handler",
            code=lambda_.Code.from_asset("lambda/auth_handler"),
            environment={
                "USER_POOL_ID": user_pool.user_pool_id,
                "CLIENT_ID": user_pool_client.user_pool_client_id,
                "CLIENT_SECRET": user_pool_client.user_pool_client_secret.unsafe_unwrap()
            }
        )
        
        # Refresh Token Handler
        self.refresh_handler = lambda_.Function(
            self,
            "RefreshHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="refresh.handler",
            code=lambda_.Code.from_asset("lambda/auth_handler"),
            environment={
                "CLIENT_ID": user_pool_client.user_pool_client_id
            }
        )
        
        # Register Handler
        self.register_handler = lambda_.Function(
            self,
            "RegisterHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="register.handler",
            code=lambda_.Code.from_asset("lambda/auth_handler"),
            environment={
                "USER_POOL_ID": user_pool.user_pool_id,
                "CLIENT_ID": user_pool_client.user_pool_client_id,
                "CLIENT_SECRET": user_pool_client.user_pool_client_secret.unsafe_unwrap()
            }
        )
        
        # Confirm Registration Handler
        self.confirm_handler = lambda_.Function(
            self,
            "ConfirmHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="confirm.handler",
            code=lambda_.Code.from_asset("lambda/auth_handler"),
            environment={
                "CLIENT_ID": user_pool_client.user_pool_client_id,
                "CLIENT_SECRET": user_pool_client.user_pool_client_secret.unsafe_unwrap()
            }
        )
        
        # Grant Cognito permissions to auth handlers
        user_pool.grant(self.login_handler, "cognito-idp:AdminInitiateAuth")
        user_pool.grant(self.refresh_handler, "cognito-idp:InitiateAuth")
        user_pool.grant(self.register_handler, "cognito-idp:SignUp")
        user_pool.grant(self.confirm_handler, "cognito-idp:ConfirmSignUp")
 