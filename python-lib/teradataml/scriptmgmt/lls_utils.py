# ####################################################################
#
# Copyright (c) 2023 by Teradata Corporation. All rights reserved.
# TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET
#
# ####################################################################
import concurrent.futures
import functools
import operator
import pandas as pd
import requests
from teradataml.scriptmgmt.UserEnv import UserEnv, _get_auth_token, _process_ues_response, _get_ues_url



from teradataml.options import configure
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.clients.pkce_client import _AuthWorkflow
from teradataml.scriptmgmt.UserEnv import UserEnv, _get_auth_token, _process_ues_response, _get_ues_url
from teradataml.utils.validators import _Validators
from time import time, sleep
import warnings
import webbrowser
from urllib.parse import urlparse

from enum import Enum

class HTTPRequest(Enum):
    # Holds variable names for HTTP calls.
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"

class UtilFuncs():
    @staticmethod
    def _http_request(url, method_type=HTTPRequest.GET, **kwargs):
        """
        Description:
            Function to initiate HTTP(S) request.

        PARAMETERS:
            url:
                Required Argument.
                Specifies the url to initiate http request.
                Types: str

            method_type:
                Optional Argument.
                Specifies the type of HTTP request.
                Default value: HTTPREquest.GET
                Types: HTTPRequest enum

            **kwargs:
                Specifies the keyword arguments required for HTTP Request.
                Below are the expected arguments as a part of kwargs:
                    json:
                        Optional Argument.
                        Specifies the payload for HTTP request in a dictionary.
                        Types: dict

                    data:
                        Optional Argument.
                        Specifies the payload for HTTP request in a string format.
                        Types: str

                    headers:
                        Optional Argument.
                        Specifies the headers for HTTP request.
                        Types: dict

                    verify:
                        Optional Argument.
                        Specifies whether to verify the certificate or not in a HTTPS request.
                        One can specify either False to suppress the certificate verification or
                        path to certificate to verify the certificate.
                        Types: str OR bool

                    files:
                        Optional Argument.
                        Specifies the file to be uploaded with a HTTP Request.
                        Types: tuple

        RETURNS:
            Response object.

        RAISES:
            None

        EXAMPLES:
            resp = UtilFuncs._http_request("http://abc/xyz.teradata")
        """
        kwargs["verify"] = configure.certificate_file

        if not configure.certificate_file:
            warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made to host[ a-zA-Z0-9'-.]*")

        return getattr(requests, method_type.value)(url=url, **kwargs)
    
def list_base_envs():
    """
    DESCRIPTION:
        Lists the available base Python environments versions configured in the
        Open Analytics Framework.

    PARAMETERS:
            None.

    RETURNS:
        Pandas DataFrame.
        If the operation is successful, function returns
        environment name, language and version of the language interpreter in a Pandas dataframe.

    RAISES:
        TeradataMlException.

    EXAMPLES:
            >>> from teradataml import list_base_envs
            >>> list_base_envs()
                   base_name language version
            0  python_3.6.11   Python  3.6.11
            1   python_3.7.9   Python   3.7.9
            2   python_3.8.5   Python   3.8.5
            >>>
    """
    try:
        response = UtilFuncs._http_request(_get_ues_url("base_environments"), headers=_get_auth_token())

        response = _process_ues_response(api_name="list_base_envs", response=response)
        data = response.json()

        # If no data, raise warning.
        if len(data) == 0:
            warnings.warn(Messages.get_message(MessageCodes.NO_ENVIRONMENT_FOUND, "Python base"))
            return

        # Create a pandas DataFrame from data.
        pandas_df = pd.DataFrame.from_records(data)

        # Filter out python base environments. If no python environments, raise a warning.
        #pandas_df = pandas_df[pandas_df.language == "Python"]
        if pandas_df.shape[0] == 0:
            warnings.warn(Messages.get_message(MessageCodes.NO_ENVIRONMENT_FOUND, "Python or R base"))
        else:
            return pandas_df

    except (TeradataMlException, RuntimeError):
        raise
    except Exception as emsg:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "list_base_envs", str(emsg))
        raise TeradataMlException(error_msg, msg_code)


