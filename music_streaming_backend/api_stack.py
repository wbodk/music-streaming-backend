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
                allow_origins=apigateway.Cors.ALL_ORIGINS
            )
        )

        # Auth endpoints (no authentication required)
        self.auth_resource = self.api.root.add_resource("auth")
        
        # POST /auth/login - Login endpoint
        self.login_resource = self.auth_resource.add_resource("login")
        self.login_resource.add_method("POST", apigateway.LambdaIntegration(login_handler),
            method_responses=[apigateway.MethodResponse(status_code="200")])
        
        # POST /auth/refresh - Refresh token endpoint
        self.refresh_resource = self.auth_resource.add_resource("refresh")
        self.refresh_resource.add_method("POST", apigateway.LambdaIntegration(refresh_handler),
            method_responses=[apigateway.MethodResponse(status_code="200")])
        
        # POST /auth/register - Register endpoint
        self.register_resource = self.auth_resource.add_resource("register")
        self.register_resource.add_method("POST", apigateway.LambdaIntegration(register_handler),
            method_responses=[apigateway.MethodResponse(status_code="201")])
        
        # POST /auth/confirm - Confirm registration endpoint
        self.confirm_resource = self.auth_resource.add_resource("confirm")
        self.confirm_resource.add_method("POST", apigateway.LambdaIntegration(confirm_handler),
            method_responses=[apigateway.MethodResponse(status_code="200")])
        
        # Songs endpoints
        self.songs_resource = self.api.root.add_resource("songs")
        
        self.songs_resource.add_method("GET", apigateway.MockIntegration(
            integration_responses=[apigateway.IntegrationResponse(status_code="200")]
        ), method_responses=[apigateway.MethodResponse(status_code="200")])
        
        self.songs_resource.add_method("POST", apigateway.LambdaIntegration(create_song_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="201")])
        
        self.song_resource = self.songs_resource.add_resource("{songId}")
        
        self.song_resource.add_method("GET", apigateway.MockIntegration(
            integration_responses=[apigateway.IntegrationResponse(status_code="200")]
        ), method_responses=[apigateway.MethodResponse(status_code="200")])
        
        self.song_resource.add_method("PUT", apigateway.MockIntegration(
            integration_responses=[apigateway.IntegrationResponse(status_code="200")]
        ), method_responses=[apigateway.MethodResponse(status_code="200")])
        
        self.song_resource.add_method("DELETE", apigateway.MockIntegration(
            integration_responses=[apigateway.IntegrationResponse(status_code="204")]
        ), method_responses=[apigateway.MethodResponse(status_code="204")]) 
