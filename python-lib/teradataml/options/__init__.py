from teradataml.options.configure import configure
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes


def set_config_params(**kwargs):
    """
    DESCRIPTION:
        Function to set the configurations in Vantage. Alternatively, user can set the
        configuration parameters independently using 'teradataml.configure' module.

    PARAMETERS:
        kwargs:
            Optional Argument.
            Specifies keyword arguments. Accepts following keyword arguments:

             auth_token:
                Optional Parameter.
                Specifies the authentication token to connect to VantageCloud Lake.
                Note:
                    Authentication token will expire after a specific time.
                    One can get the new authentication token and set it again.
                Types: str

            ues_url:
                Optional Parameter.
                Specifies the URL for User Environment Service in VantageCloud Lake.
                Types: str

            certificate_file:
                Optional Parameter.
                Specifies the path of the certificate file, which is used in
                encrypted REST service calls.
                Types: str

            default_varchar_size:
                Optional Parameter.
                Specifies the size of varchar datatype in Vantage, the default
                size is 1024.
                Types: int

            vantage_version:
                Specifies the Vantage version teradataml is connected to.
                Types: str

            val_install_location:
                Specifies the database name where Vantage Analytic Library functions
                are installed.
                Types: str

            byom_install_location:
                Specifies the database name where Bring Your Own Model functions
                are installed.
                Types: str

            sandbox_container_id:
                Specifies the id of sandbox container that will be used by Script.test_script() method.
                Types: string

            database_version:
                Specifies the database version of the system teradataml is connected to.
                Types: str

            read_nos_function_mapping:
                Specifies the mapping function name for the read_nos table operator function.
                Types: str

            write_nos_function_mapping:
                Specifies the mapping function name for the write_nos table operator function.
                Types: str

    RETURNS:
        bool

    RAISES:
        None

    EXAMPLES:
        # Example 1: Set configuration params using set_config_params() function.
        >>> from teradataml import set_config_params
        >>> set_config_params(auth_token="abc-pqr-123",
        ...                   ues_url="https://teracloud/v1/accounts/xyz-234-76085/open-analytics",
        ...                   certificate_file="cert.crt",
        ...                   default_varchar_size=512,
        ...                   val_install_location="VAL_USER",
        ...                   sandbox_container_id="bgf1233csdh123",
        ...                   read_nos_function_mapping="read_nos_fm",
        ...                   write_nos_function_mapping="write_nos_fm")
        True

        # Example 2: Alternatively, set configuration parameters without using set_config_params() function.
        #            To do so, we will use configure module.
        >>> from teradataml import configure
        >>> configure.auth_token="abc-pqr-123"
        >>> configure.ues_url="https://teracloud/v1/accounts/xyz-234-76085/open-analytics"
        >>> configure.certificate_file="cert.crt"
        >>> configure.default_varchar_size=512
        >>> configure.val_install_location="VAL_USER"
        >>> configure.sandbox_container_id="bgf1233csdh123"
        >>> configure.read_nos_function_mapping="read_nos_fm"
        >>> configure.write_nos_function_mapping="write_nos_fm"
    """
    for option in kwargs:
        try:
            setattr(configure, option, kwargs[option])
        except AttributeError as e:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.FUNC_EXECUTION_FAILED, 'set_config_params', 'Invalid parameter \'{}\'.'.format(option)),
                                      MessageCodes.FUNC_EXECUTION_FAILED)
    return True
