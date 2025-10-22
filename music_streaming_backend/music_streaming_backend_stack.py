from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
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
