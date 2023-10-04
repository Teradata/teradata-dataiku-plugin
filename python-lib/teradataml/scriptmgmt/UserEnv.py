#!/usr/bin/python
# ####################################################################
#
# Copyright (c) 2023 by Teradata Corporation. All rights reserved.
# TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET
#
# ####################################################################

import functools
import inspect
from json.decoder import JSONDecodeError
import os, time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, wait

from teradataml.options import configure
from teradataml.clients.pkce_client import _PKCEClient, _DAWorkflow
#from teradataml.context.context import _get_user
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.utils import UtilFuncs
from teradataml.utils.validators import _Validators



from urllib.parse import urlparse
#from query_engine_wrapper import QueryEngineWrapper

from enum import Enum

def get_user_name(query_engine_wrapper):
    query_string = "SELECT top 1 user FROM DBC.DBCInfoV;"
    query_results = None
 
    query_results = query_engine_wrapper.execute(query_string)
   
    # SKS loop once: for each JSON column of row, 
    # In theory only one row exists which is the InfoData we care about
    for row in query_engine_wrapper.iteratable(query_results):
        user_name = query_engine_wrapper.row_value(row, "User")
    return user_name

class HTTPRequest(Enum):
    # Holds variable names for HTTP calls.
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"

def _get_ues_url(env_type="users", user_name=None, **kwargs):
    """
    DESCRIPTION:
        Function to get the URL for inititating REST call to UES.

    PARAMETERS:
        env_type:
            Optional Argument.
            Specifies the type of resource in URL.
            Default Value: users
            Types: str

        api_name:
            Optional Argument.
            Specifies the name of the teradataml UES API to mention in the error message.
            Types: str

        kwargs:
            Specifies keyword arguments that can be passed to get the URL.

    RETURNS:
        str

    RAISES:
        TeradataMlException, RuntimeError

    EXAMPLES:
            >>> _get_ues_url("base_environments") # URL for listing base environments.
            >>> _get_ues_url() # URL to create/remove/list the user environment(s).
            >>> _get_ues_url(env_name="alice_env") # URL to delete/list files in an environment.
            >>> _get_ues_url(env_name="alice_env", files=True, api_name="install_file") # URL to install/replace file in environment.
            >>> _get_ues_url(env_name="alice_env", files=True, file_name="a.py") # URL to remove a file in environment.
            >>> _get_ues_url(env_name="alice_env", libs=True, api_name="libs") # URL to install/uninstall/update/list library in environment.
            >>> _get_ues_url(env_type="fm", claim_id="123-456", api_name=status) # URL for checking the task status.
            >>> _get_ues_url(env_type="fm", fm_type="export", claim_id="123-456") # URL for exporting a file.
            >>> _get_ues_url(env_type="fm", fm_type="import", api_name="install_file") # URL for generating end point to upload file.
            >>> _get_ues_url(env_name=self.env_name, files=True, is_property=True, api_name="files") # URL for listing down the files.
    """
    api_name = kwargs.pop("api_name", inspect.stack()[1].function)

    
    if configure.ues_url is None:
        error_msg = Messages.get_message(MessageCodes.DEPENDENT_ARGUMENT,
                                         api_name, 'configure.ues_url')
        raise RuntimeError(error_msg)

    ues_url = "{}/{}".format(configure.ues_url, env_type)

    if env_type not in ("users", "fm"):
        return ues_url

    elif env_type == "fm":
        fm_type = kwargs.get("fm_type")
        if fm_type == "import":
            return "{}/import".format(ues_url)
        elif fm_type == "export":
            return "{}/export/{}".format(ues_url, kwargs["claim_id"])
        else:
            return "{}/users/{}/{}/tasks/{}".format(configure.ues_url,
                                                    user_name,
                                                    env_type, kwargs["claim_id"])

    # We will reach here to process "users" env type.
    ues_url = "{0}/{1}/environments".format(ues_url, user_name)

    env_name, files, libs = kwargs.get("env_name"), kwargs.get("files", False), kwargs.get("libs", False)
    if env_name is not None:
        ues_url = "{0}/{1}".format(ues_url, env_name)

    if files:
        ues_url = "{0}/{1}".format(ues_url, "files")
        file_name = kwargs.get("file_name")
        if file_name is not None:
            ues_url = "{0}/{1}".format(ues_url, file_name)
    elif libs:
        ues_url = "{0}/{1}".format(ues_url, "libraries")

    return ues_url


def _process_ues_response(api_name, response, success_status_code=None):
    """
    DESCRIPTION:
        Function to process and validate the UES Response.

    PARAMETERS:
        api_name:
            Required Argument.
            Specifies the name of the teradataml UES API.
            Types: str

        response:
            Required Argument.
            Specifies the response recieved from UES.
            Types: requests.Response

        success_status_code:
            Optional Argument.
            Specifies the expected success status code for the corresponding UES API.
            Default Value: None
            Types: int

    RETURNS:
        Response object.

    RAISES:
        TeradataMlException.

    EXAMPLES:
            >>> _process_ues_response("list_base_envs", resp)
    """
    try:
        # Success status code ranges between 200-300.
        if (success_status_code is None and 200 <= response.status_code < 300) or \
                (success_status_code == response.status_code):
            return response

        # teradataml API got an error response. Error response is expected as follows -
        # {
        #     "status": 404,
        #     "req_id": "1122.3.1",
        #     "error_code": "201",
        #     "error_description": "Environment not found."
        # }
        # Extract the fields and raise error accordingly.

        add_paranthesis = lambda msg: "({})".format(msg) if msg else msg

        data = response.json()
        request_id = add_paranthesis(data.get("req_id", ""))
        error_code = add_paranthesis(data.get("error_code", ""))
        error_description = "{}{} {}".format(request_id, error_code, data.get("error_description", ""))

        exception_message = "Request Failed - {}".format(error_description)

        error_msg = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                         api_name,
                                         exception_message)
        raise TeradataMlException(error_msg, MessageCodes.FUNC_EXECUTION_FAILED)

    # teradataml API may not get a Json API response in some cases.
    # So, raise an error with the response received as it is.
    except JSONDecodeError:
        error_msg = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                         api_name,
                                         response.text)
        raise TeradataMlException(error_msg, MessageCodes.FUNC_EXECUTION_FAILED)


def _get_auth_token():
    """
    DESCRIPTION:
        Internal function to get Authentication token for all UES REST calls

    PARAMETERS:
        None

    RETURNS:
        dict

    RAISES:
        TeradataMlException

    EXAMPLES:
        >>>_get_auth_token()
    """
    '''
    # Check the current time. If token is expiring, get another one from refresh token.
    if configure._auth_token_expiry_time and time.time() > configure._auth_token_expiry_time:
        # Extract the base URL from "ues_url".
        ues_url = configure.ues_url
        client_id = configure._oauth_client_id

        url_parser = urlparse(ues_url)
        base_url = "{}://{}".format(url_parser.scheme, url_parser.netloc)

        # Get the access token.
        da_wf = _DAWorkflow(base_url, client_id)
        token_data = da_wf._get_token_data()

        # Replace the options with new values.
        configure.auth_token = token_data["access_token"]
        configure._auth_token_expiry_time = time.time() + token_data["expires_in"] - 15
    '''
    return {"Authorization": "Bearer {}".format(configure.auth_token)}


