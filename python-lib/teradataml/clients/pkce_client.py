"""
Unpublished work.
Copyright (c) 2023 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

This file implements PKCE client.
"""
import base64, httpx, hashlib, secrets, re
from teradataml.utils.validators import _Validators
from teradataml.options import configure
from urllib.parse import parse_qs, urlparse
import httpx as requests
from time import time, sleep

class _PKCEClient:
    """
    Proof Key for Code Exchange Client to get the Authorization code from any server which implements
    OAuth 2.0 for providing the access to clients.
    """

    def __init__(self, base_url, client_id, redirect_url="http://localhost:4200/callback", timeout=30):
        """
        DESCRIPTION:
            Constructor to initiate OAuth work flow.

        PARAMETERS:
            base_url:
                Required Argument.
                Specifies the base URL of OAuth Server.
                Types: str

            client_id:
                Required Argument.
                Specifies the client id of OAuth Server. One should get the client id from OAuth server.
                Types: str

            redirect_url:
                Optional Argument.
                Specifies the redirect URL in OAuth workflow. The URL will be used by Auth server
                to post the details. Then the application receives these details and stores it for
                future use. teradataml never uses this URL to redirect instead this is for Auth server.
                Default Values: http://localhost:4200/callback
                Types: str

            timeout:
                Optional Argument.
                Specifies the timeout in seconds for HTTP Request.
                Default Value: 30
                Types: int or float

        RETURNS:
            Instance of _PKCEClient.

        RAISES:
            None

        EXAMPLES :
            >>> _PKCEClient("client_id", "base_url")
        """
        # Provided by caller
        self.__base_url = base_url
        self.__client_id = client_id

        self.__session = httpx.Client(timeout=timeout)
        self.__redirect_url = redirect_url
        self.oauth_end_point = None
        self.__open_id_configuration_resource = "/auth/.well-known/openid-configuration"

        # Set the username label.
        self.__username_label = configure._pf_token_username_label
        self.__password_label = configure._pf_token_password_label

        self.__html_form_headers = {"Content-Type": "application/x-www-form-urlencoded",
                                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

    def _get_token_data(self, username=None, password=None, refresh_token=None, **kwargs):
        """
        DESCRIPTION:
            Function to fetch the Authentication token details from credentials.

        PARAMETERS:
            username:
                Optional Argument.
                Specifies the Username for which token is requested for.
                Types: str

            password:
                Optional Argument.
                Specifies the password for "username" for which token is requested for.
                Types: str

            refresh_token:
                Optional Argument.
                Specifies the refresh token.
                Note:
                    Either "username"/"password" or "refresh_token" is mandatory.
                Types: str

            kwargs:
                Optional Argument.
                Specifies keyword arguments. Reserved for MFA.

        RETURNS:
            dict.

        RAISES:
            None

        EXAMPLES :
            >>> _PKCEClient("client_id", "base_url")._get_token_data("user", "password")
            >>> _PKCEClient("client_id", "base_url")._get_token_data(refresh_token=configure._refresh_token)
        """
        # Either refresh_token or (username and password) is mandatory.
        _Validators._validate_mutually_exclusive_arguments(
            username, "username/password", refresh_token, "refresh_token")

        if refresh_token is not None:
            # Retrieve the end point if it is not available.
            if configure._oauth_end_point is None:
                open_id_config = self.__get_openid_config()
                configure._oauth_end_point = open_id_config["token_endpoint"]

            # Prepare the payload for getting the token from refresh token.
            params = {
                "grant_type": "refresh_token",
                "client_id": self.__client_id,
                "refresh_token": refresh_token
            }

            response = self.__session.post(
                url=configure._oauth_end_point,
                headers=self.__html_form_headers,
                data=params,
            )

            # Check the status. If response is not 200, raise error.
            _Validators._validate_http_response(response, 200, "get the token from refresh token")

            return response.json()

        else:
            # Get the OPEN ID Configuration.
            open_id_config = self.__get_openid_config()
            self.oauth_end_point = open_id_config["token_endpoint"]

            # Create code verifier.
            code_verifier = secrets.token_urlsafe(96)[:128]

            # Create code challenge from code verifier.
            hashed_verifier: bytes = hashlib.sha256(code_verifier.encode("ascii")).digest()
            b64encoded_hashed_verifier = base64.urlsafe_b64encode(hashed_verifier)
            code_challenge: str = b64encoded_hashed_verifier.decode("ascii")
            # (remove '=' padding)
            code_challenge = code_challenge[:-1]

            # Get the login page & relevant data.
            action_url = self.__get_login_page_action_url(open_id_config["authorization_endpoint"], code_challenge)

            # Submit login info and get code
            code = self.__get_authorization_code(action_url, username, password, **kwargs)

            # Exchange code for token.
            token_data = self.__get_jwt_token_with_code(open_id_config["token_endpoint"], code, code_verifier)

            return token_data

    def __get_openid_config(self):
        """
        DESCRIPTION:
            Internal function to fetch the OPEN ID Configuration.

        PARAMETERS:
            None

        RETURNS:
            dict

        RAISES:
            None
        """
        response = self.__session.get("{}{}".format(self.__base_url, self.__open_id_configuration_resource))

        # Check the status. If response is not 200, raise error.
        _Validators._validate_http_response(response, 200, "get the configuration")

        return response.json()

    def __get_login_page_action_url(self, auth_url, code_challenge):
        """
        DESCRIPTION:
            Internal function to get the login URL to post the credentials.

        PARAMETERS:
            auth_url:
                Required Argument.
                Specifies the Authentication URL.
                Types: str

            code_challenge:
                Required Argument.
                Specifies the Code Challenge to sent to Authentication URL.
                Types: str

        RETURNS:
            str

        RAISES:
            TeradataMlException
        """
        # Fetch the html login page.
        # Send the Code Challenge along with client id and redirect URL.
        # The response will be a HTML code which contains URL to post the
        # username and password.
        response = self.__session.get(
            url=auth_url,
            params={
                "response_type": "code",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "client_id": self.__client_id,
                "redirect_uri": self.__redirect_url,
                "scope": "openid",
            }
        )

        # Check the status. If response is not 200, raise error.
        _Validators._validate_http_response(response, 200, "get the login details")

        login_page = response.text

        # Parse the html page using regex to find Form Action URL
        return re.search(r'\s+action="([^"]+)"', login_page).group(1)

    def __get_authorization_code(self, action_url, username, password, **kwargs):
        """
        DESCRIPTION:
            Internal function to get the Authorization code using the credentials.
            Note that response is not JWT code. It is an Authorization code and
            using the Authorization code, Access code(JWT Token) is retrieved.

        PARAMETERS:
            action_url:
                Required Parameter.
                Specifies the Authorization URL to which username and password to be posted.
                Types: str

            username:
                Required Argument.
                Specifies the Username for which token is requested for.
                Types: str

            password:
                Required Argument.
                Specifies the password for "username" for which token is requested for.
                Types: str

            kwargs:
                Optional Argument.
                Specifies keyword arguments. Reserved for MFA.

        RETURNS:
            Authorization token, str.

        RAISES:
            None

        EXAMPLES :
            >>> _PKCEClient("client_id", "base_url").__get_authorization_code("http://some.client", "user", "password")
        """
        data = {self.__username_label: username, self.__password_label: password}

        # Update the data with kwargs if it has any data.
        if kwargs:
            data = data.update(kwargs)

        response = self.__session.post(
            url="{}{}".format(self.__base_url, action_url),
            headers=self.__html_form_headers,
            data=data
        )

        # We expect a 302 (redirect) response at this point
        _Validators._validate_http_response(response, 302, "get the Authorization code")

        # Extract the code from the location header (e.g. "http://localhost?code=xyz")
        location_url = response.headers["location"]
        parsed_url = urlparse(location_url)
        return parse_qs(parsed_url.query)["code"][0]

    def __get_jwt_token_with_code(self, token_url, code, code_verifier):

        # Request token data using code and code_verifier
        # Again submit the form with Authorization code recieved from
        # __get_authorization_code along with form headers.

        response = self.__session.post(
            url=token_url,
            headers=self.__html_form_headers,
            data={
                "grant_type": "authorization_code",
                "client_id": self.__client_id,
                "code_verifier": code_verifier,
                "code": code,
                "redirect_uri": self.__redirect_url
            }
        )

        # We expect a 200 (redirect) response at this point
        _Validators._validate_http_response(response, 200, "get the JWT Token")

        return response.json()
    
class _DAWorkflow:
    """
    Get the Authorization code from any server which support Device Authorization.
    """
    def __init__(self, base_url, client_id):
        """
        DESCRIPTION:
            Constructor to initiate Device Authentication work flow.
        PARAMETERS:
            base_url:
                Required Argument.
                Specifies the base URL of OAuth Server.
                Types: str
            client_id:
                Required Argument.
                Specifies the client id of OAuth Server. One should get the client id from OAuth server.
                Types: str
        RETURNS:
            Instance of _PKCEClient.
        RAISES:
            None
        EXAMPLES :
            >>> _DAWorkflow("client_id", "base_url")
        """
        self.__base_url = base_url
        self.__client_id = client_id
        self.verification_uri= None

        self.device_auth_end_point = None
        self.__token_endpoint = None
        self.__open_id_configuration_resource = "/auth/.well-known/openid-configuration"

    def _get_token_data(self):
        metadata = self.__get_issuer_metadata()
        self.device_auth_end_point = metadata["device_authorization_endpoint"]
        self.__token_endpoint = metadata["token_endpoint"]


        device_metadata = self.__get_device_metadata()

        token_data = self.__get_access_token_data(device_metadata)
        return token_data

    def __get_issuer_metadata(self):
        # Fetch the metadata to get the DA details.
        metadata_response = requests.get(
            url="{}{}".format(self.__base_url, self.__open_id_configuration_resource))

        # Check the status. If response is not 200, raise error.
        _Validators._validate_http_response(metadata_response, 200, "get the configuration")

        return metadata_response.json()

    def __get_device_metadata(self):
        device_metadata = requests.post(
            url=self.device_auth_end_point,
            data={'client_id': self.__client_id},
            verify=True)

        # Check the status. If response is not 200, raise error.
        _Validators._validate_http_response(device_metadata, 200, "get the device metadata")

        return device_metadata.json()

    def __get_access_token_data(self, device_metadata):
        self.verification_uri=device_metadata['verification_uri_complete']
        
        # Poll the token endpoint at the specified interval for an access token.
        token_data = {
            'client_id': self.__client_id,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'device_code': device_metadata['device_code'],
        }
        # Get the maximum time for polling the token endpoint.
        max_wait = time() + device_metadata['expires_in']
        
        poll_data=[max_wait,self.__token_endpoint,
               token_data,
               device_metadata['interval']
                ]
        
        return poll_data
        