def list_user_envs(env_name=None, **kwargs):
    """
    DESCRIPTION:
        Lists the Python environments created by the session user in
        Open Analytics Framework.

    PARAMETERS:
        env_name:
            Optional Argument.
            Specifies the string or regular expression to filter name of the environment.
            Types: str

        base_env:
            Optional Argument.
            Specifies the string or regular expression to filter the base Python environment.
            Types: str

        desc:
            Optional Argument.
            Specifies the string or regular expression to filter the description
            about the environment.
            Types: str
        
        case:
            Optional Argument.
            Specifies whether filtering operation should be case sensitive or not.
            Default Value: False
            Types: boolean
        
        regex:
            Optional Argument.
            Specifies whether string passed to "env_name", "base_env", and "desc"
            should be treated as regular expression or a literal.
            When set to True, string is considered as a regular expression pattern,
            otherwise treats it as literal string.
            Default Value: True
            Types: boolean
        
        flags:
            Optional Argument.
            Specifies flags to pass for regular expressions in filtering.
            For example
                re.IGNORECASE.
            Default Value: 0
            Types: int

    RETURNS:
        Pandas DataFrame.
        Function returns remote user environments and their details in a Pandas dataframe.
        Function will help user find environments created, version of Python language used
        in the environment and description of each environment if provided at the time of
        environment creation.

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # Create example environments.
        >>> create_env('Fraud_Detection',
        ...            'python_3.7.9',
        ...            'Fraud detection through time matching')
            User environment 'Fraud_detection' created.
        >>> create_env('Lie_Detection',
        ...            'python_3.7.9',
        ...            'Lie detection through time matching')
            User environment 'Lie_Detection' created.
        >>> create_env('Lie_Detection_ML',
        ...            'python_3.6.11',
        ...            'Detect lie through machine learning.')
            User environment 'Lie_Detection_ML' created.
        >>> create_env('Sales_env',
        ...            'python_3.8.5',
        ...            'Sales team environment.')
            User environment 'Sales_env' created.
        
        # Example 1: List all available user environments.
        >>> list_user_envs()
           env_name         env_description                        base_env_name  language
        0  Fraud_Detection  Fraud detection through time matching  python_3.7.9   Python
        1  Lie_Detection    Lie detection through time matching    python_3.7.9   Python
        2  Lie_Detection_ML Detect lie through machine learning.   python_3.6.11  Python
        3  Sales_env        Sales team environment.                python_3.8.5   Python

        # Example 2: List all user environments with environment name containing string
        #            "Detection" and description that contains string "."(period).
        >>> list_user_envs(env_name="Detection", desc=".", regex=False)
           env_name         env_description                        base_env_name  language
        2  Lie_Detection_ML Detect lie through machine learning.   python_3.6.11  Python

        # Example 3: List all user environments with description that contains string "lie"
        #            and is case sensitive. 
        >>> list_user_envs(desc="lie", case=True)
           env_name         env_description                        base_env_name  language
        2  Lie_Detection_ML Detect lie through machine learning.   python_3.6.11  Python

        # Example 4: List all user environments with base environment version containing string
        #            "3.8".
        >>> list_user_envs(base_env="3.8")
           env_name         env_description                        base_env_name  language
        3  Sales_env        Sales team environment                 python_3.8.5   Python

        # Example 5: List all user environments with environment name contains string "detection",
        #            description containing string "fraud" and base environment containing string "3.7".
        >>> list_user_envs("detection", desc="fraud", base_env="3.7")
           env_name         env_description                        base_env_name  language
        0  Fraud_Detection  Fraud detection through time matching  python_3.7.9   Python

        # Example 6: List all user environments with environment name that ends with "detection".
        >>> list_user_envs("detection$")
           env_name         env_description                        base_env_name  language
        0  Fraud_Detection  Fraud detection through time matching  python_3.7.9   Python
        1  Lie_Detection    Lie detection through time matching    python_3.7.9   Python

        # Example 7: List all user environments with description that has either "lie" or "sale".
        #            Use re.VERBOSE flag to add inline comment.
        >>> list_user_envs(desc="lie|sale # Search for lie or sale.", flags=re.VERBOSE)
           env_name         env_description                        base_env_name  language
        1  Lie_Detection    Lie detection through time matching    python_3.7.9   Python
        2  Lie_Detection_ML Detect lie through machine learning.   python_3.6.11  Python
        3  Sales_env        Sales team environment.                python_3.8.5   Python

        # Example 8: List all user environments where python 3 environment release version has 
        #            odd number. For e.g. python_3.7.x. 
        >>> list_user_envs(base_env="\.\d*[13579]\.")
           env_name         env_description                        base_env_name  language
        0  Fraud_Detection  Fraud detection through time matching  python_3.7.9   Python
        1  Lie_Detection    Lie detection through time matching    python_3.7.9   Python

        # Remove example environments.
        remove_env("Fraud_Detection")
        remove_env("Lie_Detection")
        remove_env("Lie_Detection_ML")
        remove_env("Sales_env")
               
    """
    base_env = kwargs.pop("base_env", None)
    desc = kwargs.pop("desc", None)
    case = kwargs.pop("case", False)
    user = kwargs.pop("user",None)
    __arg_info_matrix = []
    __arg_info_matrix.append(["env_name", env_name, True, (str), True])
    __arg_info_matrix.append(["base_env", base_env, True, (str), True])
    __arg_info_matrix.append(["desc", desc, True, (str), True])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)

    try:
        response = UtilFuncs._http_request(_get_ues_url(user_name=user), headers=_get_auth_token())
        response = _process_ues_response(api_name="list_user_envs", response=response)
        data = response.json()

        if len(data) > 0:
            unknown_label = "Unknown"
            # Check if environment is corrupted or not. If it is corrupted, alter the details.
            for base_env_details in data:
                if base_env_details["base_env_name"] == "*":
                    base_env_details["base_env_name"] = unknown_label
                    base_env_details["language"] = unknown_label
                    base_env_details["env_description"] = "Environment is corrupted. Use remove_env() to remove environment."

            # Return result as Pandas dataframe.
            pandas_df = pd.DataFrame.from_records(data)
            # Filter only Python environments.
            #pandas_df = pandas_df[(pandas_df.language == "Python") | (pandas_df.language == unknown_label)]

            # Filter based on arguments passed by user.
            exprs = []
            if env_name is not None:
                exprs.append(pandas_df.env_name.str.contains(pat=env_name, case=case, **kwargs))
            if base_env is not None:
                exprs.append(pandas_df.base_env_name.str.contains(pat=base_env, case=case, **kwargs))
            if desc is not None:
                exprs.append(pandas_df.env_description.str.contains(pat=desc, case=case, **kwargs))

            pandas_df = pandas_df[functools.reduce(operator.and_, exprs)] if exprs else pandas_df

            # Return the DataFrame if not empty.
            if len(pandas_df) > 0:
                return pandas_df
        
        warnings.warn(Messages.get_message(MessageCodes.NO_ENVIRONMENT_FOUND, "user"))
    except (TeradataMlException, RuntimeError):
        raise
    except Exception as emsg:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "list_user_envs", emsg)
        raise TeradataMlException(error_msg, msg_code)


