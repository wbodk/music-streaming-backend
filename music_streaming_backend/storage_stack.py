from aws_cdk import (
    Stack,
    Duration,
    aws_s3 as s3,
    RemovalPolicy,
    aws_iam as iam,
)
from constructs import Construct

class StorageStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.music_bucket = s3.Bucket(
            self,
            "MusicStorageBucket",
            bucket_name=f"music-streaming-bucket-{self.account}",
            versioned=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True
            ),
            encryption=s3.BucketEncryption.S3_MANAGED,
            lifecycle_rules=[
                s3.LifecycleRule(
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(30)
                        )
                    ]
                )
            ],
            removal_policy=RemovalPolicy.RETAIN,
        )

        self.music_bucket.add_cors_rule(
            allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST],
            allowed_origins=["*"],
            allowed_headers=["*"],
            max_age=3000
        )
