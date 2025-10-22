from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb
)
from constructs import Construct

class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, db: dynamodb.TableV2, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.create_song_handler = lambda_.Function(
            self,
            "CreateSongHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda/create_song"),
            environment={
                "TABLE_NAME": db.table_name
            }
        )

        db.grant_write_data(self.create_song_handler)
 