def create_env(env_name, base_env, desc=None,user=None):
    """
    DESCRIPTION:
        Creates an isolated remote user environment in the Open Analytics Framework that
        includes a specific Python language interpreter version.
        Available base Python environments can be found using list_base_envs() function.

    PARAMETERS:
        env_name:
            Required Argument.
            Specifies the name of the environment to be created.
            Types: str

        base_env:
            Required Argument.
            Specifies the name of the base Python environment to be used to create remote
            user environment.
            Types: str

        desc:
            Optional Argument.
            Specifies description about the environment's usage or purpose.
            Types: str

    RETURNS:
        An object of class UserEnv representing the remote user environment.

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # List available Python environments in the Vantage.
        >>> list_base_envs()
                   base_name language version
            0  python_3.6.11   Python  3.6.11
            1   python_3.7.9   Python   3.7.9
            2   python_3.8.5   Python   3.8.5

        # create a Python 3.7.3 environment with given name and description in the Vantage.
        >>> fraud_detection_env = create_env('Fraud_detection',
        ...                                  'python_3.7.9',
        ...                                  'Fraud detection through time matching')
            User environment 'Fraud_detection' created.
    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["env_name", env_name, False, (str), True])
    __arg_info_matrix.append(["base_env", base_env, False, (str), True])
    __arg_info_matrix.append(["desc", desc, True, (str)])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)

    try:
        data = {"env_name": env_name,
                "env_description": desc,
                "base_env_name": base_env
                }

        response = UtilFuncs._http_request(
            _get_ues_url(user_name=user), HTTPRequest.POST, headers=_get_auth_token(), json=data)

        # Validate the ues response.
        _process_ues_response(api_name="create_env", response=response)


        # Return an instance of class UserEnv.
        return UserEnv(env_name, base_env, desc)

    except (TeradataMlException, RuntimeError):
        raise

    except Exception as emsg:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "create_env", str(emsg))
        raise TeradataMlException(error_msg, msg_code)


def remove_env(env_name,user=None):
    """
    DESCRIPTION:
        Removes the user's Python environment from the Open Analytics Framework.
        The remote user environments are created using create_env() function.
        Note:
            remove_env() should not be triggered on any of the environment if
            install_lib/uninstall_lib/update_lib is running on the corresponding
            environment.

    PARAMETERS:
        env_name:
            Required Argument.
            Specifies the name of the environment to be removed.
            Types: str

    RETURNS:
        True, if the operation is successful.

    RAISES:
        TeradataMlException, RuntimeError.

    EXAMPLES:
        >>> remove_env('Fraud_detection')
        User environment 'Fraud_detection' removed.
    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["env_name", env_name, False, (str), True])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)

    try:
        response = UtilFuncs._http_request(
            _get_ues_url(env_name=env_name,user_name=user), HTTPRequest.DELETE, headers=_get_auth_token())
        _process_ues_response(api_name="remove_env", response=response)
        return True

    except (TeradataMlException, RuntimeError):
        raise
    except Exception as emsg:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "remove_env", emsg)
        raise TeradataMlException(error_msg, msg_code)


