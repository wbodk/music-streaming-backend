from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_lambda as lambda_,
)
from constructs import Construct

class ApiStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            create_song_handler: lambda_.Function,
            get_songs_handler: lambda_.Function,
            get_songs_by_album_handler: lambda_.Function,
            get_song_handler: lambda_.Function,
            update_song_handler: lambda_.Function,
            delete_song_handler: lambda_.Function,
            create_album_handler: lambda_.Function,
            get_albums_handler: lambda_.Function,
            get_album_handler: lambda_.Function,
            update_album_handler: lambda_.Function,
            delete_album_handler: lambda_.Function,
            create_artist_handler: lambda_.Function,
            get_artists_handler: lambda_.Function,
            get_artist_handler: lambda_.Function,
            update_artist_handler: lambda_.Function,
            delete_artist_handler: lambda_.Function,
            get_albums_by_artist_handler: lambda_.Function,
            get_songs_by_artist_handler: lambda_.Function,
            login_handler: lambda_.Function,
            refresh_handler: lambda_.Function,
            register_handler: lambda_.Function,
            confirm_handler: lambda_.Function,
            user_pool: cognito.UserPool,
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)
    
        self.cognito_authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self,
            "CognitoAuthorizer",
            cognito_user_pools=[user_pool]
        )

        self.api = apigateway.RestApi(
            self,
            "MusicStreamingAPI",
            rest_api_name="Music Streaming API",
            description="REST API for music streaming CRUD operations",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_headers=apigateway.Cors.DEFAULT_HEADERS + ["Authorization"],
                allow_credentials=True
            )
        )
    
        # Define CORS response headers that will be added to all responses
        cors_response_headers = {
            "Access-Control-Allow-Origin": "'*'",
            "Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
            "Access-Control-Allow-Methods": "'GET,POST,PUT,DELETE,OPTIONS'"
        }

        # Auth endpoints (no authentication required)
        self.auth_resource = self.api.root.add_resource("auth")
        
        # POST /auth/login - Login endpoint
        self.login_resource = self.auth_resource.add_resource("login")
        self.login_resource.add_method("POST", apigateway.LambdaIntegration(login_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        # POST /auth/refresh - Refresh token endpoint
        self.refresh_resource = self.auth_resource.add_resource("refresh")
        self.refresh_resource.add_method("POST", apigateway.LambdaIntegration(refresh_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        # POST /auth/register - Register endpoint
        self.register_resource = self.auth_resource.add_resource("register")
        self.register_resource.add_method("POST", apigateway.LambdaIntegration(register_handler),
            method_responses=[apigateway.MethodResponse(status_code="201", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        # POST /auth/confirm - Confirm registration endpoint
        self.confirm_resource = self.auth_resource.add_resource("confirm")
        self.confirm_resource.add_method("POST", apigateway.LambdaIntegration(confirm_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        # Songs endpoints
        self.songs_resource = self.api.root.add_resource("songs")
        
        self.songs_resource.add_method("GET", apigateway.LambdaIntegration(get_songs_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.songs_resource.add_method("POST", apigateway.LambdaIntegration(create_song_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="201", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.song_resource = self.songs_resource.add_resource("{songId}")
        
        self.song_resource.add_method("GET", apigateway.LambdaIntegration(get_song_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.song_resource.add_method("PUT", apigateway.LambdaIntegration(update_song_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.song_resource.add_method("DELETE", apigateway.LambdaIntegration(delete_song_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="204", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        # Albums endpoints
        self.albums_resource = self.api.root.add_resource("albums")
        
        self.albums_resource.add_method("GET", apigateway.LambdaIntegration(get_albums_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.albums_resource.add_method("POST", apigateway.LambdaIntegration(create_album_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="201", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.album_resource = self.albums_resource.add_resource("{albumId}")
        
        self.album_resource.add_method("GET", apigateway.LambdaIntegration(get_album_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.album_resource.add_method("PUT", apigateway.LambdaIntegration(update_album_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.album_resource.add_method("DELETE", apigateway.LambdaIntegration(delete_album_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="204", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        # GET /albums/{albumId}/songs - Get songs in album
        self.album_songs_resource = self.album_resource.add_resource("songs")
        
        self.album_songs_resource.add_method("GET", apigateway.LambdaIntegration(get_songs_by_album_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        # Artists endpoints
        self.artists_resource = self.api.root.add_resource("artists")
        
        self.artists_resource.add_method("GET", apigateway.LambdaIntegration(get_artists_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.artists_resource.add_method("POST", apigateway.LambdaIntegration(create_artist_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="201", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.artist_resource = self.artists_resource.add_resource("{artistId}")
        
        self.artist_resource.add_method("GET", apigateway.LambdaIntegration(get_artist_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.artist_resource.add_method("PUT", apigateway.LambdaIntegration(update_artist_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        self.artist_resource.add_method("DELETE", apigateway.LambdaIntegration(delete_artist_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="204", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        # GET /artists/{artistId}/albums - Get albums by artist
        self.artist_albums_resource = self.artist_resource.add_resource("albums")
        
        self.artist_albums_resource.add_method("GET", apigateway.LambdaIntegration(get_albums_by_artist_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])
        
        # GET /artists/{artistId}/songs - Get songs by artist
        self.artist_songs_resource = self.artist_resource.add_resource("songs")
        
        self.artist_songs_resource.add_method("GET", apigateway.LambdaIntegration(get_songs_by_artist_handler),
            method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={"method.response.header.Access-Control-Allow-Origin": True})])

