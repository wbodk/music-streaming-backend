from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_cognito as cognito,
    aws_iam as iam
)
from constructs import Construct

class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, db: dynamodb.TableV2, subscriptions_table: dynamodb.TableV2, music_bucket: s3.Bucket, user_pool: cognito.UserPool, user_pool_client: cognito.UserPoolClient, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create Song Handler
        self.create_song_handler = lambda_.Function(
            self,
            "CreateSongHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="create.handler",
            code=lambda_.Code.from_asset("lambda/songs"),
            environment={
                "TABLE_NAME": db.table_name,
                "BUCKET_NAME": music_bucket.bucket_name
            }
        )

        db.grant_read_write_data(self.create_song_handler)
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
        
        # Get Songs Handler
        self.get_songs_handler = lambda_.Function(
            self,
            "GetSongsHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_songs.handler",
            code=lambda_.Code.from_asset("lambda/songs"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_data(self.get_songs_handler)
        
        # Get Songs By Album Handler
        self.get_songs_by_album_handler = lambda_.Function(
            self,
            "GetSongsByAlbumHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_songs_by_album.handler",
            code=lambda_.Code.from_asset("lambda/songs"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_data(self.get_songs_by_album_handler)
        
        # Get Song Handler
        self.get_song_handler = lambda_.Function(
            self,
            "GetSongHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_song.handler",
            code=lambda_.Code.from_asset("lambda/songs"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_data(self.get_song_handler)
        
        # Update Song Handler
        self.update_song_handler = lambda_.Function(
            self,
            "UpdateSongHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="update.handler",
            code=lambda_.Code.from_asset("lambda/songs"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_write_data(self.update_song_handler)
        
        # Delete Song Handler
        self.delete_song_handler = lambda_.Function(
            self,
            "DeleteSongHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="delete.handler",
            code=lambda_.Code.from_asset("lambda/songs"),
            environment={
                "TABLE_NAME": db.table_name,
                "BUCKET_NAME": music_bucket.bucket_name
            }
        )
        
        db.grant_read_write_data(self.delete_song_handler)
        music_bucket.grant_delete(self.delete_song_handler)
        
        # Create Album Handler
        self.create_album_handler = lambda_.Function(
            self,
            "CreateAlbumHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="create.handler",
            code=lambda_.Code.from_asset("lambda/albums"),
            environment={
                "TABLE_NAME": db.table_name,
                "BUCKET_NAME": music_bucket.bucket_name
            }
        )

        db.grant_read_write_data(self.create_album_handler)
        music_bucket.grant_put(self.create_album_handler)        # Get Albums Handler
        self.get_albums_handler = lambda_.Function(
            self,
            "GetAlbumsHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_albums.handler",
            code=lambda_.Code.from_asset("lambda/albums"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_data(self.get_albums_handler)
        
        # Get Album Handler
        self.get_album_handler = lambda_.Function(
            self,
            "GetAlbumHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_album.handler",
            code=lambda_.Code.from_asset("lambda/albums"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_data(self.get_album_handler)
        
        # Get Album Songs Handler
        self.get_album_songs_handler = lambda_.Function(
            self,
            "GetAlbumSongsHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_album_songs.handler",
            code=lambda_.Code.from_asset("lambda/albums"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_data(self.get_album_songs_handler)
        
        # Update Album Handler
        self.update_album_handler = lambda_.Function(
            self,
            "UpdateAlbumHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="update.handler",
            code=lambda_.Code.from_asset("lambda/albums"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_write_data(self.update_album_handler)
        
        # Delete Album Handler
        self.delete_album_handler = lambda_.Function(
            self,
            "DeleteAlbumHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="delete.handler",
            code=lambda_.Code.from_asset("lambda/albums"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_write_data(self.delete_album_handler)
        
        # Create Artist Handler
        self.create_artist_handler = lambda_.Function(
            self,
            "CreateArtistHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="create.handler",
            code=lambda_.Code.from_asset("lambda/artists"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_write_data(self.create_artist_handler)
        
        # Get Artists Handler
        self.get_artists_handler = lambda_.Function(
            self,
            "GetArtistsHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_artists.handler",
            code=lambda_.Code.from_asset("lambda/artists"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_data(self.get_artists_handler)
        
        # Get Artist Handler
        self.get_artist_handler = lambda_.Function(
            self,
            "GetArtistHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_artist.handler",
            code=lambda_.Code.from_asset("lambda/artists"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_data(self.get_artist_handler)
        
        # Update Artist Handler
        self.update_artist_handler = lambda_.Function(
            self,
            "UpdateArtistHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="update.handler",
            code=lambda_.Code.from_asset("lambda/artists"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_write_data(self.update_artist_handler)
        
        # Delete Artist Handler
        self.delete_artist_handler = lambda_.Function(
            self,
            "DeleteArtistHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="delete.handler",
            code=lambda_.Code.from_asset("lambda/artists"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_write_data(self.delete_artist_handler)
        
        # Get Albums By Artist Handler
        self.get_albums_by_artist_handler = lambda_.Function(
            self,
            "GetAlbumsByArtistHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_albums_by_artist.handler",
            code=lambda_.Code.from_asset("lambda/artists"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_data(self.get_albums_by_artist_handler)
        
        # Get Songs By Artist Handler
        self.get_songs_by_artist_handler = lambda_.Function(
            self,
            "GetSongsByArtistHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_songs_by_artist.handler",
            code=lambda_.Code.from_asset("lambda/artists"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_read_data(self.get_songs_by_artist_handler)
        
        # Subscribe Handler - Subscribe user to artist
        self.subscribe_handler = lambda_.Function(
            self,
            "SubscribeHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="subscribe.handler",
            code=lambda_.Code.from_asset("lambda/subscriptions"),
            environment={
                "SUBSCRIPTIONS_TABLE_NAME": subscriptions_table.table_name,
                "TABLE_NAME": db.table_name
            }
        )
        
        subscriptions_table.grant_read_write_data(self.subscribe_handler)
        db.grant_read_data(self.subscribe_handler)
        
        # Unsubscribe Handler - Unsubscribe user from artist
        self.unsubscribe_handler = lambda_.Function(
            self,
            "UnsubscribeHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="unsubscribe.handler",
            code=lambda_.Code.from_asset("lambda/subscriptions"),
            environment={
                "SUBSCRIPTIONS_TABLE_NAME": subscriptions_table.table_name
            }
        )
        
        subscriptions_table.grant_read_write_data(self.unsubscribe_handler)
        
        # Get User Subscriptions Handler - Get all subscriptions for a user
        self.get_user_subscriptions_handler = lambda_.Function(
            self,
            "GetUserSubscriptionsHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="get_subscriptions.handler",
            code=lambda_.Code.from_asset("lambda/subscriptions"),
            environment={
                "SUBSCRIPTIONS_TABLE_NAME": subscriptions_table.table_name
            }
        )
        
        subscriptions_table.grant_read_data(self.get_user_subscriptions_handler)
        
        # Toggle Notifications Handler - Toggle notifications for a subscription
        self.toggle_notifications_handler = lambda_.Function(
            self,
            "ToggleNotificationsHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="toggle_notifications.handler",
            code=lambda_.Code.from_asset("lambda/subscriptions"),
            environment={
                "SUBSCRIPTIONS_TABLE_NAME": subscriptions_table.table_name
            }
        )
        
        subscriptions_table.grant_read_write_data(self.toggle_notifications_handler)
        
        # Send Notifications Handler - Send email notifications to subscribers
        self.send_notifications_handler = lambda_.Function(
            self,
            "SendNotificationsHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="send_notifications.handler",
            code=lambda_.Code.from_asset("lambda/subscriptions"),
            environment={
                "SUBSCRIPTIONS_TABLE_NAME": subscriptions_table.table_name,
                "TABLE_NAME": db.table_name,
                "SES_SENDER_EMAIL": "romanminakov@proton.me",  # Change to your verified email
                "APP_URL": "d1wnmsdwgb6x45.cloudfront.net"
            },
            timeout=Duration.seconds(60),
            memory_size=256
        )
        
        subscriptions_table.grant_read_data(self.send_notifications_handler)
        db.grant_read_data(self.send_notifications_handler)
        
        # Grant SES permissions to send emails
        self.send_notifications_handler.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ses:SendEmail",
                    "ses:SendRawEmail"
                ],
                resources=["*"]
            )
        )
        
        # Update song and album create handlers to invoke send notifications
        self.create_song_handler.add_environment("SEND_NOTIFICATIONS_FUNCTION", self.send_notifications_handler.function_name)
        self.create_album_handler.add_environment("SEND_NOTIFICATIONS_FUNCTION", self.send_notifications_handler.function_name)
        
        # Grant permissions for create handlers to invoke send notifications
        self.send_notifications_handler.grant_invoke(self.create_song_handler)
        self.send_notifications_handler.grant_invoke(self.create_album_handler)
        
        # Grant Cognito permissions to auth handlers
        user_pool.grant(self.login_handler, "cognito-idp:AdminInitiateAuth")
        user_pool.grant(self.refresh_handler, "cognito-idp:InitiateAuth")
        user_pool.grant(self.register_handler, "cognito-idp:SignUp")
        user_pool.grant(self.confirm_handler, "cognito-idp:ConfirmSignUp")
 