def get_env(env_name,user=None):
    """
    DESCRIPTION:
        Returns an object of class UserEnv which represents an existing remote user environment
        created in the Open Analytics Framework. The user environment can be created using
        create_env() function. This function is useful to get an object of existing user
        environment. The object returned can be used to perform further operations such as
        installing, removing files and libraries.

    PARAMETERS:
        env_name:
            Required Argument.
            Specifies the name of the existing remote user environment.
            Types: str

    RETURNS:
        An object of class UserEnv representing the remote user environment.

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # List available Python environments in the Vantage.
        >>> list_base_envs()
           base_name      language  version
        0  python_3.6.11  Python   3.6.11
        1  python_3.7.9   Python   3.7.9
        2  python_3.8.5   Python   3.8.5

        # Create a Python 3.8.5 environment with given name and description in the Vantage and
        # get an object of class UserEnv.
        #
        >>> test_env = create_env('test_env', 'python_3.8.5', 'Fraud detection through time matching')
        User environment 'test_env' created.

        # In a new terdataml session, user can use get_env() function to get an object pointing to
        # existing user environment created in previous step so that further operations can be
        # performed such as install files/libraries.
        >>> test_env = get_env('test_env')
    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["env_name", env_name, False, (str), True])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)

    try:
        # Get environments created by the current logged in user.
        user_envs_df = list_user_envs(env_name=env_name,user=user)

        if env_name not in user_envs_df.env_name.values:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "get_env()", "User environment '{}' not found."
                                                                    " Use 'create_env()' function to create"
                                                                    " user environment.".format(env_name))
            raise TeradataMlException(error_msg, msg_code)

        # Get row matching the environment name.
        userenv_row = user_envs_df[user_envs_df['env_name'] == env_name]

        if userenv_row.base_env_name.values[0] == "Unknown":
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "get_env()", "User environment '{}' is corrupted."
                                                                    " Use 'remove_env()' function to remove"
                                                                    " user environment.".format(env_name))
            raise TeradataMlException(error_msg, msg_code)
            
        
        # Return an instance of class UserEnv.
        return UserEnv(userenv_row.env_name.values[0],
                       userenv_row.base_env_name.values[0],
                       userenv_row.env_description.values[0])
    except (TeradataMlException, RuntimeError) as tdemsg:
        # TeradataMlException and RuntimeError are raised by list_user_envs.
        # list_user_envs should be replaced with get_env in the error 
        # message for final users.
        tdemsg.args = (tdemsg.args[0].replace("list_user_envs", "get_env"),)
        raise tdemsg
    except Exception as emsg:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "get_env", emsg)
        raise TeradataMlException(error_msg, msg_code)
        



def remove_all_envs(): 
    """
    DESCRIPTION:
        Removes all the user's Python environment from the Open Analytics Framework.
        Note:
            remove_all_envs() should not be triggered if install_lib/uninstall_lib/update_lib
            is running on any environment.

    PARAMETERS:
            None.

    RETURNS:
        True, if the operation is successful.

    RAISES:
        TeradataMlException, RuntimeError.

    EXAMPLES:
          >>> remove_all_envs()
          User environment 'Fraud_detection' removed.
          User environment 'Sales' removed.
          User environment 'Purchase' removed.
    """
    try:
        # Retrieve all user env data.
        user_envs_df = list_user_envs()
        if user_envs_df is not None:
            env_name = user_envs_df["env_name"]
            # Executing remove_env in multiple threads (max_workers set to 10).
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Execute remove_env for each env_name.
                future_remove_env = {executor.submit(remove_env, env): env for env in env_name}
                # Get the result of all executions.
                failed_envs = {}
                for future in concurrent.futures.as_completed(future_remove_env):
                    env = future_remove_env[future]
                    try:
                        future.result()
                    except (TeradataMlException, RuntimeError, Exception) as emsg:
                        # Catching exceptions by remove_env if occured in any thread.
                        failed_envs[env] = emsg
            
            if len(failed_envs) > 0:
                emsg = ""
                for env, tdemsg in failed_envs.items():
                    emsg += "\nUser environment '{0}' failed to remove. Reason: {1}"\
                        .format(env, tdemsg.args[0])
                msg_code = MessageCodes.FUNC_EXECUTION_FAILED
                error_msg = Messages.get_message(msg_code, "remove_all_envs()", emsg)
                raise TeradataMlException(error_msg, msg_code)
                
            return True
        else:
            warnings.warn(Messages.get_message(MessageCodes.NO_ENVIRONMENT_FOUND, "user"))
    except (TeradataMlException, RuntimeError) as tdemsg:
        # TeradataMlException and RuntimeError are raised by list_user_envs.
        # list_user_envs should be replaced with remove_all_envs in the error 
        # message for final users.
        tdemsg.args = (tdemsg.args[0].replace("list_user_envs", "remove_all_envs"),)
        raise tdemsg
    except Exception as emsg:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "remove_all_envs", emsg)
        raise TeradataMlException(error_msg, msg_code)


def set_user_env(env):
    """
    DESCRIPTION:
        Function allows to set the default user environment to be used for the Apply()
        and DataFrame.apply() function execution.

    PARAMETERS:
        env:
            Required Argument.
            Specifies the remote user environment name to set as default for the session.
            Types: str OR Object of UserEnv

    RETURNS:
        True, if the operation is successful.

    RAISES:
        TeradataMlException, RuntimeError.

    EXAMPLES:
        # Create remote user environment.
        >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
        User environment 'testenv' created.

        # Example 1: Set the environment 'testenv' as default environment.
        >>> set_user_env('testenv')
        Default environment is set to 'testenv'.
        >>>

        # Example 2: Create an environment with name 'demo_env' and set it as default environment.
        >>> set_user_env(get_env('test_env'))
        User environment 'testenv' created.
        Default environment is set to 'testenv'.
        >>>
    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["env", env, False, (str, UserEnv), True])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)

    # Get the environment name.
    env = get_env(env_name=env) if isinstance(env, str) else env

    configure._default_user_env = env

    return True