class UserEnv:

    def __init__(self, env_name, base_env, desc=None):
        """
        DESCRIPTION:
            Represents remote user environment from Vantage Languages Ecosystem.
            The object of the class can be created either by using create_env() function which will
            create a new remote user environment and returns an object of UserEnv class or
            by using get_env() function which will return an object representing the existing remote user environment.

        PARAMETERS:
            env_name:
                Required Argument.
                Specifies the name of the remote user environment.
                Types: str

            base_env:
                Required Argument.
                Specifies base environment interpreter which is used to create remote user environment.
                Types: str

            desc:
                Optional Argument.
                Specifies description associated with the remote user environment.
                Types: str

        RETURNS:
            Instance of the class UserEnv.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create a new environment and get instance of UserEnv class.
            env1 = create_env('testenv', 'python_3.7.9', 'Test environment')

            # Get an object for existing user environment.
            env2 = get_env('testenv')
        """

        # Make sure the initialization happens only using either create_env() or get_env().
        if inspect.stack()[1][3] not in ['create_env', 'get_env']:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.USE_FUNCTION_TO_INSTANTIATE).format("A teradataml UserEnv object",
                                                                 "create_env() and get_env() functions from teradataml.scriptmgmt.lls_utils"),
                                      MessageCodes.USE_FUNCTION_TO_INSTANTIATE)

        self.env_name = env_name
        self.base_env = base_env
        self.desc = desc

        # Initialize variables to store files and libraries from the remote user environment.
        self.__files = None
        self.__libs = None

        # This variable will be used to detect if files from the remote user environment are changed by
        # install_file or remove_file functions.
        self.__files_changed = None

        # This variable will be used to detect if libraries from the remote user environment are changed by
        # install_lib, remove_lib or update_lib functions in teradataml.
        # Updates from only current session are recorded by this variable.
        self.__libs_changed = None

        # This variable will be set to False when remove() method is called to indicate that.
        self.__exists = True

        # Create argument information matrix to do parameter checking
        self.__arg_info_matrix = []
        self.__arg_info_matrix.append(["env_name", self.env_name, False, (str), True])
        self.__arg_info_matrix.append(["base_env", self.base_env, False, (str), True])
        self.__arg_info_matrix.append(["desc", self.desc, True, (str), False])

        # Argument validation.
        _Validators._validate_function_arguments(self.__arg_info_matrix)

        # Map to store the claim id and corresponding file.
        self.__claim_ids = {}

        # Define the order of columns in output DataFrame.
        self.__status_columns = ['Claim Id', 'File/Libs', 'Method Name', 'Stage', 'Timestamp', 'Additional Details']

    def install_file(self, file_path, replace=False, **kwargs):
        """
        DESCRIPTION:
            Function installs or replaces a file from client machine to the remote user environment created in
            Vantage Languages Ecosystem.
            * If the size of the file is more than 10 MB, the function installs the file synchronously
              and returns the status of installation when 'asynchronous' is set to False. Otherwise, the
              function installs the file asynchronously and returns claim-id to check the installation status
              using status().
            * If the size of the file is less than or equal to 10 MB, the function installs the
              file synchronously and returns the status of installation.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute or relative path of the file (including file name) to be installed in the
                remote user environment.
                Types: str

            replace:
                Optional Argument.
                Specifies if the file should be forcefully replaced in remote user environment.
                * When set to True,
                   * If the file already exists in remote user environment, it will be replaced with the file
                     specified by argument "file_path".
                   * If the file does not already exist in remote user environment, then the specified file will
                     be installed.
                * Argument is ignored when file size <= 10MB.
                Default Value: False
                Types: bool

        **kwargs:
            Specifies the keyword arguments.
                suppress_output:
                    Optional Argument.
                    Specifies whether to print the output message or not.
                    When set to True, then the output message is not printed.
                    Default Value: False
                    Types: bool

            asynchronous:
                Optional Argument.
                Specifies whether to install the file in remote user environment
                synchronously or asynchronously. When set to True, file is installed
                asynchronously. Otherwise, file is installed synchronously.
                Note:
                    Argument is ignored when file size <= 10MB.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for installing the file. If the file is
                not installed with in "timeout" seconds, the function returns a claim-id and one
                can check the status using the claim-id. If "timeout" is not specified, then there
                is no limit on the wait time.
                Note:
                     Argument is ignored when "asynchronous" is True.
                Types: int OR float

        RETURNS:
            True, if the file size is less than or equal to 10 MB and operation is successful.
            str(claim-id), if the file size is greater than 10 MB.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.

            # Example 1: Install the file mapper.py in the 'testenv' environment.
            >>> import os, teradataml
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.py")
            >>> env.install_file(file_path = file_path)
            File 'mapper.py' installed successfully in the remote user environment 'testenv'.

            # Example 2: Replace the file mapper.py.
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.py")
            >>> env.install_file(file_path = file_path, replace=True)
            File 'mapper.py' replaced successfully in the remote user environment 'testenv'.

            # Example 3: Install the file 'large_file' asynchronously with 'large_file' found in
                         temp folder and check the status of installation.
            # Note:
            #     Running this example creates a file 'large_file' with size
            #     approximately 11MB in the temp folder.
            >>> import tempfile, os
            >>> def create_large_file():
            ...     file_name = os.path.join(tempfile.gettempdir(),"large_file")
            ...     with open(file_name, 'xb') as fp:
            ...         fp.seek((1024 * 1024 * 11) - 1)
            ...         fp.write(b'\0')
            ...
            >>> create_large_file()
            >>> claim_id = env.install_file(file_path = os.path.join(tempfile.gettempdir(),"large_file"), asynchronous=True)
            File installation is initiated. Check the status using status() with the claim id 76588d13-6e20-4892-9686-37768adcfadb.
            >>> env.status(claim_id)
                                            Claim Id              File/Libs    Method Name               Stage             Timestamp Additional Details
            0   76588d13-6e20-4892-9686-37768adcfadb             large_file   install_file       File Uploaded  2022-07-13T10:34:02Z               None
            >>> env.status(claim_id, stack=True)
                                            Claim Id              File/Libs    Method Name               Stage             Timestamp Additional Details
            0   76588d13-6e20-4892-9686-37768adcfadb             large_file   install_file  Endpoint Generated  2022-07-13T10:34:00Z               None
            1   76588d13-6e20-4892-9686-37768adcfadb             large_file   install_file       File Uploaded  2022-07-13T10:34:02Z               None
            2   76588d13-6e20-4892-9686-37768adcfadb             large_file   install_file      File Installed  2022-07-13T10:34:08Z               None

            # Example 4: Install the file 'large_file' synchronously with 'large_file' found in
                         temp folder and check the status of installation.
            # Note:
            #     Running this example creates a file 'large_file' with size
            #     approximately 11MB in the temp folder.
            >>> import tempfile, os
            >>> def create_large_file():
            ...     file_name = os.path.join(tempfile.gettempdir(), "large_file")
            ...     with open(file_name, 'xb') as fp:
            ...         fp.seek((1024 * 1024 * 11) - 1)
            ...         fp.write(b'\0')
            ...
            >>> create_large_file()
            >>> result = env.install_file(file_path = os.path.join(tempfile.gettempdir(),"large_file"))

            >>> result
                                            Claim Id              File/Libs    Method Name               Stage             Timestamp Additional Details
            0   87588d13-5f20-3461-9686-46668adcfadb             large_file   install_file  Endpoint Generated  2022-07-13T10:34:00Z               None
            1   87588d13-5f20-3461-9686-46668adcfadb             large_file   install_file       File Uploaded  2022-07-13T10:34:02Z               None
            2   87588d13-5f20-3461-9686-46668adcfadb             large_file   install_file      File Installed  2022-07-13T10:34:08Z               None

            >>> os.remove(os.path.join(tempfile.gettempdir(),"large_file")) # Remove the file created using function 'create_large_file'.

            # Remove the environment.
            >>> remove_env('testenv')
            User environment 'testenv' removed.
        """
        # Install/Replace file on Vantage
        asynchronous = kwargs.get("asynchronous", False)
        timeout = kwargs.get("timeout")
        user_name = kwargs.get("user")
        suppress_output = kwargs.get("suppress_output", False)
        __arg_info_matrix = []
        __arg_info_matrix.append(["file_path", file_path, False, (str), True])
        __arg_info_matrix.append(["replace", replace, True, (bool)])
        __arg_info_matrix.append(["asynchronous", asynchronous, True, (bool)])
        __arg_info_matrix.append(["timeout", timeout, True, (int, float)])
        __arg_info_matrix.append(["suppress_output", suppress_output, True, (bool)])

        # Argument validation.
        _Validators._validate_function_arguments(__arg_info_matrix)

        # Check if file exists or not.
        _Validators._validate_file_exists(file_path)

        try:
            # If file size is more than 10 MB, upload the file to cloud and export it to UES.
            if UtilFuncs._get_file_size(file_path) > configure._ues_max_file_upload_size:
                res = self.__install_file_from_cloud(file_path,user_name,asynchronous, timeout, suppress_output)
            else:
                res = self.__install_file_from_local(file_path,replace,user_name, suppress_output)
            self.__files_changed = True
            return res

        except (TeradataMlException, RuntimeError):
            raise

        except Exception as emsg:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "install_file", str(emsg))
            raise TeradataMlException(error_msg, msg_code)

    def __install_file_from_local(self, file_path, replace,user=None, suppress_output=False):
        """
        DESCRIPTION:
            Internal function to install or replace a file from client machine to the remote
            user environment created in Vantage Languages Ecosystem.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute or relative path of the file (including file name) to be installed in the
                remote user environment.
                Types: str

            replace:
                Required Argument.
                Specifies if the file should be forcefully replaced in remote user environment.
                When set to True,
                    * If the file already exists in remote user environment, it will be replaced with the file
                      specified by argument "file_path".
                    * If the file does not already exist in remote user environment, then the specified file will
                      be installed.
                Types: bool

            suppress_output:
                Optional Argument.
                Specifies whether to print the output message or not.
                When set to True, then the output message is not printed.
                Default Value: False
                Types: bool

        RETURNS:
            True, if the operation is successful.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.
            >>> env.__install_file_from_local("abc.py")
            File 'abc.py' is installed successfully in 'testenv' environment.
        """
        file_name = os.path.basename(file_path)

        # Prepare the payload.
        files = {
            'env-file': (file_name, UtilFuncs._get_file_contents(file_path, read_in_binary_mode=True))
        }

        http_method = HTTPRequest.POST
        success_msg = "installed"
        params = {"env_name": self.env_name, "files": True, "api_name": "install_file"}

        if replace:
            http_method = HTTPRequest.PUT
            success_msg = "replaced"
            params["file_name"] = file_name
        #SNIGDHA
        resource_url = _get_ues_url(user_name=user,**params)
        # UES accepts multiform data. Specifying the 'files' attribute makes 'requests'
        # module to send it as multiform data.
        resp = UtilFuncs._http_request(resource_url, http_method, headers=_get_auth_token(), files=files)

        # Process the response.
        _process_ues_response(api_name="install_file", response=resp)

        if not suppress_output:
            print("File '{}' {} successfully in the remote user environment '{}'.".format(
                  file_name, success_msg, self.env_name))

        return True

    @staticmethod
    def __upload_file_to_cloud(file_path,user_name=None):
        """
        DESCRIPTION:
            Internal function to upload a file to the cloud environment.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute or relative path of the file (including file name) to be uploaded
                to the cloud.
                Types: str

        RETURNS:
            str, if the operation is successful.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.
            >>> env.__upload_file_to_cloud("abc.txt")
        """
        # Prepare the payload for UES to get the URL and claim-id.
        payload = {"user": user_name, "file": os.path.basename(file_path)}

        response = UtilFuncs._http_request(_get_ues_url(env_type="fm",user_name=user_name, fm_type="import", api_name="install_file"),
                                           HTTPRequest.POST,
                                           json=payload,
                                           headers=_get_auth_token())
        data = _process_ues_response("install_file", response).json()

        # Get the URL to upload file to cloud and the claim-id from response.
        cloud_storage_url, claim_id = data["url"], data["claim_id"]

        # Initiate file upload to cloud.
        response = UtilFuncs._http_request(cloud_storage_url,
                                           HTTPRequest.PUT,
                                           data=UtilFuncs._get_file_contents(file_path, read_in_binary_mode=True))

        # Since the API is not for UES, it is better to validate and raise error separately.
        if response.status_code != 200:
            raise Exception("File upload failed with status code - {}".format(response.status_code))

        return claim_id

    def __install_file_from_cloud(self, file_path,user_name=None, asynchronous=False, timeout=None, suppress_output=False):
        """
        DESCRIPTION:
            Internal Function to export file from cloud environment to the remote user
            environment created in Vantage Languages Ecosystem.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute or relative path of the file (including file name) to
                be installed in the remote user environment.
                Types: str

            asynchronous:
                Optional Argument.
                Specifies whether to install the file in remote user environment
                synchronously or asynchronously. When set to True, file is installed
                asynchronously. Otherwise, file is installed synchronously.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for installing the file. If the file is
                not installed with in "timeout" seconds, the function returns a claim-id and one
                can check the status using the claim-id. If "timeout" is not specified, then there
                is no limit on the wait time.
                Note:
                     Argument is ignored when "asynchronous" is True.
                Types: int OR float

            suppress_output:
                Optional Argument.
                Specifies whether to print the output message or not.
                When set to True, then the output message is not printed.
                Default Value: False
                Types: bool

        RETURNS:
            str, if the operation is successful.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.
            >>> env.__install_file_from_cloud("abc.py")
            File installation is initiated. Check the status using 'status' API with the claim id abc-xyz.
            abc-xyz
        """
        # Upload file to cloud.
        claim_id = self.__upload_file_to_cloud(file_path,user_name)

        # Initiate file export from cloud to UES file system. Note that, the corresponding call to
        # UES is an asynchronous call.
        data = {"user": user_name,
                "environment": self.env_name,
                "claim_id": claim_id
                }
        url = _get_ues_url(env_type="fm", user_name=user_name,fm_type="export", claim_id=claim_id, api_name="install_file")
        response = UtilFuncs._http_request(url, HTTPRequest.POST, json=data, headers=_get_auth_token())

        # Validate the response.
        _process_ues_response("install_file", response)

        # Store the claim id locally to display the file/library name in status API.
        self.__claim_ids[claim_id] = {"action": "install_file", "value": file_path}

        if not asynchronous:
            return self.__get_claim_status(claim_id, timeout, "install file")

        if not suppress_output:
            # Print a message to user console.
            print("File installation is initiated. Check the status"
                  " using status() with the claim id {}.".format(claim_id))

        return claim_id

    def remove_file(self, file_name, **kwargs):
        """
        DESCRIPTION:
            Function removes the specified file from the remote user environment.

        PARAMETERS:
            file_name:
                Required Argument.
                Specifies the file name to be removed. If the file has an extension, specify the filename with extension.
                Types: str

        **kwargs:
            Specifies the keyword arguments.
                suppress_output:
                    Optional Argument.
                    Specifies whether to print the output message or not.
                    When set to True, then the output message is not printed.
                    Types: bool

        RETURNS:
            True, if the operation is successful.

        RAISES:
            TeradataMlException, RuntimeError

        EXAMPLES:
            # Create a Python 3.7.3 environment with given name and description in Vantage.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment 'testenv' created.
            # Install the file "mapper.py" using the default text mode in the remote user environment.
            >>> import os, teradataml
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.py")
            >>> env.install_file(file_path = file_path)
                File 'mapper.py' replaced successfully in the remote user environment 'testenv'.

            # Example 1: Remove file from remote user environment.
            >>> env.remove_file('mapper.py')
            File 'mapper.py' removed successfully from the remote user environment 'testenv'.

            # Remove the environment.
            >>> remove_env('testenv')
            User environment 'testenv' removed.
        """
        user_name = kwargs.get("user")

        __arg_info_matrix = []
        __arg_info_matrix.append(["file_name", file_name, False, (str), True])
        __arg_info_matrix.append(["suppress_output", kwargs.get("suppress_output", False), True, (bool)])

        # Argument validation.
        _Validators._validate_missing_required_arguments(__arg_info_matrix)
        _Validators._validate_function_arguments(__arg_info_matrix)

        try:
            response = UtilFuncs._http_request(_get_ues_url(env_name=self.env_name,user_name=user_name, files=True, file_name=file_name),
                                               HTTPRequest.DELETE,
                                               headers=_get_auth_token())
            _process_ues_response(api_name="remove_file", response=response)

            if not kwargs.get("suppress_output", False):
                print("File '{0}' removed successfully from the remote user environment '{1}'.".
                      format(file_name, self.env_name))

            # Files are changed, change the flag.
            self.__files_changed = True
            return True

        except (TeradataMlException, RuntimeError):
            raise
        except Exception as err:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "remove_file", err)
            raise TeradataMlException(error_msg, msg_code)

    #@property
    def files(self,**kwargs):
        """
        DESCRIPTION:
            A class property that returns list of files installed in remote user environment.

        PARAMETERS:
            None

        RETURNS:
            Pandas DataFrame containing files and it's details.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create a remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.

            >>> env.install_file(file_path = 'data/scripts/mapper.py')
            File mapper.py installed successfully in the remote user environment testenv.

            # List files installed in the user environment.
            >>> env.files
                    file	size	last_updated_dttm
            0	mapper.py	233	    2020-08-06T21:59:22Z
        """
        # Fetch the list of files from remote user environment only when they are not already fetched in this object
        # or files are changed either by install or remove functions.
        user_name = kwargs.get("user")
        if self.__files is None or self.__files_changed:
            self._set_files(user=user_name)

        if len(self.__files) == 0:
            print("No files found in remote user environment {}.".format(self.env_name))
        else:
            return self.__files

    def _set_files(self,**kwargs):
        """
        DESCRIPTION:
            Function fetches the list of files installed in a remote user environment using
            the REST call to User Environment Service.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> self._set_files()
        """

        try:
            user_name = kwargs.get("user")

            response = UtilFuncs._http_request(_get_ues_url(env_name=self.env_name,user_name=user_name, files=True, api_name="files"),
                                               headers=_get_auth_token())
            data = _process_ues_response(api_name="files", response=response).json()

            if len(data) > 0:
                self.__files = pd.DataFrame.from_records(data)
            else:
                self.__files = pd.DataFrame(columns=["file", "size", "last_updated_dttm"])

            # Latest files are fetched; reset the flag.
            self.__files_changed = False

        except (TeradataMlException, RuntimeError):
            raise

        except Exception as err:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "files", err)
            raise TeradataMlException(error_msg, msg_code)

    def _set_libs(self,**kwargs):

        """
        DESCRIPTION:
            Function lists the installed libraries in the remote user environment using
            the REST call to User Environment Service and sets the '__libs' data member.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            self._set_libs()
        """
        try:
            user_name = kwargs.get("user")

            response = UtilFuncs._http_request(_get_ues_url(env_name=self.env_name,user_name=user_name, libs=True, api_name="libs"),
                                               headers=_get_auth_token())
            data = _process_ues_response(api_name="libs", response=response).json()

            if len(data) > 0:
                # Return result as Pandas dataframe.
                df = pd.DataFrame.from_records(data)
                self.__libs = df

            # Latest libraries are fetched; reset the flag.
            self.__libs_changed = False

        except (TeradataMlException, RuntimeError):
            raise
        except Exception as emsg:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "libs", emsg)
            raise TeradataMlException(error_msg, msg_code)

    #@property
    def libs(self,**kwargs):
        """
        DESCRIPTION:
            A class property that returns list of libraries installed in the remote user environment.

        PARAMETERS:
            None

        RETURNS:
            Pandas DataFrame containing libraries and their versions.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create a remote user environment.
            >>> env = create_env('test_env', 'python_3.7.9', 'Test environment')
            User environment test_env created.

            # View existing libraries installed.
            >>> env.libs
                     name version
            0         pip  20.1.1
            1  setuptools  47.1.0

            # Install additional Python libraries.
            >>> env.install_lib(['numpy','nltk>=3.3'])
            Request to install libraries initiated successfully in the remote user environment test_env. Check the status using status() with the claim id '1e23d244-3c88-401f-a432-277d72dc6835'.
            '1e23d244-3c88-401f-a432-277d72dc6835'

            # List libraries installed.
            >>> env.libs
                     name version
            0        nltk   3.4.5
            1       numpy  1.21.6
            2         pip  20.1.1
            3  setuptools  47.1.0
            4         six  1.16.0

        """
        # Fetch the list of libraries from remote user environment only when they are not
        # already fetched in this object or libraries are changed either by
        # install_lib/uninstall_lib/update_lib functions.
        user_name = kwargs.get("user")

        if self.__libs is None or self.__libs_changed:
            self._set_libs(user=user_name)

        return self.__libs

    def __manage(self, file_contents,user_name=None, option="INSTALL"):
        """
        DESCRIPTION:
            Function installs, removes and updates Python libraries from
            remote user environment.

        PARAMETERS:
            file_contents:
                Required Argument.
                Specifies the contents of the file in binary format.
                Types: binary

            option:
                Required Argument.
                Specifies the action intended to be performed on the libraries.
                Permitted Values: INSTALL, UNINSTALL, UPDATE
                Types: str
                Default Value: INSTALL

        RETURNS:
            True, if the operation is successful.

        RAISES:
            TeradataMlException, SqlOperationalError

        EXAMPLES:
            self.__manage(b'pandas' ,"INSTALL")
            self.__manage(b'pandas', "UNINSTALL")
            self.__manage(b'pandas', "UPDATE")
        """
        # Common code to call XSP manage_libraries with options "INSTALL", "UNINSTALL", "update"
        # This internal method will be called by install_lib, uninstall_lib and update_lib.
        __arg_info_matrix = []
        __arg_info_matrix.append(["option", option, False, (str), True, ["INSTALL", "UNINSTALL", "UPDATE"]])

        # Validate arguments
        _Validators._validate_missing_required_arguments(__arg_info_matrix)
        _Validators._validate_function_arguments(__arg_info_matrix)

        try:
            # Prepare the payload.
            # Update the action to 'UPGRADE' for the post call as the UES accepts 'UPGRADE'.
            http_req = HTTPRequest.POST
            if option == "UPDATE":
                http_req = HTTPRequest.PUT
            elif option == "UNINSTALL":
                http_req = HTTPRequest.DELETE

            files = {
                'reqs-file': ("requirements.txt", file_contents),
            }

            # Get the API name (install_lib or uninstall_lib or update_lib) which calls
            # __manage_libraries which ends up calling this function.
            api_name = inspect.stack()[2].function

            # UES accepts multiform data. Specifying the 'files' attribute makes 'requests'
            # module to send it as multiform data.
            resp = UtilFuncs._http_request(url=_get_ues_url(env_name=self.env_name,user_name=user_name, libs=True, api_name=api_name),
                                           method_type=http_req,
                                           headers=_get_auth_token(),
                                           files=files)

            # Process the response.
            resp = _process_ues_response(api_name="{}_lib".format(option.lower()), response=resp)
            # Set the flag to indicate that libraries are changed in remote user environment.
            self.__libs_changed = True
            return resp.json().get("claim_id", "")

        except (TeradataMlException, RuntimeError):
            raise
        except Exception as emsg:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "{}_lib".format(option.lower()), str(emsg))
            raise TeradataMlException(error_msg, msg_code)

    def __validate(self, libs=None, libs_file_path=None, asynchronous=True, timeout=None):
        """
        DESCRIPTION:
            Function performs argument validations.

        PARAMETERS:
            libs:
                Optional Argument.
                Specifies the add-on library name(s).
                Types: str OR list of Strings(str)

            libs_file_path:
                Optional Argument.
                Specifies file path with extension.
                Types: str

            asynchronous:
                Optional Argument.
                Specifies whether to install/uninstall/update the library in remote user environment
                synchronously or asynchronously. When set to True, libraries are installed/uninstalled/updated
                asynchronously. Otherwise, libraries are installed/uninstalled/updated synchronously.
                Default Value: True
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for installing the libraries. If the library is
                not installed/uninstalled/updated with in 'timeout' seconds, the function returns a
                claim-id and one can check the status using the claim-id. If 'timeout' is not specified,
                then there is no limit on the wait time.
                Types: int OR float

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            __validate_requirement_filename(libs_file_path = 'data/requirements.txt')
            __validate_requirement_filename(libs="numpy")
            __validate_requirement_filename(libs=['pandas','numpy'])
        """
        __arg_info_matrix = []
        __arg_info_matrix.append(["libs", libs, True, (str, list), True])
        __arg_info_matrix.append(["libs_file_path", libs_file_path, True, str, True])
        __arg_info_matrix.append(["asynchronous", asynchronous, True, bool])
        __arg_info_matrix.append(["timeout", timeout, True, (int, float)])

        # Argument validation.
        _Validators._validate_missing_required_arguments(__arg_info_matrix)
        _Validators._validate_function_arguments(__arg_info_matrix)
        _Validators._validate_mutually_exclusive_arguments(libs, "libs", libs_file_path, "libs_file_path")

        if libs_file_path is not None:
            # If user has specified libraries in a file.
            _Validators._validate_file_exists(libs_file_path)

            # Verify only files with .txt extension are allowed.
            _Validators._validate_file_extension(libs_file_path, ".txt")
            _Validators._check_empty_file(libs_file_path)

        if timeout is not None:
            _Validators._validate_argument_range(timeout, 'timeout', lbound=0, lbound_inclusive=False)

    def __manage_libraries(self, libs=None, libs_file_path=None, user_name=None, action="INSTALL", asynchronous=False, timeout=None):
        """
        DESCRIPTION:
            Internal function to perform argument validation, requirement text file
            generation and executing XSP call to get the results.

        PARAMETERS:
            libs:
                Optional Argument.
                Specifies the add-on library name(s).
                Types: str OR list of Strings(str)

            libs_file_path:
                Optional Argument.
                Specifies the absolute/relative path of the text file (including file name)
                which supplies a list of libraries to be installed in remote user
                environment. Path specified should include the filename with extension.
                Note:
                    1. The file must have an ".txt" extension.
                    2. Either libs or libs_file_path argument must be specified.
                Types: str

            action:
                Optional Argument.
                Specifies if libraries are to be installed or uninstalled or updated
                from remote user environment.
                Default Value: 'INSTALL'
                Types: str

            asynchronous:
                Optional Argument.
                Specifies whether to install/uninstall/update the library in
                remote user environment synchronously or asynchronously. When
                set to True, libraries are installed/uninstalled/updated asynchronously.
                Otherwise, libraries are installed/uninstalled/updated synchronously.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the the maximum number of seconds to install/uninstall/update
                the libraries in remote user environment. If None, then there is
                no limit on the wait time.
                * Argument is ignored when 'asynchronous' is True.
                Types: int OR float

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            __manage_libraries(libs_file_path="/data/requirement.txt", action="INSTALL")
            __manage_libraries(libs="pandas", action="UNINSTALL")
            __manage_libraries(libs=["pandas","numpy","joblib==0.13.2"], action="UPDATE")
        """
        # Argument validation.
        self.__validate(libs, libs_file_path, asynchronous, timeout)

        # If file is provided, store the file_name and also extracts it contents
        if libs_file_path is not None:
            value = libs_file_path
            file_contents = UtilFuncs._get_file_contents(libs_file_path, read_in_binary_mode=True)
        else:
            # If libs are provided as string or list, convert the contents to binary.
            file_contents = libs
            # When library names are provided in a list, create a string.
            if isinstance(libs, list):
                file_contents = '\n'.join(libs)
            # Store it with comma separated values if it is a list.
            value = ', '.join(libs) if isinstance(libs, list) else libs
            # Convert to binary.
            file_contents = file_contents.encode('ascii')

        claim_id = self.__manage(file_contents,user_name, action)
        action = action.lower()
        self.__claim_ids[claim_id] = {"action": "{}_lib".format(action), "value": value}

        # Check if installation should be asynchronous or not. If it is, then
        # return claim id and let user to poll the status using status API.
        # Else, poll the status API for 'timeout' seconds.
        if asynchronous:
            print("Request to {} libraries initiated successfully in the remote user environment {}. "
                  "Check the status using status() with the claim id '{}'.".format(
                   action, self.env_name, claim_id))
            return claim_id
        else:
            return self.__get_claim_status(claim_id, timeout, "{} libraries".format(action))

    def install_lib(self, libs=None, libs_file_path=None, **kwargs):
        """
        DESCRIPTION:
            Function installs Python libraries in the remote user environment.

        PARAMETERS:
            libs:
                Optional Argument.
                Specifies the add-on library name(s).
                Types: str OR list of Strings(str)

            libs_file_path:
                Optional Argument.
                Specifies the absolute/relative path of the text file (including file name)
                which supplies a list of libraries to be installed in remote user environment.
                Path specified should include the filename with extension.
                The file should contain library names and version number(optional) of libraries.
                The file should contain library names and version number(optional) of libraries.
                Note:
                    This file format should adhere to the specification of the requirements file
                    used to install Python libraries with pip install command.
                Sample text file contents:
                    numpy
                    joblib==0.13.2
                Note:
                    1. The file must have an ".txt" extension.
                    2. Either libs or libs_file_path argument must be specified.
                Types: str

        **kwargs:
            asynchronous:
                Optional Argument.
                Specifies whether to install the library in remote user environment
                synchronously or asynchronously. When set to True, libraries are installed
                asynchronously. Otherwise, libraries are installed synchronously.
                Note:
                    One should not use remove_env() on the same environment till the
                    asynchronous call is complete.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for installing the libraries. If the library is
                not installed with in "timeout" seconds, the function returns a claim-id and one
                can check the status using the claim-id. If "timeout" is not specified, then there
                is no limit on the wait time.
                Note:
                     Argument is ignored when "asynchronous" is True.
                Types: int OR float

        RETURNS:
            Pandas DataFrame when libraries are installed synchronously.
            claim_id, to track status when libraries are installed asynchronously.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.

            # Example 1: Install single Python library asynchronously.
            >>> env.install_lib('numpy', asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '4b062b0e-6e9f-4996-b92b-5b20ac23b0f9'.

            # Check the status.
            >>> env.status('4b062b0e-6e9f-4996-b92b-5b20ac23b0f9')
                                           Claim Id File/Libs  Method Name     Stage             Timestamp Additional Details
            0  4b062b0e-6e9f-4996-b92b-5b20ac23b0f9     numpy  install_lib   Started  2022-07-13T11:07:34Z               None
            1  4b062b0e-6e9f-4996-b92b-5b20ac23b0f9     numpy  install_lib  Finished  2022-07-13T11:07:35Z               None
            >>>

            # Verify if libraries are installed.
            >>> env.libs
                  library version
            0       numpy  1.21.6
            1         pip  20.1.1
            2  setuptools  47.1.0

            # Example 2: Install libraries asynchronously by passing them as list of library names.
            >>> env.install_lib(["pandas",
            ...                   "joblib==0.13.2",
            ...                   "scikit-learn",
            ...                   "numpy>=1.17.1",
            ...                   "nltk>=3.3,<3.5"], asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '90aae7df-5efe-4b5a-af26-150aab35f1fb'.

            # Check the status.
            >>> env.status('90aae7df-5efe-4b5a-af26-150aab35f1fb')
                                           Claim Id                                                           File/Libs  Method Name     Stage             Timestamp Additional Details
            0  90aae7df-5efe-4b5a-af26-150aab35f1fb pandas, joblib==0.13.2, scikit-learn, numpy>=1.17.1, nltk>=3.3,<3.5  install_lib   Started  2022-07-13T11:09:39Z               None
            1  90aae7df-5efe-4b5a-af26-150aab35f1fb pandas, joblib==0.13.2, scikit-learn, numpy>=1.17.1, nltk>=3.3,<3.5  install_lib  Finished  2022-07-13T11:09:40Z               None

            # Verify if libraries are installed with specific version.
            >>> env.libs
                        library version
            0            joblib  0.13.2
            1              nltk   3.4.5
            2             numpy  1.21.6
            3            pandas   1.3.5
            4               pip  20.1.1
            5   python-dateutil   2.8.2
            6              pytz  2022.1
            7      scikit-learn   1.0.2
            8             scipy   1.7.3
            9        setuptools  47.1.0
            10              six  1.16.0
            11    threadpoolctl   3.1.0

            # Example 3: Install libraries synchronously by passing them as list of library names.
            >>> env.install_lib(["Flask", "gunicorn"])
                                           Claim Id        File/Libs  Method Name     Stage             Timestamp Additional Details
            0  ebc11a82-4606-4ce3-9c90-9f54d1260f47  Flask, gunicorn  install_lib   Started  2022-08-12T05:35:58Z
            1  ebc11a82-4606-4ce3-9c90-9f54d1260f47  Flask, gunicorn  install_lib  Finished  2022-08-12T05:36:13Z
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
                              name version
            0                click   8.1.3
            1                Flask   2.2.2
            2             gunicorn  20.1.0
            3   importlib-metadata  4.12.0
            4         itsdangerous   2.1.2
            5               Jinja2   3.1.2
            6               joblib  0.13.2
            7           MarkupSafe   2.1.1
            8                 nltk   3.4.5
            9                numpy  1.21.6
            10              pandas   1.3.5
            11                 pip  20.1.1
            12     python-dateutil   2.8.2
            13                pytz  2022.2
            14        scikit-learn   1.0.2
            15               scipy   1.7.3
            16          setuptools  64.0.1
            17                 six  1.16.0
            18       threadpoolctl   3.1.0
            19   typing-extensions   4.3.0
            20            Werkzeug   2.2.2
            21                zipp   3.8.1
            >>>

            # Example 4: Install libraries synchronously by passing them as list of library names within a
            #            specific timeout of 5 seconds.
            >>> env.install_lib(["teradataml",  "teradatasqlalchemy"], timeout=5)
            Request to install libraries initiated successfully in the remote user environment 'testenv' but unable to get the status. Check the status using status() with the claim id '30185e0e-bb09-485a-8312-c267fb4b3c1b'.
            '30185e0e-bb09-485a-8312-c267fb4b3c1b'

            # Check the status.
            >>> env.status('30185e0e-bb09-485a-8312-c267fb4b3c1b')
                                           Claim Id                       File/Libs  Method Name     Stage             Timestamp Additional Details
            0  30185e0e-bb09-485a-8312-c267fb4b3c1b  teradataml, teradatasqlalchemy  install_lib   Started  2022-08-12T05:42:58Z
            1  30185e0e-bb09-485a-8312-c267fb4b3c1b  teradataml, teradatasqlalchemy  install_lib  Finished  2022-08-12T05:43:29Z
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
                              name    version
            0              certifi  2022.6.15
            1   charset-normalizer      2.1.0
            2                click      8.1.3
            3               docker      5.0.3
            4                Flask      2.2.2
            5             greenlet      1.1.2
            6             gunicorn     20.1.0
            7                 idna        3.3
            8   importlib-metadata     4.12.0
            9         itsdangerous      2.1.2
            10              Jinja2      3.1.2
            11              joblib     0.13.2
            12          MarkupSafe      2.1.1
            13                nltk      3.4.5
            14               numpy     1.21.6
            15              pandas      1.3.5
            16                 pip     20.1.1
            17              psutil      5.9.1
            18        pycryptodome     3.15.0
            19     python-dateutil      2.8.2
            20                pytz     2022.2
            21            requests     2.28.1
            22        scikit-learn      1.0.2
            23               scipy      1.7.3
            24          setuptools     64.0.1
            25                 six     1.16.0
            26          SQLAlchemy     1.4.40
            27          teradataml  17.10.0.1
            28         teradatasql  17.20.0.1
            29  teradatasqlalchemy   17.0.0.3
            30       threadpoolctl      3.1.0
            31   typing-extensions      4.3.0
            32             urllib3    1.26.11
            33    websocket-client      1.3.3
            34            Werkzeug      2.2.2
            35                zipp      3.8.1
            >>>

            # Example 5: Install libraries asynchronously by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            pandas
            joblib==0.13.2
            scikit-learn
            numpy>=1.17.1
            nltk>=3.3,<3.5
            -----------------------------------------------------------

            # Install libraries specified in the file.
            >>> env.install_lib(libs_file_path="requirement.txt", asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'f11c7f28-f958-4cae-80a8-926733954bdc'.

            # Check the status.
            >>> env.status('8709b464-f144-4c37-8918-ef6a98ecf295')
                                           Claim Id         File/Libs  Method Name     Stage             Timestamp Additional Details
            0  f11c7f28-f958-4cae-80a8-926733954bdc  requirements.txt  install_lib   Started  2022-07-13T11:23:23Z               None
            1  f11c7f28-f958-4cae-80a8-926733954bdc  requirements.txt  install_lib  Finished  2022-07-13T11:25:37Z               None
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
                        library version
            0            joblib  0.13.2
            1              nltk   3.4.5
            2             numpy  1.21.6
            3            pandas   1.3.5
            4               pip  20.1.1
            5   python-dateutil   2.8.2
            6              pytz  2022.1
            7      scikit-learn   1.0.2
            8             scipy   1.7.3
            9        setuptools  47.1.0
            10              six  1.16.0
            11    threadpoolctl   3.1.0

            # Example 6: Install libraries synchronously by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            matplotlib
            -----------------------------------------------------------

            # Install libraries specified in the file.
            >>> env.install_lib(libs_file_path="requirements.txt")
                                           Claim Id         File/Libs  Method Name     Stage             Timestamp Additional Details
            0  6221681b-f663-435c-80a9-3f99d2af5d83  requirements.txt  install_lib   Started  2022-08-12T05:49:09Z
            1  6221681b-f663-435c-80a9-3f99d2af5d83  requirements.txt  install_lib  Finished  2022-08-12T05:49:41Z
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
                              name    version
            0              certifi  2022.6.15
            1   charset-normalizer      2.1.0
            2                click      8.1.3
            3               cycler     0.11.0
            4               docker      5.0.3
            5                Flask      2.2.2
            6            fonttools     4.34.4
            7             greenlet      1.1.2
            8             gunicorn     20.1.0
            9                 idna        3.3
            10  importlib-metadata     4.12.0
            11        itsdangerous      2.1.2
            12              Jinja2      3.1.2
            13              joblib     0.13.2
            14          kiwisolver      1.4.4
            15          MarkupSafe      2.1.1
            16          matplotlib      3.5.3
            17                nltk      3.4.5
            18               numpy     1.21.6
            19           packaging       21.3
            20              pandas      1.3.5
            21              Pillow      9.2.0
            22                 pip     20.1.1
            23              psutil      5.9.1
            24        pycryptodome     3.15.0
            25           pyparsing      3.0.9
            26     python-dateutil      2.8.2
            27                pytz     2022.2
            28            requests     2.28.1
            29        scikit-learn      1.0.2
            30               scipy      1.7.3
            31          setuptools     64.0.1
            32                 six     1.16.0
            33          SQLAlchemy     1.4.40
            34          teradataml  17.10.0.1
            35         teradatasql  17.20.0.1
            36  teradatasqlalchemy   17.0.0.3
            37       threadpoolctl      3.1.0
            38   typing-extensions      4.3.0
            39             urllib3    1.26.11
            40    websocket-client      1.3.3
            41            Werkzeug      2.2.2
            42                zipp      3.8.1
            >>>
        """
        asynchronous = kwargs.get("asynchronous", False)
        user_name = kwargs.get("user")
        timeout = kwargs.get("timeout")
        claim_id = self.__manage_libraries(libs, libs_file_path,user_name, "INSTALL", asynchronous, timeout)
        return (claim_id)

    def uninstall_lib(self, libs=None, libs_file_path=None, **kwargs):
        """
        DESCRIPTION:
            Function uninstalls Python libraries from remote user environment.

        PARAMETERS:
            libs:
                Optional Argument.
                Specifies the add-on library name(s).
                Types: str OR list of Strings(str)

            libs_file_path:
                Optional Argument.
                Specifies the absolute/relative path of the text file (including file name)
                which supplies a list of libraries to be uninstalled from the remote user
                environment. Path specified should include the filename with extension.
                The file should contain library names and version number(optional) of libraries.
                Note:
                    This file format should adhere to the specification of the requirements file
                    used to uninstall Python libraries with pip uninstall command.
                Sample text file contents:
                    numpy
                    joblib==0.13.2
                Note:
                    1. The file must have an ".txt" extension.
                    2. Either libs or libs_file_path argument must be specified.
                Types: str

        **kwargs:
            asynchronous:
                Optional Argument.
                Specifies whether to uninstall the library in remote user environment
                synchronously or asynchronously. When set to True, libraries are uninstalled
                asynchronously. Otherwise, libraries are uninstalled synchronously.
                Note:
                    One should not use remove_env() on the same environment till the
                    asynchronous call is complete.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for uninstalling the libraries. If the library is
                not uninstalled with in "timeout" seconds, the function returns a claim-id and one
                can check the status using the claim-id. If "timeout" is not specified, then there
                is no limit on the wait time.
                Note:
                     Argument is ignored when "asynchronous" is True.
                Types: int OR float

        RETURNS:
            Pandas DataFrame when libraries are uninstalled synchronously.
            claim_id, to track status when libraries are uninstalled asynchronously.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create remote user environment.
            >>> testenv = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.

            # Example 1: Install and uninstall a single Python library.
            >>> testenv.install_lib('numpy')
                                           Claim Id File/Libs  Method Name     Stage             Timestamp Additional Details
            0  407e644d-3630-4085-8a0b-169406f52340     numpy  install_lib   Started  2022-07-13T11:32:32Z               None
            1  407e644d-3630-4085-8a0b-169406f52340     numpy  install_lib  Finished  2022-07-13T11:32:33Z               None
            >>>

            # Verify installed library.
            >>> testenv.libs
                  library version
            0       numpy  1.21.6
            1         pip  20.1.1
            2  setuptools  47.1.0

            # Uninstall single Python library asynchrnously.
            >>> testenv.uninstall_lib('numpy', asynchronous=True)
            Request to uninstall libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '16036846-b9d7-4c5b-be92-d7cf14aa2016'.

            # Check the status.
            >>> testenv.status('16036846-b9d7-4c5b-be92-d7cf14aa2016')
                                           Claim Id File/Libs    Method Name     Stage             Timestamp Additional Details
            0  16036846-b9d7-4c5b-be92-d7cf14aa2016     numpy  uninstall_lib   Started  2022-07-13T11:33:42Z               None
            1  16036846-b9d7-4c5b-be92-d7cf14aa2016     numpy  uninstall_lib  Finished  2022-07-13T11:33:42Z               None
            >>>

            # Verify library is uninstalled.
            >>> testenv.libs
                library	    version
            0	pip	        20.1.1
            1	setuptools	47.1.0

            # Example 2: Install list of Python libraries asynchronously and uninstall them synchronously.
            >>> testenv.install_lib(["pandas", "scikit-learn"], asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'a91af321-cf57-43cc-b864-a67fa374cb42'.

            # Check the status
            >>> testenv.status('a91af321-cf57-43cc-b864-a67fa374cb42')
                                           Claim Id             File/Libs  Method Name     Stage             Timestamp Additional Details
            0  a91af321-cf57-43cc-b864-a67fa374cb42  pandas, scikit-learn  install_lib   Started  2022-07-13T11:34:38Z               None
            1  a91af321-cf57-43cc-b864-a67fa374cb42  pandas, scikit-learn  install_lib  Finished  2022-07-13T11:36:40Z               None
            >>>

            # Verify libraries are installed along with its dependant libraries.
            >>> testenv.libs
                        library version
            0            joblib   1.1.0
            1             numpy  1.21.6
            2            pandas   1.3.5
            3               pip  20.1.1
            4   python-dateutil   2.8.2
            5              pytz  2022.1
            6      scikit-learn   1.0.2
            7             scipy   1.7.3
            8        setuptools  47.1.0
            9               six  1.16.0
            10    threadpoolctl   3.1.0

            # Uninstall libraries by passing them as a list of library names.
            >>> testenv.uninstall_lib(["pandas", "scikit-learn"])
                                           Claim Id             File/Libs    Method Name     Stage             Timestamp Additional Details
            0  8d6bb524-c047-4aae-8597-b48ab467ef37  pandas, scikit-learn  uninstall_lib   Started  2022-07-13T11:46:55Z               None
            1  8d6bb524-c047-4aae-8597-b48ab467ef37  pandas, scikit-learn  uninstall_lib  Finished  2022-07-13T11:47:20Z               None
            >>>

            # Verify if the specified libraries are uninstalled.
             >>> testenv.libs
                       library version
            0           joblib   1.1.0
            1            numpy  1.21.6
            2              pip  20.1.1
            3  python-dateutil   2.8.2
            4             pytz  2022.1
            5            scipy   1.7.3
            6       setuptools  47.1.0
            7              six  1.16.0
            8    threadpoolctl   3.1.0

            # Example 3: Install and uninstall libraries specified in
            #            requirement text file asynchronously.

            # Install libraries by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            pandas
            joblib==0.13.2
            scikit-learn
            numpy>=1.17.1
            nltk>=3.3,<3.5
            -----------------------------------------------------------

            # Install libraries specified in the file.
            >>> testenv.install_lib(libs_file_path="requirements.txt", asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'c3669eea-327c-453f-b068-6b5f3f4768a5'.

            # Check the status.
            >>> testenv.status('c3669eea-327c-453f-b068-6b5f3f4768a5')
                                           Claim Id         File/Libs  Method Name     Stage             Timestamp Additional Details
            0  c3669eea-327c-453f-b068-6b5f3f4768a5  requirements.txt  install_lib   Started  2022-07-13T11:48:46Z               None
            1  c3669eea-327c-453f-b068-6b5f3f4768a5  requirements.txt  install_lib  Finished  2022-07-13T11:50:09Z               None
            >>>

            # Verify libraries are installed along with its dependant libraries.
                        library version
            0            joblib   1.1.0
            1             numpy  1.21.6
            2            pandas   1.3.5
            3               pip  20.1.1
            4   python-dateutil   2.8.2
            5              pytz  2022.1
            6      scikit-learn   1.0.2
            7             scipy   1.7.3
            8        setuptools  47.1.0
            9               six  1.16.0
            10    threadpoolctl   3.1.0

            # Uninstall libraries specified in the file.
            >>> testenv.uninstall_lib(libs_file_path="requirements.txt", asynchronous=True)
            Request to uninstall libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '95ebfc7b-2910-4aab-be80-3e47f84737bd'.

            # Check the status.
            >>> testenv.status('95ebfc7b-2910-4aab-be80-3e47f84737bd')
                                           Claim Id         File/Libs    Method Name     Stage             Timestamp Additional Details
            0  95ebfc7b-2910-4aab-be80-3e47f84737bd  requirements.txt  uninstall_lib   Started  2022-07-13T11:52:03Z               None
            1  95ebfc7b-2910-4aab-be80-3e47f84737bd  requirements.txt  uninstall_lib  Finished  2022-07-13T11:52:39Z               None
            >>>

            # Verify if the specified libraries are uninstalled.
             >>> testenv.libs
                       library version
            0           joblib   1.1.0
            1            numpy  1.21.6
            2              pip  20.1.1
            3  python-dateutil   2.8.2
            4             pytz  2022.1
            5            scipy   1.7.3
            6       setuptools  47.1.0
            7              six  1.16.0
            8    threadpoolctl   3.1.0

            # Example 4: Install and uninstall libraries specified in requirement text file synchronously
            #            by specifying the timeout.

            # Install libraries by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            matplotlib
            -----------------------------------------------------------

            # Install libraries specified in the file.
            >>> testenv.install_lib(libs_file_path="requirements.txt")
                                           Claim Id         File/Libs  Method Name     Stage             Timestamp Additional Details
            0  d441bc45-6594-4244-ba26-de2ca3272d3f  requirements.txt  install_lib   Started  2022-08-12T06:03:54Z
            1  d441bc45-6594-4244-ba26-de2ca3272d3f  requirements.txt  install_lib  Finished  2022-08-12T06:04:44Z
            >>>

            # Verify libraries are installed along with its dependant libraries.
            >>> testenv.libs
                             name version
            0              cycler  0.11.0
            1           fonttools  4.34.4
            2          kiwisolver   1.4.4
            3          matplotlib   3.5.3
            4               numpy  1.21.6
            5           packaging    21.3
            6              Pillow   9.2.0
            7                 pip  20.1.1
            8           pyparsing   3.0.9
            9     python-dateutil   2.8.2
            10         setuptools  47.1.0
            11                six  1.16.0
            12  typing-extensions   4.3.0
            >>>

            # Uninstall libraries specified in the file.
            >>> testenv.uninstall_lib(libs_file_path="requirements.txt", timeout=1)
            Request to uninstall libraries initiated successfully in the remote user environment 'testenv' but unable to get the status. Check the status using status() with the claim id '3e811857-969d-418c-893d-29ec38f54020'.
            '3e811857-969d-418c-893d-29ec38f54020'
            >>>

            # Check the status.
            >>> testenv.status('3e811857-969d-418c-893d-29ec38f54020')
                                           Claim Id         File/Libs    Method Name     Stage             Timestamp Additional Details
            0  3e811857-969d-418c-893d-29ec38f54020  requirements.txt  uninstall_lib   Started  2022-08-12T06:05:51Z
            1  3e811857-969d-418c-893d-29ec38f54020  requirements.txt  uninstall_lib  Finished  2022-08-12T06:05:57Z
            >>>

            # Verify if the specified libraries are uninstalled.
            >>> testenv.libs
                             name version
            0              cycler  0.11.0
            1           fonttools  4.34.4
            2          kiwisolver   1.4.4
            3               numpy  1.21.6
            4           packaging    21.3
            5              Pillow   9.2.0
            6                 pip  20.1.1
            7           pyparsing   3.0.9
            8     python-dateutil   2.8.2
            9          setuptools  47.1.0
            10                six  1.16.0
            11  typing-extensions   4.3.0
            >>>
        """
        user_name = kwargs.get("user")

        asynchronous = kwargs.get("asynchronous", False)
        timeout = kwargs.get("timeout")
        claim_id = self.__manage_libraries(libs, libs_file_path,user_name, "UNINSTALL", asynchronous, timeout)
        return (claim_id)

    def update_lib(self, libs=None, libs_file_path=None, **kwargs):
        """
        DESCRIPTION:
            Function updates Python libraries if already installed,
            otherwise installs the libraries in remote user environment.

        PARAMETERS:
            libs:
                Optional Argument.
                Specifies the add-on library name(s).
                Types: str OR list of Strings(str)

            libs_file_path:
                Optional Argument.
                Specifies the absolute/relative path of the text file (including file name)
                which supplies a list of libraries to be updated from the remote user
                environment. Path specified should include the filename with extension.
                The file should contain library names and version number(optional) of libraries.
                Note:
                    This file format should adhere to the specification of the requirements file
                    used to update Python libraries with pip command.
                Sample text file contents:
                    numpy
                    joblib==0.13.2
                Note:
                    1. The file must have an ".txt" extension.
                    2. Either libs or libs_file_path argument must be specified.
                Types: str

        **kwargs:
            asynchronous:
                Optional Argument.
                Specifies whether to update the library in remote user environment
                synchronously or asynchronously. When set to True, libraries are updated
                asynchronously. Otherwise, libraries are updated synchronously.
                Note:
                    One should not use remove_env() on the same environment till the
                    asynchronous call is complete.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for updating the libraries. If the library is
                not updated with in "timeout" seconds, the function returns a claim-id and one
                can check the status using the claim-id. If "timeout" is not specified, then there
                is no limit on the wait time.
                Note:
                     Argument is ignored when "asynchronous" is True.
                Types: int OR float

        RETURNS:
            claim_id, to track status.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create remote user environment.
            >>> testenv = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.

            # Example 1: Update a single Python library asynchronously.
            # Install a Python library.
            >>> testenv.install_lib(["joblib==0.13.2"], asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'f44443a9-42c3-4fd3-b4a2-735d1bfb7c27'.

            # Check the status.
            >>> testenv.status('f44443a9-42c3-4fd3-b4a2-735d1bfb7c27')
                                           Claim Id       File/Libs  Method Name     Stage             Timestamp Additional Details
            0  f44443a9-42c3-4fd3-b4a2-735d1bfb7c27  joblib==0.13.2  install_lib  Finished  2022-07-13T11:54:31Z               None
            >>>

            # Verify joblib library is installed with specified version.
            >>> testenv.libs
                  library version
            0      joblib  0.13.2
            1         pip  20.1.1
            2  setuptools  47.1.0

            # Update joblib libary to the new version specified.
            >>> testenv.update_lib("joblib==0.14.1", asynchronous=True)
            Request to update libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '8bfe55fc-efaa-44c7-9137-af24b6bb9ef8'.

            # Check the status.
            >>> testenv.status('8bfe55fc-efaa-44c7-9137-af24b6bb9ef8')
                                           Claim Id       File/Libs Method Name     Stage             Timestamp Additional Details
            0  8bfe55fc-efaa-44c7-9137-af24b6bb9ef8  joblib==0.14.1  update_lib  Finished  2022-07-13T11:55:29Z               None
            >>>

            # Verify joblib library version is updated with specified version.
            >>> testenv.libs
                  library version
            0      joblib  0.14.1
            1         pip  20.1.1
            2  setuptools  47.1.0

            # Example 2: Update multiple Python libraries synchronously.
            >>> testenv.update_lib(["joblib==0.14.1","numpy==1.19.5"])
                                           Claim Id                      File/Libs Method Name     Stage             Timestamp Additional Details
            0  28e0e03e-469b-440c-a939-a0e8a901078f  joblib==0.14.1, numpy==1.19.5  update_lib   Started  2022-07-13T11:56:32Z               None
            1  28e0e03e-469b-440c-a939-a0e8a901078f  joblib==0.14.1, numpy==1.19.5  update_lib  Finished  2022-07-13T11:56:34Z               None
            >>>

            # Verify if numpy is installed with the specific version.
            >>> testenv.libs
                  library version
            0      joblib  0.14.1
            1       numpy  1.19.5
            2         pip  20.1.1
            3  setuptools  47.1.0

            # Example 3: update libraries specified in the requirements text file asynchrnously.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            numpy==1.21.6
            -----------------------------------------------------------
            >>> testenv.update_lib(libs_file_path="requirement.txt", asynchronous=True)
            Request to update libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'd3301da5-f5cb-4248-95dc-a59e77fe9db5'.

            # Verify if numpy is updated to the specific version.
            >>> testenv.libs
                  library version
            0      joblib  0.14.1
            1       numpy  1.21.6
            2         pip  20.1.1
            3  setuptools  47.1.0

            # Example 4: Downgrade the Python library joblib to 0.13.2 synchronously by specifying timeout.
            # As higher version of the package is not automatically uninstalled, we need to uninstall the higher version
            # to use the lower version.
            >>> testenv.uninstall_lib("joblib", asynchronous=True)
            Request to uninstall libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'e32d69d9-452b-4600-be4b-1d5c60647a54'.

            >>> testenv.status('e32d69d9-452b-4600-be4b-1d5c60647a54')
                                           Claim Id File/Libs    Method Name     Stage             Timestamp Additional Details
            0  e32d69d9-452b-4600-be4b-1d5c60647a54    joblib  uninstall_lib   Started  2022-07-13T11:59:14Z               None
            1  e32d69d9-452b-4600-be4b-1d5c60647a54    joblib  uninstall_lib  Finished  2022-07-13T11:59:17Z               None
            >>>

            # Verify if joblib package is uninstalled or not.
            >>> testenv.libs
                  library version
            0         pip  20.1.1
            1  setuptools  47.1.0

            >>> testenv.update_lib(["joblib==0.13.2"], timeout=1)
            Request to update libraries initiated successfully in the remote user environment 'testenv' but unable to get the status. Check the status using status() with the claim id 'ca669e5b-bd2c-4037-ae65-e0147954b85d'.
            'ca669e5b-bd2c-4037-ae65-e0147954b85d'

            # Check the status.
            >>> testenv.status('ca669e5b-bd2c-4037-ae65-e0147954b85d')
                                           Claim Id       File/Libs Method Name     Stage             Timestamp Additional Details
            0  ca669e5b-bd2c-4037-ae65-e0147954b85d  joblib==0.13.2  update_lib   Started  2022-07-13T11:57:41Z               None
            1  ca669e5b-bd2c-4037-ae65-e0147954b85d  joblib==0.13.2  update_lib  Finished  2022-07-13T11:57:47Z               None
            >>>

            # Listing the available libraries.
            >>> testenv.libs
                  library version
            0      joblib  0.13.2
            1         pip  20.1.1
            2  setuptools  47.1.0
        """
        user_name = kwargs.get("user")

        asynchronous = kwargs.get("asynchronous", False)
        timeout = kwargs.get("timeout")
        claim_id = self.__manage_libraries(libs, libs_file_path,user_name, "UPDATE", asynchronous, timeout)
        return (claim_id)

    def refresh(self):
        """
        DESCRIPTION:
            Function refreshes the UserEnv properties 'files' and 'libs'.
            'files' and 'libs' properties cache user environment file and library
            information respectively when invoked. This information is refreshed
            when user invokes any of the following methods of 'UserEnv' class:
                * install_lib
                * uninstall_lib
                * update_lib
                * install_file
                * remove_file
                * refresh

            This method should be used when user environment is updated outside
            of teradataml or cache is not updated after user environment updates.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            NOne

        EXAMPLES:
            # Create a remote user environment.
            >>> env = create_env('test_env', 'python_3.7.9', 'Test environment')
            User environment 'test_env' created.

            # Example 1: Install the libs in the 'test_env' environment.
            # View existing libraries installed.
            >>> env.libs
                     name version
            0         pip  20.1.1
            1  setuptools  47.1.0

            # Install additional Python library using UserEnv method.
            >>> env.install_lib("joblib")
            Request to install libraries initiated successfully in the remote user environment test_env.
            Check the status using status() with the claim id '31157cc6-41eb-4b5d-b618-469840f711e4'.
            '31157cc6-41eb-4b5d-b618-469840f711e4'

            # View installed libraries.
            >>> env.libs
                     name version
            0      joblib   1.1.0
            1         pip  20.1.1
            2  setuptools  47.1.0

            # Install additional Python libraries from outside, i.e. without using the UserEnv methods.
            >>> with open('requirements.txt', 'w') as fp:
            ...     fp.write("numpy")

            >>> import requests
            >>> files = {
            ...     'env-file': open('requirements.txt', 'rb'),
            ...     'env-name': (None, 'test_env'),
            ...     'env-user': (None, 'alice'),
            ...     'action': (None, 'install'),
            ... }
            >>> response = requests.post('{url}/users/ALICE/environments/{env_name}/libraries'. \
            ...                          format(url=configure.ues_url, env_name="dt_testenv"), files=files)

            # View installed libraries. Note that 'numpy' library is not visible as "libs" cache is not updated.
            # To refresh cache execute the 'refresh()' method.
            >>> env.libs
                     name version
            0      joblib   1.1.0
            1         pip  20.1.1
            2  setuptools  47.1.0

            # Refresh the 'libs' and 'files' in the environment.
            >>> env.refresh()

            # View refreshed libraries.
            >>> env.libs
                     name version
            0      joblib   1.1.0
            1       numpy  1.21.6
            2         pip  20.1.1
            3  setuptools  47.1.0

            # Example 2: Install the files in the 'test_env' environment.
            # View existing files.
            >>> env.files
            No files found in remote user environment test_env.

            # Install the file mapper.py in the 'testenv' environment using UserEnv method.
            >>> import os, teradataml
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.py")
            >>> env.install_file(file_path = file_path)
            File 'mapper.py' installed successfully in the remote user environment 'dt_testenv'.
            True

            # View installed files.
            >>> env.files
                    name size     last_updated_dttm
            0  mapper.py  547  2022-07-25T13:18:19Z

            # Install mapper_replace.py from outside, i.e. without using the UserEnv methods.
            >>> import os, requests, teradataml
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper_replace.py")
            >>> headers = {
            ...     'X-User-ID': 'ALICE',
            ... }
            >>> user="alice"
            >>> files = {
            ...     'env-file': open(file_path, 'rb'),
            ...     'env-name': (None, 'test_env'),
            ...     'env-user': (None, 'alice'),
            ... }
            >>> response = requests.post('{url}/users/{user}/environments/pyenv/files'. \
            ...                          format(url=configure.ues_url, user=user), headers=headers, files=files)

            # View installed files. Note that recently installed file using REST call
            # is not visible as "files" cache is not updated. To refresh cache execute the 'refresh()' method.
            >>> env.files
                    name size     last_updated_dttm
            0  mapper.py  547  2022-07-20T16:24:06Z

            # Refresh the 'libs' and 'files' in the environment.
            >>> env.refresh()

            # View refreshed files.
            >>> env.files
                            name size     last_updated_dttm
            0          mapper.py  547  2022-07-25T13:18:19Z
            1  mapper_replace.py  552  2022-07-25T13:22:23Z

        """
        # Set self.__libs_changed and self.__files_changed flags to True.
        self.__libs_changed = True
        self.__files_changed = True

    def status(self, claim_ids=None,user=None):
        """
        DESCRIPTION:
            Function to check the status of the operations performed by the library/file
            management methods of UserEnv. Status of the following operations can be checked:
              * File installation, when installed asynchronously. Applicable for the files
                with size greater than 10 MB.
              * Install/Uninstall/Update of the libraries in user environment.

        PARAMETERS:
            claim_ids:
                Optional Argument.
                Specifies the unique identifier(s) of the asynchronous process
                started by the UserEnv management methods.
                If user do not pass claim_ids, then function gets the status
                of all the asynchronus process'es in the current session.
                Types: str OR list of Strings (str)

        RETURNS:
            Pandas DataFrame.

        RAISES:
            None

        EXAMPLES:
            # Create a remote user environment.
            >>> env = create_env('test_env', 'python_3.7.9', 'Test environment')
            User environment test_env created.

            # Example 1: Install the file 'large_file' asynchronously with 'large_file' found in
                         temp folder and check the latest status of installation.
            # Note:
            #     Running this example creates a file 'large_file' with size
            #     approximately 41MB in the temp folder.
            >>> import tempfile, os
            >>> def create_large_file():
            ...     file_name = os.path.join(tempfile.gettempdir(),"large_file")
            ...     with open(file_name, 'xb') as fp:
            ...         fp.seek((1024 * 1024 * 41) - 1)
            ...         fp.write(b'\0')
            ...
            >>> claim_id = env.install_file('large_file')
                File installation is initiated. Check the status using status() with the claim id 53e44892-1952-45eb-b828-6635c0447b59.
            >>> env.status(claim_id)
                                           Claim Id                                                       File/Libs   Method Name               Stage             Timestamp Additional Details
            0  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz  install_file  Endpoint Generated  2022-07-27T18:20:34Z               None
            1  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz  install_file       File Uploaded  2022-07-27T18:20:35Z               None
            2  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz  install_file      File Installed  2022-07-27T18:20:38Z               None
            >>>

            # Example 2: Install the library 'teradataml' asynchronously and check the status of installation.
            >>> claim_id = env.install_lib('teradataml')
                Request to install libraries initiated successfully in the remote user environment test_env. Check the status using status() with the claim id '349615e2-9257-4a70-8304-ac76f50712f8'.
            >>> env.status(claim_id)
                                           Claim Id   File/Libs  Method Name     Stage             Timestamp Additional Details
            0  349615e2-9257-4a70-8304-ac76f50712f8  teradataml  install_lib   Started  2022-07-13T10:37:40Z               None
            1  349615e2-9257-4a70-8304-ac76f50712f8  teradataml  install_lib  Finished  2022-07-13T10:39:29Z               None
            >>>

            # Example 3: update the library 'teradataml' to 17.10.0.0 asynchronously and check the status of installation.
            >>> claim_id = env.update_lib('teradataml==17.10.0.0')
            Request to update libraries initiated successfully in the remote user environment test_env. Check the status using status() with the claim id '29d06296-7444-4851-adef-ca1f921b1dd6'.
            >>> env.status(claim_id)
                                           Claim Id              File/Libs Method Name     Stage             Timestamp Additional Details
            0  29d06296-7444-4851-adef-ca1f921b1dd6  teradataml==17.10.0.0  update_lib   Started  2022-07-13T10:47:39Z               None
            1  29d06296-7444-4851-adef-ca1f921b1dd6  teradataml==17.10.0.0  update_lib  Finished  2022-07-13T10:49:52Z               None
            >>>

            # Example 4: uninstall the library 'teradataml' and check the complete status of all the asynchronous process'es.
            >>> claim_id = env.uninstall_lib('teradataml')
            Request to uninstall libraries initiated successfully in the remote user environment test_env. Check the status using status() with the claim id '5cd3b3f7-f3b8-4bfd-8abe-7c811a6728db'.
            >>> env.status()
                                           Claim Id                                                       File/Libs    Method Name               Stage             Timestamp Additional Details
            0  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz   install_file  Endpoint Generated  2022-07-27T18:20:34Z               None
            1  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz   install_file       File Uploaded  2022-07-27T18:20:35Z               None
            2  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz   install_file      File Installed  2022-07-27T18:20:38Z               None
            3  29d06296-7444-4851-adef-ca1f921b1dd6                                           teradataml==17.10.0.0     update_lib             Started  2022-07-13T10:47:39Z               None
            4  29d06296-7444-4851-adef-ca1f921b1dd6                                           teradataml==17.10.0.0     update_lib            Finished  2022-07-13T10:49:52Z               None
            5  349615e2-9257-4a70-8304-ac76f50712f8                                           teradataml               install_lib             Started  2022-07-13T10:37:40Z               None
            6  349615e2-9257-4a70-8304-ac76f50712f8                                           teradataml               install_lib            Finished  2022-07-13T10:39:29Z               None
            7  5cd3b3f7-f3b8-4bfd-8abe-7c811a6728db                                           teradataml             uninstall_lib             Started  2022-07-13T10:37:40Z               None
            8  5cd3b3f7-f3b8-4bfd-8abe-7c811a6728db                                           teradataml             uninstall_lib            Finished  2022-07-13T10:39:29Z               None

        """
        __arg_info_matrix = []
        __arg_info_matrix.append(["claim_ids", claim_ids, True, (list, str), True])

        # Validate arguments
        _Validators._validate_function_arguments(__arg_info_matrix)

        

        # If user do not pass any claim_ids, get the status for all the claim-ids
        # created in the current session.
        if claim_ids is None:

            # If there are no claim_ids in the current session, print a message and return.
            if not self.__claim_ids:
                return("No file/library management operations found.")
                

            # Get all the claim_ids.
            claim_ids = self.__claim_ids.keys()
        else:
            # If user pass a single claim_id as string, convert to list.
            claim_ids = UtilFuncs._as_list(claim_ids)

        return pd.DataFrame.from_records(self.__process_claim_ids(claim_ids=claim_ids,user=user), columns=self.__status_columns)

    def __process_claim_ids(self, claim_ids,user=None):
        """
        DESCRIPTION:
            Function processes the claim IDs of asynchronous process using
            their 'claim_ids' parallelly to get the status.

        PARAMETERS:
            claim_ids:
                Required Argument.
                Specifies the unique identifier(s) of the asynchronous process
                started by the UserEnv management methods.
                Types: str OR list of Strings (str)

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            # Create a remote user environment.
            >>> env.__process_claim_ids(['123-456-789', 'abc-xyz'])
        """
        # Create thread pool executor to get the status parallelly.
        executor = ThreadPoolExecutor(max_workers=10)

        # executor.submit returns a future object. Store all the futures in a list.
        futures = [executor.submit(self.__get_claim_id_status, claim_id,user) for claim_id in claim_ids]

        # Wait forever, till all the futures complete.
        wait(futures)

        # Add all the results to a list.
        return functools.reduce(lambda x, y: x + y, (future.result() for future in futures))

    def __get_claim_id_status(self, claim_id,user=None):
        """
        DESCRIPTION:
            Function to get the status of asynchronus process using the claim_id.

        PARAMETERS:
            claim_id:
                Required Argument.
                Specifies the unique identifier of the asynchronous process
                started by the UserEnv management methods.
                Types: str

        RETURNS:
            Pandas DataFrame.

        RAISES:
            None

        EXAMPLES:
            # Create a remote user environment.
            >>> env.__get_claim_id_status('123-456')
        """
        # Get the claim_id details.
        claim_id_details = {"Claim Id": claim_id,
                            "Method Name": self.__claim_ids.get(claim_id, {}).get("action", "Unknown"),
                            "File/Libs": self.__claim_ids.get(claim_id, {}).get("value", "Unknown")}

        try:
            response = UtilFuncs._http_request(_get_ues_url(env_type="fm",user_name=user, claim_id=claim_id, api_name="status"),
                                               headers=_get_auth_token())
            data = _process_ues_response(api_name="status", response=response).json()
            # if claim_id is for install_file - 'data' looks as below:
            #      [
            #         {'timestamp': '2022-06-29T17:03:49Z', 'stage': 'Endpoint Generated'},
            #         {'timestamp': '2022-06-29T17:03:50Z', 'stage': 'File Uploaded'},
            #         {'timestamp': '2022-06-29T17:03:52Z', 'stage': 'File Installed'}
            #      ]

            # if claim_id is for install_lib/uninstall_lib/update_lib - 'data' looks as below:
            #     [
            #         {
            #             "timestamp": "2022-07-07T09:43:04Z",
            #             "stage": "Started"
            #         },
            #         {
            #             "timestamp": "2022-07-07T09:43:06Z",
            #             "stage": "Finished",
            #             "details": "WARNING: Skipping numpysts as it is not installed."
            #                        "WARNING: Skipping pytest as it is not installed."
            #         }
            #      ]

            # Create a lamda function to extract the data.
            get_details = lambda data: {"Additional Details": data.pop("details", None),
                                        "Stage": data.pop("stage", None),
                                        "Timestamp": data.pop("timestamp", None),
                                        **claim_id_details}

            return [get_details(sub_step) for sub_step in data]

        except Exception as e:
            # For any errors, construct a row with error reason in 'additional_details' column.
            record = {"Additional Details": str(e), "Timestamp": None, "Stage": "Errored"}
            record.update(claim_id_details)
            return [record]

    def __get_claim_status(self, claim_id, timeout, action):
        """
        DESCRIPTION:
            Function to get the status of asynchronus process using the claim_id.
            The function polls the status of asynchronous process using the 'status' API
            for 'timeout' seconds and get's the status of it. When asynchronus process
            is not completed in 'timeout' seconds, the function stops polling the status
            API and returns the claim-id.

        PARAMETERS:
            claim_id:
                Required Argument.
                Specifies the unique identifier of the asynchronous process
                started by the UserEnv management methods.
                Types: str

            timeout:
                Required Argument.
                Specifies the maximum time in seconds to poll the status.
                Types: int OR float

            action:
                Required Argument.
                Specifies the action for asynchronous process.
                Types: str

            suppress_output:
                Required Argument.
                Specifies whether to print the output message or not.
                When set to True, then the output message is not printed.
                Default Value: False
                Types: bool

        RETURNS:
            Pandas DataFrame OR claim id.

        RAISES:
            None

        EXAMPLES:
            # Create a remote user environment.
            >>> env.__get_claim_status('123-456', 5, 'install_file')
        """
        # If user specifies 'timeout', poll only for 'timeout' seconds. Otherwise,
        # poll status API indefinitely.
        timeout = UtilFuncs._get_positive_infinity() if timeout is None else timeout

        start_time = time.time()
        while time.time() - start_time <= timeout:
            time.sleep(3)
            records = self.__is_async_operation_completed(claim_id)
            if records:
                return pd.DataFrame.from_records(records, columns=self.__status_columns)

        # Unable to get the response with in 'timeout' seconds. Print a message and
        # return claim id.
        print("Request to {} initiated successfully in the remote user environment '{}' "
              "but Timed out status check. Check the status using status() with the "
              "claim id '{}'.".format(action, self.env_name, claim_id))
        return claim_id

    def __is_async_operation_completed(self, claim_id):
        """
        DESCRIPTION:
            Function to check whether asynchronous process to install/update/uninstall libraries/file
            has completed or not.

        PARAMETERS:
            claim_id:
                Required Argument.
                Specifies the unique identifier of the asynchronous process
                started by the UserEnv management methods.
                Types: str

        RETURNS:
            list OR bool.

        RAISES:
            None

        EXAMPLES:
            # Create a remote user environment.
            >>> env.__is_async_operation_completed('123-456')
        """
        records = self.__get_claim_id_status(claim_id)

        # For library installation/uninstallation/updation, if the background process in
        # UES completes, it always returns two records. However, for file, this may not
        # be the case. So, validating both separately.
        if self.__claim_ids.get(claim_id, {}).get("action") == "install_file":
            for record in records:
                if "File Installed" in record["Stage"]:
                    return records
            return False

        return records if len(records) == 2 else False

    def __repr__(self):
        """
        Returns the string representation for class instance.
        """
        repr_string = "Environment Name: {}\n".format(self.env_name)
        repr_string = repr_string + "Base Environment: {}\n".format(self.base_env)
        repr_string = repr_string + "Description: {}\n".format(self.desc)

        if self.__files is not None:
            repr_string_files = "############ Files installed in User Environment ############"
            repr_string = "{}\n\n{}\n\n{}".format(repr_string, repr_string_files, self.__files)

        if self.__libs is not None:
            repr_string_libs = "############ Libraries installed in User Environment ############"
            repr_string = "{}\n\n{}\n\n{}".format(repr_string, repr_string_libs, self.__libs)

        return repr_string
