import hashlib
import hmac
import datetime
import requests

from spapi import setup


class SPAPI:
    def __init__(
        self, access_token: str, stscreds: dict, path: str,
        http_verb: str = 'GET', querystring: str = '',
        payload: str = '', region: str = None
    ):
        self.access_token = access_token
        self.stscreds = stscreds

        self.region: str = setup.Endpoints[region.lower()].value[1]
        self.endpoint: str = setup.Endpoints[region.lower()].value[0]

        self.path = path

        self.set_datestrings()

        # api
        self.http_verb = http_verb
        self.host: str = self.endpoint.split('https://')[-1]
        self.payload = payload

        self.canonical_headers = (
            f'host:{self.host}\nx-amz-date:{self.amzdate}\n')
        self.canonical_request = None
        self.canonical_querystring: str = querystring

        self.service = 'execute-api'
        self.signed_headers = 'host;x-amz-date'
        self.algorithm = 'AWS4-HMAC-SHA256'
        self.credential_scope = (f'{self.datestamp}/{self.region}'
                                 f'/{self.service}/aws4_request')

        self.create_canonical_request()
        self.create_string_to_sign()
        self.add_signing_to_request()
        self.prepare_request()

    def set_datestrings(self):
        """Create a date for headers and the credential string."""
        now = datetime.datetime.utcnow()
        self.amzdate = now.strftime('%Y%m%dT%H%M%SZ')
        self.datestamp = now.strftime('%Y%m%d')

    def sign(self, key, msg) -> str:
        # https://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html

        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def getSignatureKey(self):
        kDate = self.sign((
            'AWS4' + self.stscreds['secret_key']).encode(
                'utf-8'), self.datestamp)
        kRegion = self.sign(kDate, self.region)
        kService = self.sign(kRegion, self.service)
        kSigning = self.sign(kService, 'aws4_request')
        return kSigning

    def hash_payload(self) -> str:
        """For GET requests it is an empty string."""
        return hashlib.sha256((self.payload).encode('utf-8')).hexdigest()

    def create_canonical_request(self) -> str:
        # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
        # https://cloud.google.com/storage/docs/authentication/canonical-requests

        canonical_request_components = [
            self.http_verb,
            self.path,
            self.canonical_querystring.strip('?'),
            self.canonical_headers,
            self.signed_headers,
            self.hash_payload()
        ]
        self.canonical_request = '\n'.join(canonical_request_components)

    def create_string_to_sign(self):
        hashed_request = hashlib.sha256(self.canonical_request.encode(
            'utf-8')).hexdigest()
        string_to_sign_components = [
            self.algorithm,
            self.amzdate,
            self.credential_scope,
            hashed_request
        ]
        self.string_to_sign = '\n'.join(string_to_sign_components)

        signing_key = self.getSignatureKey()

        # Sign the string_to_sign using the signing_key
        signature = hmac.new(signing_key, (
            self.string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def add_signing_to_request(self):
        signature = self.create_string_to_sign()
        authorization_header = (
            f'{self.algorithm} '
            f"Credential={self.stscreds['access_key']}"
            f'/{self.credential_scope}'
            f', SignedHeaders={self.signed_headers} Signature={signature}')

        headers = {'x-amz-date': self.amzdate,
                   'Authorization': authorization_header,
                   'x-amz-access-token': self.access_token,
                   'x-amz-security-token': self.stscreds['session_token']}
        return headers

    def prepare_request(self):
        self.headers = self.add_signing_to_request()
        self.request_url = (
            self.endpoint + self.path + self.canonical_querystring)

    def prepared_request(self):
        req = requests.Request(
            method='GET', headers=self.headers, url=self.request_url
        )
        return req

    def make_request(self):
        response = requests.get(self.request_url, headers=self.headers)
        return response

    def main(self):
        """Main entry for queries."""
        response = self.make_request()
        return response