def get_user_env():
    """
    DESCRIPTION:
        Function to get the default user environment set for the session.

    PARAMETERS:
        None.

    RETURNS:
        An object of UserEnv, if the operation is successful.

    RAISES:
        TeradataMlException, RuntimeError.

    EXAMPLES:
        # Create remote user environment.
        >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
        User environment 'testenv' created.
        >>> set_user_env('testenv')
        Default environment is set to 'testenv'.
        >>>

        # Example 1: Get the default environment.
        >>> env = get_user_env()
    """
    if configure._default_user_env is None:
        return

    return configure._default_user_env



def set_auth_token(ues_url, token, pem_file,pem_file_name, org_id=None, **kwargs):
    """
    DESCRIPTION:
        Function to set the Authentication token to connect to User Environment Service
        in VantageCloud Lake.
        Note:
            User must have a privilege to login with a NULL password to use set_auth_token().
            Please refer to GRANT LOGON section in Teradata Documentation for more details.


    PARAMETERS:
        ues_url:
            Required Argument.
            Specifies the URL for User Environment Service in VantageCloud Lake.
            Types: str

        token:
            Required Argument.
            Specifies the PAT token generated from ccp.
            Types: str

        pem_file:
            Required Argument.
            Specifies the path to Private Key file.
            Types: str

        org_id:
            Required Argument.
            Specifies the organization id.
            Default Value: None
            Types: str

        **kwargs:
            username:
            Specifies the user for which authentication is to be requested.
            Types: str

    RETURNS:
        True, if the operation is successful.

    RAISES:
        TeradataMlException, RuntimeError.

    EXAMPLES:

        # Example 1: Set the Authentication token for database username associated with the current context.
        >>> import getpass
        >>> set_auth_token(ues_url=getpass.getpass("ues_url : "),
        token=getpass.getpass("token : "),
        pem_file=getpass.getpass("pem_file : "),

        # Example 1: Set the Authentication token for user "alice".
        >>> import getpass
        >>> set_auth_token(ues_url=getpass.getpass("ues_url : "),
        token=getpass.getpass("token : "),
        pem_file=getpass.getpass("pem_file : "),
        username = "alice")

    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["ues_url", ues_url, False, (str), True])
    __arg_info_matrix.append(["org_id", org_id, True, (str), True])
    __arg_info_matrix.append(["token", token, True, (str), True])
    __arg_info_matrix.append(["pem_file", pem_file, True, (str), True])
    __arg_info_matrix.append(["pem_file_name", pem_file_name, True, (str), True])

    
    username = kwargs.get("username")
    jwt_expiration = kwargs.get("jwt_expiration")

    # If username is specified then the database username associated with the current context will be considered.
    if username is None:
        username = _get_user().lower()

    # Validate arguments.
    _Validators._validate_function_arguments(__arg_info_matrix)

    # Check if pem file exists.
    #_Validators._validate_file_exists(pem_file)

    # Extract the base URL from "ues_url".
    url_parser = urlparse(ues_url)
    base_url = "{}://{}".format(url_parser.scheme, url_parser.netloc)

    if org_id is None:
        netloc = url_parser.netloc
        org_id = netloc.split('.')[0]

    # Construct a dictionary to be passed to _AuthWorkflow().
    state_dict = {}
    state_dict["base_url"] = base_url
    state_dict["org_id"] = org_id
    state_dict["username"] = username
    state_dict["token"] = token
    state_dict["pem_file"] = pem_file
    state_dict["pem_file_name"] = pem_file_name
    state_dict["jwt_expiration"] = jwt_expiration


    

    configure._state_dict = state_dict

    auth_wf = _AuthWorkflow(state_dict)
    token_data = auth_wf._proxy_jwt()

    #print("token: {}".format(token_data))

    #values={'uri':'hello', 'poll_data': token_data}
    values={'token':token_data}
    # Set Open AF parameters.
    configure.ues_url = ues_url
    return values
