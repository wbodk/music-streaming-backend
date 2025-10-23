#!/usr/bin/env python3
import os

import aws_cdk as cdk

from music_streaming_backend.database_stack import DatabaseStack
from music_streaming_backend.auth_stack import AuthStack
from music_streaming_backend.storage_stack import StorageStack
from music_streaming_backend.lambda_stack import LambdaStack
from music_streaming_backend.api_stack import ApiStack

app = cdk.App()

db_stack = DatabaseStack(app, "MusicStreamingDataBaseStack")
auth_stack = AuthStack(app, "MusicStreamingAuthStack")
storage_stack = StorageStack(app, "MusicStreamingStorageStack")
lambda_stack = LambdaStack(
    app, 
    "MusicStreamingLambdaStack", 
    db=db_stack.db, 
    music_bucket=storage_stack.music_bucket,
    user_pool=auth_stack.user_pool,
    user_pool_client=auth_stack.user_pool_client
)
api_stack = ApiStack(
                        app,
                        "MusicStreamingApiStack",
                        create_song_handler=lambda_stack.create_song_handler,
                        get_songs_handler=lambda_stack.get_songs_handler,
                        get_songs_by_album_handler=lambda_stack.get_songs_by_album_handler,
                        get_song_handler=lambda_stack.get_song_handler,
                        update_song_handler=lambda_stack.update_song_handler,
                        delete_song_handler=lambda_stack.delete_song_handler,
                        create_album_handler=lambda_stack.create_album_handler,
                        get_albums_handler=lambda_stack.get_albums_handler,
                        get_album_handler=lambda_stack.get_album_handler,
                        update_album_handler=lambda_stack.update_album_handler,
                        delete_album_handler=lambda_stack.delete_album_handler,
                        create_artist_handler=lambda_stack.create_artist_handler,
                        get_artists_handler=lambda_stack.get_artists_handler,
                        get_artist_handler=lambda_stack.get_artist_handler,
                        update_artist_handler=lambda_stack.update_artist_handler,
                        delete_artist_handler=lambda_stack.delete_artist_handler,
                        get_albums_by_artist_handler=lambda_stack.get_albums_by_artist_handler,
                        get_songs_by_artist_handler=lambda_stack.get_songs_by_artist_handler,
                        login_handler=lambda_stack.login_handler,
                        refresh_handler=lambda_stack.refresh_handler,
                        register_handler=lambda_stack.register_handler,
                        confirm_handler=lambda_stack.confirm_handler,
                        user_pool=auth_stack.user_pool,
                    )

lambda_stack.add_dependency(db_stack)
lambda_stack.add_dependency(storage_stack)
lambda_stack.add_dependency(auth_stack)
api_stack.add_dependency(lambda_stack)
api_stack.add_dependency(auth_stack)
api_stack.add_dependency(db_stack)

app.synth()
