"""
Unpublished work.
Copyright (c) 2021 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

"""
import os
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes


class _ConfigureSuper(object):

    def __init__(self):
        pass

    def _SetKeyValue(self, name, value):
        super().__setattr__(name, value)

    def _GetValue(self, name):
        return super().__getattribute__(name)


def _create_property(name):
    storage_name = '_' + name

    @property
    def prop(self):
        return self._GetValue(storage_name)

    @prop.setter
    def prop(self, value):
        self._SetKeyValue(storage_name, value)

    return prop


class _Configure(_ConfigureSuper):
    """
    Options to configure database related values.
    """

    default_varchar_size = _create_property('default_varchar_size')
    column_casesensitive_handler = _create_property('column_casesensitive_handler')
    vantage_version = _create_property('vantage_version')
    val_install_location = _create_property('VAL_install_location')
    byom_install_location = _create_property('BYOM_install_location')
    sandbox_container_id = _create_property('sandbox_container_id')
    temp_table_database = _create_property('temp_table_database')
    temp_view_database = _create_property('temp_view_database')
    read_nos_function_mapping = _create_property('read_nos_function_mapping')
    write_nos_function_mapping = _create_property('write_nos_function_mapping')


    def __init__(self, default_varchar_size=1024, column_casesensitive_handler = False,
                 vantage_version="vantage1.1", val_install_location=None,
                 byom_install_location=None, sandbox_container_id=None,
                 temp_table_database=None, temp_view_database=None, database_version=None,
                 read_nos_function_mapping="read_nos", write_nos_function_mapping="write_nos"):
        """
        PARAMETERS:
            default_varchar_size:
                Specifies the size of varchar datatype in Teradata Vantage, the default
                size is 1024.
                User can configure this parameter using options.
                Types: int
                Example:
                    teradataml.options.configure.default_varchar_size = 512

            column_casesensitive_handler:
                Specifies a boolean value that sets the value of this option to True or
                False.
                One should set this to True, when ML Engine connector property is
                CASE-SENSITIVE, else set to False, which is CASE-INSENSITIVE.
                Types: bool
                Example:
                    # When ML Engine connector property is CASE-SENSITIVE, set this
                    # parameter to True.
                    teradataml.options.configure.column_casesensitive_handler = True

            vantage_version:
                Specifies the Vantage version of the system teradataml is connected to.
                Types: string
                Example:
                    # Set the Vantage Version
                    teradataml.options.configure.vantage_version = "vantage1.1"

            val_install_location:
                Specifies the name of the database where Vantage Analytic Library functions
                are installed.
                Types: string
                Example:
                    # Set the Vantage Analytic Library install location to 'SYSLIB'
                    # when VAL functions are installed in 'SYSLIB'.
                    teradataml.options.configure.val_install_location = "SYSLIB"

            byom_install_location:
                Specifies the name of the database where Bring Your Own Model functions
                are installed.
                Types: string
                Example:
                    # Set the BYOM install location to 'SYSLIB'
                    # when BYOM functions are installed in 'SYSLIB'.
                    teradataml.options.configure.byom_install_location = "SYSLIB"

            sandbox_container_id:
                Specifies the id of sandbox container that will be used by test_script method.
                Types: string
                Example:
                    # Set the sandbox_container_id.
                    teradataml.options.configure.sandbox_container_id = '734rfjsls3'

            database_version:
                Specifies the actual database version of the system teradataml is connected to.
                Types: string
                Example:
                    # Set the Vantage Version
                    teradataml.options.configure.database_version = "17.05a.00.147"
            
            read_nos_function_mapping:
                Specifies the function mapping name for the read_nos table operator function.
                Types: string
                Example:
                    # Set the read nos function mapping name
                    teradataml.options.configure.read_nos_function_mapping = "read_nos_fm"
            
            write_nos_function_mapping:
                Specifies the function mapping name for the write_nos table operator function.
                Types: string
                Example:
                    # Set the write nos function mapping name
                    teradataml.options.configure.write_nos_function_mapping = "write_nos_fm"

        """
        super().__init__()
        super().__setattr__('default_varchar_size', default_varchar_size)
        super().__setattr__('column_casesensitive_handler', column_casesensitive_handler)
        super().__setattr__('vantage_version', vantage_version)
        super().__setattr__('val_install_location', val_install_location)
        super().__setattr__('byom_install_location', byom_install_location)
        super().__setattr__('sandbox_container_id', sandbox_container_id)
        super().__setattr__('temp_table_database', temp_table_database)
        super().__setattr__('temp_view_database', temp_view_database)
        super().__setattr__('database_version', database_version)
        super().__setattr__('read_nos_function_mapping', read_nos_function_mapping)
        super().__setattr__('write_nos_function_mapping', write_nos_function_mapping)

        
        # internal configurations
        # These configurations are internal and should not be
        # exported to the user's namespace.
        super().__setattr__('_validate_metaexpression', False)
        # Internal parameter, that should be used while testing to validate whether
        # Garbage collection is being done or not.
        super().__setattr__('_validate_gc', False)
        # Internal parameter, that is used for checking if sto sandbox image exists on user's system
        super().__setattr__('_latest_sandbox_exists', False)
        # Internal parameter, that is used for checking whether a container was started by
        # teradataml.
        super().__setattr__('_container_started_by_teradataml', None)
        # Internal parameter, that is used for specifying the global model cataloging schema name which
        # will be used by the byom APIs.
        super().__setattr__('_byom_model_catalog_database', None)
        # Internal parameter, that is used for specifying the global model cataloging table name which
        # will be used by the byom APIs.
        super().__setattr__('_byom_model_catalog_table', None)
        # Internal parameter, that is used for specifying the license information as a string, file
        # path or column name which will be used by the byom APIs.
        super().__setattr__('_byom_model_catalog_license', None)
        # Internal parameter, that is used for specifying the source where the license came from
        # which will be used by the byom APIs.
        super().__setattr__('_byom_model_catalog_license_source', None)
        # Internal parameter, that is used for specifying the license table name
        # where the license is stored
        super().__setattr__('_byom_model_catalog_license_table', None)
        # Internal parameter, that is used for specifying the schema name where
        # the license table is stored
        super().__setattr__('_byom_model_catalog_license_database', None)
        # Internal parameter, that is used for specifying the URL to be used as
        # base URL in UES REST calls
        super().__setattr__('ues_url', None)
        # Internal parameter, that is used for specifying the Authentication token to be used
        # in UES REST calls
        super().__setattr__('auth_token', None)
        # Internal parameter, that is used to specify the certificate file in a secured HTTP request.
        super().__setattr__('certificate_file', False)
        # Internal parameter, that is used for specify the maximum size of the file
        # allowed by UES to upload it.
        super().__setattr__('_ues_max_file_upload_size', 10)
        # Internal parameter, that is used to specify the default environment,
        super().__setattr__('_default_user_env', None)

        # Internal parameter, that is used to post the Code verifier in OAuth work flow.
        super().__setattr__('_oauth_end_point', None)

        # Internal parameter, that is used for specifying the client id in OAuth work flow.
        super().__setattr__('_oauth_client_id', None)

        # Internal parameter, that is used for specifying the ID of Authentication token.
        super().__setattr__('_id_auth_token', None)

        # Internal parameter, that is used for specifying the Authentication token expiry time.
        super().__setattr__('_auth_token_expiry_time', None)

        # Internal parameter, that is used for specifying the refresh token to be used
        # in UES REST calls
        super().__setattr__('_refresh_token', None)

        # Internal parameter, that is used for specifying the refresh token to be used
        # in UES REST calls
        super().__setattr__('_pf_token_username_label', "pf.username")

        # Internal parameter, that is used for specifying the refresh token to be used
        # in UES REST calls
        super().__setattr__('_pf_token_password_label', "pf.pass")
        
        # Internal parameter, that is used for specifying the PAT token state in _AuthWorkflow.
        super().__setattr__('_state_dict', None)

    def __setattr__(self, name, value):
        if hasattr(self, name):
            if name == 'default_varchar_size':
                if not isinstance(value, int):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'int'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
                if value <= 0:
                    raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_POSITIVE_INT, name,
                                                                   "greater than"),
                                              MessageCodes.TDMLDF_POSITIVE_INT)
            elif name == '_ues_max_file_upload_size':
                if type(value) != int:
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'int'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
                if value < 0:
                    raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_POSITIVE_INT, name,
                                                                   "greater than or equal to"),
                                              MessageCodes.TDMLDF_POSITIVE_INT)
            elif name in ['column_casesensitive_handler', '_validate_metaexpression',
                          '_validate_gc', '_latest_sandbox_exists']:

                if not isinstance(value, bool):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'bool'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
            elif name == 'certificate_file':
                if not isinstance(value, str):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'str'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)

                if not os.path.exists(value):
                    msg_code = MessageCodes.EXECUTION_FAILED
                    raise TeradataMlException(Messages.get_message(msg_code,
                                                                   "read contents of file '{}'".format(value),
                                                                   'File does not exist.'),
                                              msg_code)

                if not os.path.isfile(value):
                    msg_code = MessageCodes.EXECUTION_FAILED
                    raise TeradataMlException(Messages.get_message(msg_code,
                                                                   "read contents of file '{}'".format(value),
                                                                   'Not a file.'),
                                              msg_code)

            elif name == 'vantage_version':
                if not isinstance(value, str):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'str'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
                valid_versions = ['vantage1.0', 'vantage1.1', 'vantage1.3', 'vantage2.0']
                value = value.lower()
                if value not in valid_versions:
                    raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                                   value,
                                                                   name,
                                                                   "a value in {}".format(valid_versions)),
                                              MessageCodes.INVALID_ARG_VALUE)

            elif name in ['val_install_location', 'byom_install_location', 'database_version',
                          'read_nos_function_mapping', 'write_nos_function_mapping',
                          '_byom_model_catalog_database', '_byom_model_catalog_table',
                          '_byom_model_catalog_license', '_byom_model_catalog_license_source']:
                if not isinstance(value, str):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'str'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)

            elif name in {'ues_url', 'auth_token', '_oauth_end_point', '_oauth_client_id',
                          '_id_auth_token', '_refresh_token', '_pf_token_username_label',
                          '_pf_token_password_label'}:

                if not isinstance(value, str):
                    raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name, 'str'))

                if len(value) == 0:
                    raise ValueError(Messages.get_message(MessageCodes.ARG_EMPTY, name))

                if name == 'ues_url':
                    value = value[: -1] if value.endswith("/") else value

            elif name in ['sandbox_container_id', '_container_started_by_teradataml',
                          'temp_table_database', 'temp_view_database',
                          "_byom_model_catalog_license_table", "_byom_model_catalog_license_database"]:
                if not isinstance(value, str) and not isinstance(value, type(None)):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'str or None'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)

            elif name in {'_auth_token_expiry_time'}:

                if not isinstance(value, float):
                    raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name, 'float'))

            super().__setattr__(name, value)
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))


configure = _Configure()