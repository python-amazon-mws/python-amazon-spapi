"""Structured setup to get all your tokens."""
import boto3
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, BaseSettings, ValidationError
import requests


class Endpoints(Enum):
    """The 3 endpoints reflect AWS regions and are used for the signature."""
    north_america = 'https://sellingpartnerapi-na.amazon.com', 'us-east-1'
    brazil = 'https://sellingpartnerapi-na.amazon.com', 'us-east-1'
    canada = 'https://sellingpartnerapi-na.amazon.com', 'us-east-1'
    mexico = 'https://sellingpartnerapi-na.amazon.com', 'us-east-1'
    us = 'https://sellingpartnerapi-na.amazon.com', 'us-east-1'

    europe = 'https://sellingpartnerapi-eu.amazon.com', 'eu-west-1'
    spain = 'https://sellingpartnerapi-eu.amazon.com', 'eu-west-1'
    uk = 'https://sellingpartnerapi-eu.amazon.com', 'eu-west-1'
    france = 'https://sellingpartnerapi-eu.amazon.com', 'eu-west-1'
    germany = 'https://sellingpartnerapi-eu.amazon.com', 'eu-west-1'
    italy = 'https://sellingpartnerapi-eu.amazon.com', 'eu-west-1'
    turkey = 'https://sellingpartnerapi-eu.amazon.com', 'eu-west-1'
    uae = 'https://sellingpartnerapi-eu.amazon.com', 'eu-west-1'
    india = 'https://sellingpartnerapi-eu.amazon.com', 'eu-west-1'

    far_east = 'https://sellingpartnerapi-fe.amazon.com', 'us_west-2'
    singapore = 'https://sellingpartnerapi-fe.amazon.com', 'us_west-2'
    australia = 'https://sellingpartnerapi-fe.amazon.com', 'us_west-2'
    japan = 'https://sellingpartnerapi-fe.amazon.com', 'us_west-2'


class AccessTokenParams(BaseSettings):
    """Your credentials are best put into ~/.sellerpartnerapi.env."""
    grant_type = 'refresh_token'
    refresh_token: str
    client_id: str
    client_secret: str

    class Config:
        """
        Alternative locations for your configs.
        See in docs: https://pydantic-docs.helpmanual.io/usage/settings/
        """
        env_file = Path('~/.sellerpartnerapi.env')
        underscore_attrs_are_private = True


class AccessTokenRequest(BaseModel):
    """Model for data we need to request access token."""
    url = 'https://api.amazon.com/auth/o2/token'
    try:  # if you change local files you have to reimport
        params: AccessTokenParams = AccessTokenParams()
    except ValidationError:
        params: AccessTokenParams

    access_token: str = None

    def request_access_token(self):
        """Exchange your refresh token into an access token."""
        return requests.post(self.url, data=self.params.dict())

    def get_access_token(self) -> dict:
        """Parse access_token from request."""
        return self.request_access_token().json()['access_token']

    def prepare_access_token_request(self) -> dict:
        """For testing we return a request and you can do req.prepared()."""
        req = requests.Request(
            method='PUT', url=self.url, data=self.params.dict())
        return req

    def set_access_token(self) -> None:
        """Easy object interface for main."""
        self.access_token = self.get_access_token()


class StsTokenRequest(BaseSettings):
    """IAM Authentification with Amazon STS."""
    role_arn: str
    role_session_name: str

    access_key: str = None
    secret_key: str = None
    session_token: str = None

    class Config:
        """
        Alternative locations for your configs.
        See in docs: https://pydantic-docs.helpmanual.io/usage/settings/
        """
        env_file = Path('~/.sellerpartnerapi.env')
        underscore_attrs_are_private = True

    def request_sts_creds(self) -> dict:
        """Temporal sts creds from your iam role."""
        # boto does the signing for us
        client = boto3.client('sts')
        sts_creds = client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=self.role_session_name)
        return sts_creds

    def get_sts_creds(self) -> dict:
        sts_creds = self.request_sts_creds()
        return {
            'access_key': sts_creds['Credentials']['AccessKeyId'],
            'secret_key': sts_creds['Credentials']['SecretAccessKey'],
            'session_token': sts_creds['Credentials']['SessionToken']
        }

    def set_sts_creds(self) -> None:
        sts_creds = self.get_sts_creds()
        self.access_key = sts_creds['access_key']
        self.secret_key = sts_creds['secret_key']
        self.session_token = sts_creds['session_token']
