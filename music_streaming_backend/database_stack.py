from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb
)
from constructs import Construct

class DatabaseStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.db = dynamodb.TableV2(
            self,
            id="music-streaming-db-2025",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            global_secondary_indexes=[
                dynamodb.GlobalSecondaryIndexPropsV2(
                    index_name="artist-index",
                    partition_key=dynamodb.Attribute(name="artist", type=dynamodb.AttributeType.STRING),
                    sort_key=dynamodb.Attribute(name="title", type=dynamodb.AttributeType.STRING)
                ),
                dynamodb.GlobalSecondaryIndexPropsV2(
                    index_name="album-index",
                    partition_key=dynamodb.Attribute(name="album_id", type=dynamodb.AttributeType.STRING),
                    sort_key=dynamodb.Attribute(name="created_at", type=dynamodb.AttributeType.STRING)
                ),
                dynamodb.GlobalSecondaryIndexPropsV2(
                    index_name="artist-id-index",
                    partition_key=dynamodb.Attribute(name="artist_id", type=dynamodb.AttributeType.STRING),
                    sort_key=dynamodb.Attribute(name="created_at", type=dynamodb.AttributeType.STRING)
                )
            ]
        )

        # Subscriptions table for user subscriptions to artists
        self.subscriptions_table = dynamodb.TableV2(
            self,
            id="subscriptions-db-2025",
            partition_key=dynamodb.Attribute(name="user_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="artist_id", type=dynamodb.AttributeType.STRING),
            global_secondary_indexes=[
                dynamodb.GlobalSecondaryIndexPropsV2(
                    index_name="user-id-index",
                    partition_key=dynamodb.Attribute(name="user_id", type=dynamodb.AttributeType.STRING),
                    sort_key=dynamodb.Attribute(name="subscription_date", type=dynamodb.AttributeType.STRING)
                )
            ]
        )