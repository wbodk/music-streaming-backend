from aws_cdk import (
    Stack,
    Duration,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_cognito as cognito
)
from constructs import Construct

class MusicStreamingBackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        db = dynamodb.TableV2(
            self,
            id="music-streaming-db-2025",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            global_secondary_indexes=[
                dynamodb.GlobalSecondaryIndexPropsV2(
                    index_name="artist-index",
                    partition_key=dynamodb.Attribute(name="artist", type=dynamodb.AttributeType.STRING),
                    sort_key=dynamodb.Attribute(name="title", type=dynamodb.AttributeType.STRING)
                )
            ]
        )

        create_song_handler = lambda_.Function(
            self,
            "CreateSongHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda/create_song"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )
        
        db.grant_write_data(create_song_handler)

        user_pool = cognito.UserPool(
            self,
            "MusicStreamingUserPool",
            self_sign_up_enabled=True,
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=False,
                require_uppercase=False,
                require_digits=True,
                require_symbols=True
            ),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True),
                given_name=cognito.StandardAttribute(required=True, mutable=True),
                family_name=cognito.StandardAttribute(required=True, mutable=True),
                birthdate=cognito.StandardAttribute(required=True, mutable=True),
                preferred_username=cognito.StandardAttribute(required=True, mutable=True)
            ),
            sign_in_aliases=cognito.SignInAliases(
                username=True,
                email=True
            ),
            auto_verify=cognito.AutoVerifiedAttrs(
                email=True
            )
        )

        user_pool_domain = cognito.UserPoolDomain(
            self,
            "MusicStreamingUserPoolDomain",
            user_pool=user_pool,
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="music-streaming-app-romanminakov"  
            )
        )

        user_pool_client = cognito.UserPoolClient(
            self,
            "MusicStreamingUserPoolClient",
            user_pool=user_pool,
            user_pool_client_name="music-streaming-client",
            generate_secret=True,
            auth_flows=cognito.AuthFlow(
                user_password=True,
                admin_user_password=True
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True
                ),
                scopes=[cognito.OAuthScope.OPENID, cognito.OAuthScope.EMAIL, cognito.OAuthScope.PROFILE],
                callback_urls=["http://localhost:3000", "http://localhost:3000/callback"],
                logout_urls=["http://localhost:3000/logout"]
            ),
            read_attributes=cognito.ClientAttributes().with_standard_attributes(
                email=True,
                given_name=True,
                family_name=True,
                birthdate=True,
                preferred_username=True
            ),
            write_attributes=cognito.ClientAttributes().with_standard_attributes(
                email=True,
                given_name=True,
                family_name=True,
                birthdate=True,
                preferred_username=True
            ),
            enable_token_revocation=True,
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
            prevent_user_existence_errors=True
        )

        admin_group = cognito.CfnUserPoolGroup(
            self,
            "AdminGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="admin",
            description="Administrator group for music streaming app",
            precedence=0
        )

        cognito_authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self,
            "CognitoAuthorizer",
            cognito_user_pools=[user_pool]
        )

        api = apigateway.RestApi(
            self,
            "MusicStreamingAPI",
            rest_api_name="Music Streaming API",
            description="REST API for music streaming CRUD operations",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_origins=apigateway.Cors.ALL_ORIGINS
            )
        )

        songs_resource = api.root.add_resource("songs")
        
        songs_resource.add_method("GET", apigateway.MockIntegration(
            integration_responses=[apigateway.IntegrationResponse(status_code="200")]
        ), method_responses=[apigateway.MethodResponse(status_code="200")])
        
        songs_resource.add_method("POST", apigateway.LambdaIntegration(create_song_handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=cognito_authorizer,
            method_responses=[apigateway.MethodResponse(status_code="201")])
        
        song_resource = songs_resource.add_resource("{songId}")
        
        song_resource.add_method("GET", apigateway.MockIntegration(
            integration_responses=[apigateway.IntegrationResponse(status_code="200")]
        ), method_responses=[apigateway.MethodResponse(status_code="200")])
        
        song_resource.add_method("PUT", apigateway.MockIntegration(
            integration_responses=[apigateway.IntegrationResponse(status_code="200")]
        ), method_responses=[apigateway.MethodResponse(status_code="200")])
        
        song_resource.add_method("DELETE", apigateway.MockIntegration(
            integration_responses=[apigateway.IntegrationResponse(status_code="204")]
        ), method_responses=[apigateway.MethodResponse(status_code="204")])
