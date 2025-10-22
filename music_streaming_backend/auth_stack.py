from aws_cdk import (
    Stack,
    Duration,
    aws_cognito as cognito
)
from constructs import Construct

class AuthStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.user_pool = cognito.UserPool(
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

        self.user_pool_domain = cognito.UserPoolDomain(
            self,
            "MusicStreamingUserPoolDomain",
            user_pool=self.user_pool,
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="music-streaming-app-ruo2025"  
            )
        )

        self.user_pool_client = cognito.UserPoolClient(
            self,
            "MusicStreamingUserPoolClient",
            user_pool=self.user_pool,
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

        self.admin_group = cognito.CfnUserPoolGroup(
            self,
            "AdminGroup",
            user_pool_id=self.user_pool.user_pool_id,
            group_name="admin",
            description="Administrator group for music streaming app",
            precedence=0
        )