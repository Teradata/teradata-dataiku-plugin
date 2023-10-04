# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: rameshchandra.d@teradata.com
Secondary Owner:

teradataml.common.messages
----------
A messages class for holding all text messages that are displayed to the user
"""
from teradataml.common import messagecodes
from teradataml.common.messagecodes import ErrorInfoCodes
from teradataml.common.messagecodes import MessageCodes

class Messages():
    """
    Contains list of messages with respective error codes
    Add new error and message codes in self.messages list whenever codes are added in errormessagecodes
    file.
    """
    __messages = []
    __standard_message = "[Teradata][Plugin]"
    __messages = [
            [ErrorInfoCodes.CONNECTION_SUCCESS, MessageCodes.CONNECTION_SUCCESS],
            [ErrorInfoCodes.CONNECTION_FAILURE, MessageCodes.CONNECTION_FAILURE],
            [ErrorInfoCodes.DISCONNECT_FAILURE, MessageCodes.DISCONNECT_FAILURE],
            [ErrorInfoCodes.MISSING_ARGS, MessageCodes.MISSING_ARGS],
            [ErrorInfoCodes.OVERWRITE_CONTEXT, MessageCodes.OVERWRITE_CONTEXT],
            [ErrorInfoCodes.FORMULA_INVALID_FORMAT, MessageCodes.FORMULA_INVALID_FORMAT],
            [ErrorInfoCodes.ARG_EMPTY, MessageCodes.ARG_EMPTY],
            [ErrorInfoCodes.ARG_NONE, MessageCodes.ARG_NONE],
            [ErrorInfoCodes.DICT_ARG_KEY_VALUE_EMPTY, MessageCodes.DICT_ARG_KEY_VALUE_EMPTY],
            [ErrorInfoCodes.INVALID_DICT_KEYS, MessageCodes.INVALID_DICT_KEYS],
            [ErrorInfoCodes.DUPLICATE_DICT_KEYS_NAMES, MessageCodes.DUPLICATE_DICT_KEYS_NAMES],
            [ErrorInfoCodes.INVALID_DICT_KEY_VALUE_LENGTH, MessageCodes.INVALID_DICT_KEY_VALUE_LENGTH],
            [ErrorInfoCodes.EITHER_FUNCTION_OR_ARGS, MessageCodes.EITHER_FUNCTION_OR_ARGS],
            [ErrorInfoCodes.INVALID_ARG_VALUE, MessageCodes.INVALID_ARG_VALUE],
            [ErrorInfoCodes.INVALID_DICT_ARG_VALUE, MessageCodes.INVALID_DICT_ARG_VALUE],
            [ErrorInfoCodes.TDF_UNKNOWN_COLUMN, MessageCodes.TDF_UNKNOWN_COLUMN],
            [ErrorInfoCodes.AED_LIBRARY_LOAD_FAIL, MessageCodes.AED_LIBRARY_LOAD_FAIL],
            [ErrorInfoCodes.AED_LIBRARY_NOT_LOADED, MessageCodes.AED_LIBRARY_NOT_LOADED],
            [ErrorInfoCodes.AED_EXEC_FAILED, MessageCodes.AED_EXEC_FAILED],
            [ErrorInfoCodes.AED_NON_ZERO_STATUS, MessageCodes.AED_NON_ZERO_STATUS],
            [ErrorInfoCodes.AED_QUERY_COUNT_MISMATCH, MessageCodes.AED_QUERY_COUNT_MISMATCH],
            [ErrorInfoCodes.AED_NODE_QUERY_LENGTH_MISMATCH, MessageCodes.AED_NODE_QUERY_LENGTH_MISMATCH],
            [ErrorInfoCodes.AED_INVALID_ARGUMENT, MessageCodes.AED_INVALID_ARGUMENT],
            [ErrorInfoCodes.AED_INVALID_GEN_TABLENAME, MessageCodes.AED_INVALID_GEN_TABLENAME],
            [ErrorInfoCodes.AED_INVALID_SQLMR_QUERY, MessageCodes.AED_INVALID_SQLMR_QUERY],
            [ErrorInfoCodes.AED_NODE_ALREADY_EXECUTED, MessageCodes.AED_NODE_ALREADY_EXECUTED],
            [ErrorInfoCodes.AED_SHOW_QUERY_MULTIPLE_OPTIONS, MessageCodes.AED_SHOW_QUERY_MULTIPLE_OPTIONS],
            [ErrorInfoCodes.SQL_UNKNOWN_KEY, MessageCodes.SQL_UNKNOWN_KEY],
            [ErrorInfoCodes.TDMLDF_CREATE_FAIL, MessageCodes.TDMLDF_CREATE_FAIL],
            [ErrorInfoCodes.TDMLDF_EXEC_SQL_FAILED, MessageCodes.TDMLDF_EXEC_SQL_FAILED],
            [ErrorInfoCodes.TDMLDF_CREATE_GARBAGE_COLLECTOR, MessageCodes.TDMLDF_CREATE_GARBAGE_COLLECTOR],
            [ErrorInfoCodes.TDMLDF_DELETE_GARBAGE_COLLECTOR, MessageCodes.TDMLDF_DELETE_GARBAGE_COLLECTOR],
            [ErrorInfoCodes.IS_NOT_VALID_DF, MessageCodes.IS_NOT_VALID_DF],
            [ErrorInfoCodes.TD_MAX_COL_MESSAGE, MessageCodes.TD_MAX_COL_MESSAGE],
            [ErrorInfoCodes.INVALID_PRIMARY_INDEX, MessageCodes.INVALID_PRIMARY_INDEX],
            [ErrorInfoCodes.INDEX_ALREADY_EXISTS, MessageCodes.INDEX_ALREADY_EXISTS],
            [ErrorInfoCodes.INVALID_INDEX_LABEL, MessageCodes.INVALID_INDEX_LABEL],
            [ErrorInfoCodes.TABLE_ALREADY_EXISTS, MessageCodes.TABLE_ALREADY_EXISTS],
            [ErrorInfoCodes.COPY_TO_SQL_FAIL, MessageCodes.COPY_TO_SQL_FAIL],
            [ErrorInfoCodes.TDMLDF_INFO_ERROR, MessageCodes.TDMLDF_INFO_ERROR],
            [ErrorInfoCodes.TDMLDF_UNKNOWN_TYPE, MessageCodes.TDMLDF_UNKNOWN_TYPE],
            [ErrorInfoCodes.TDMLDF_POSITIVE_INT, MessageCodes.TDMLDF_POSITIVE_INT],
            [ErrorInfoCodes.TDMLDF_SELECT_DF_FAIL, MessageCodes.TDMLDF_SELECT_DF_FAIL],
            [ErrorInfoCodes.TDMLDF_SELECT_INVALID_FORMAT, MessageCodes.TDMLDF_SELECT_INVALID_FORMAT],
            [ErrorInfoCodes.TDMLDF_SELECT_INVALID_COLUMN, MessageCodes.TDMLDF_SELECT_INVALID_COLUMN],
            [ErrorInfoCodes.TDMLDF_SELECT_EXPR_UNSPECIFIED, MessageCodes.TDMLDF_SELECT_EXPR_UNSPECIFIED],
            [ErrorInfoCodes.TDMLDF_SELECT_NONE_OR_EMPTY, MessageCodes.TDMLDF_SELECT_NONE_OR_EMPTY],
            [ErrorInfoCodes.INVALID_LENGTH_ARGS, MessageCodes.INVALID_LENGTH_ARGS],
            [ErrorInfoCodes.UNSUPPORTED_DATATYPE, MessageCodes.UNSUPPORTED_DATATYPE],
            [ErrorInfoCodes.UNSUPPORTED_DICT_KEY_VALUE_DTYPE, MessageCodes.UNSUPPORTED_DICT_KEY_VALUE_DTYPE],
            [ErrorInfoCodes.TDMLDF_DROP_ARGS, MessageCodes.TDMLDF_DROP_ARGS],
            [ErrorInfoCodes.TDMLDF_INVALID_DROP_AXIS, MessageCodes.TDMLDF_INVALID_DROP_AXIS],
            [ErrorInfoCodes.TDMLDF_DROP_INVALID_COL, MessageCodes.TDMLDF_DROP_INVALID_COL],
            [ErrorInfoCodes.TDMLDF_DROP_INVALID_INDEX_TYPE, MessageCodes.TDMLDF_DROP_INVALID_INDEX_TYPE],
            [ErrorInfoCodes.TDMLDF_DROP_INVALID_COL_NAMES, MessageCodes.TDMLDF_DROP_INVALID_COL_NAMES],
            [ErrorInfoCodes.TDMLDF_DROP_ALL_COLS, MessageCodes.TDMLDF_DROP_ALL_COLS],
            [ErrorInfoCodes.LIST_DB_TABLES_FAILED, MessageCodes.LIST_DB_TABLES_FAILED],
            [ErrorInfoCodes.INVALID_CONTEXT_CONNECTION, MessageCodes.INVALID_CONTEXT_CONNECTION],
            [ErrorInfoCodes.DF_LABEL_MISMATCH, MessageCodes.DF_LABEL_MISMATCH],
            [ErrorInfoCodes.DF_WITH_NO_COLUMNS, MessageCodes.DF_WITH_NO_COLUMNS],
            [ErrorInfoCodes.DATA_EXPORT_FAILED, MessageCodes.DATA_EXPORT_FAILED],
            [ErrorInfoCodes.TDMLDF_INVALID_JOIN_CONDITION, MessageCodes.TDMLDF_INVALID_JOIN_CONDITION],
            [ErrorInfoCodes.TDMLDF_INVALID_TABLE_ALIAS, MessageCodes.TDMLDF_INVALID_TABLE_ALIAS],
            [ErrorInfoCodes.TDMLDF_REQUIRED_TABLE_ALIAS, MessageCodes.TDMLDF_REQUIRED_TABLE_ALIAS],
            [ErrorInfoCodes.TDMLDF_COLUMN_ALREADY_EXISTS, MessageCodes.TDMLDF_COLUMN_ALREADY_EXISTS],
            [ErrorInfoCodes.INVALID_LENGTH_ARGS, MessageCodes.INVALID_LENGTH_ARGS],
            [ErrorInfoCodes.TDMLDF_AGGREGATE_UNSUPPORTED, MessageCodes.TDMLDF_AGGREGATE_UNSUPPORTED],
            [ErrorInfoCodes.TDMLDF_INVALID_AGGREGATE_OPERATION, MessageCodes.TDMLDF_INVALID_AGGREGATE_OPERATION],
            [ErrorInfoCodes.INSERTION_INCOMPATIBLE, MessageCodes.INSERTION_INCOMPATIBLE],
            [ErrorInfoCodes.TABLE_OBJECT_CREATION_FAILED, MessageCodes.TABLE_OBJECT_CREATION_FAILED],
            [ErrorInfoCodes.FORMULA_MISSING_DEPENDENT_VARIABLE, MessageCodes.FORMULA_MISSING_DEPENDENT_VARIABLE],
            [ErrorInfoCodes.TDMLDF_COLUMN_IN_ARG_NOT_FOUND, MessageCodes.TDMLDF_COLUMN_IN_ARG_NOT_FOUND],
            [ErrorInfoCodes.TDMLDF_AGGREGATE_INVALID_COLUMN, MessageCodes.TDMLDF_AGGREGATE_INVALID_COLUMN],
            [ErrorInfoCodes.TDMLDF_AGGREGATE_COMBINED_ERR, MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR],
            [ErrorInfoCodes.DEPENDENT_ARGUMENT, MessageCodes.DEPENDENT_ARGUMENT],
            [ErrorInfoCodes.DROP_FAILED, MessageCodes.DROP_FAILED],
            [ErrorInfoCodes.UNSUPPORTED_ARGUMENT, MessageCodes.UNSUPPORTED_ARGUMENT],
            [ErrorInfoCodes.EITHER_THIS_OR_THAT_ARGUMENT, MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT],
            [ErrorInfoCodes.TDMLDF_UNEQUAL_NUMBER_OF_COLUMNS, MessageCodes.TDMLDF_UNEQUAL_NUMBER_OF_COLUMNS],
            [ErrorInfoCodes.TDMLDF_INDEXES_ARE_NONE, MessageCodes.TDMLDF_INDEXES_ARE_NONE],
            [ErrorInfoCodes.MODEL_ALREADY_EXISTS, MessageCodes.MODEL_ALREADY_EXISTS],
            [ErrorInfoCodes.MODEL_NOT_FOUND, MessageCodes.MODEL_NOT_FOUND],
            [ErrorInfoCodes.MODEL_WITH_SEARCH_CRITERION_NOT_FOUND, MessageCodes.MODEL_WITH_SEARCH_CRITERION_NOT_FOUND],
            [ErrorInfoCodes.MODEL_CATALOGING_TABLE_DOES_EXIST, MessageCodes.MODEL_CATALOGING_TABLE_DOES_EXIST],
            [ErrorInfoCodes.TABLE_DOES_NOT_EXIST, MessageCodes.TABLE_DOES_NOT_EXIST],
            [ErrorInfoCodes.EMPTY_FILE, MessageCodes.EMPTY_FILE],
            [ErrorInfoCodes.MODEL_CATALOGING_OPERATION_FAILED, MessageCodes.MODEL_CATALOGING_OPERATION_FAILED],
            [ErrorInfoCodes.UNKNOWN_MODEL_ENGINE, MessageCodes.UNKNOWN_MODEL_ENGINE],
            [ErrorInfoCodes.FUNCTION_JSON_MISSING, MessageCodes.FUNCTION_JSON_MISSING],
            [ErrorInfoCodes.CANNOT_SAVE_RETRIEVED_MODEL, MessageCodes.CANNOT_SAVE_RETRIEVED_MODEL],
            [ErrorInfoCodes.CANNOT_TRANSLATE_TO_TDML_NAME, MessageCodes.CANNOT_TRANSLATE_TO_TDML_NAME],
            [ErrorInfoCodes.MUST_PASS_ARGUMENT, MessageCodes.MUST_PASS_ARGUMENT],
            [ErrorInfoCodes.CONFIG_ALIAS_DUPLICATES, MessageCodes.CONFIG_ALIAS_DUPLICATES],
            [ErrorInfoCodes.CONFIG_ALIAS_ENGINE_NOT_SUPPORTED, MessageCodes.CONFIG_ALIAS_ENGINE_NOT_SUPPORTED],
            [ErrorInfoCodes.CONFIG_ALIAS_ANLY_FUNC_NOT_FOUND, MessageCodes.CONFIG_ALIAS_ANLY_FUNC_NOT_FOUND],
            [ErrorInfoCodes.CONFIG_ALIAS_VANTAGE_VERSION_NOT_SUPPORTED, MessageCodes.CONFIG_ALIAS_VANTAGE_VERSION_NOT_SUPPORTED],
            [ErrorInfoCodes.CONFIG_ALIAS_CONFIG_FILE_NOT_FOUND, MessageCodes.CONFIG_ALIAS_CONFIG_FILE_NOT_FOUND],
            [ErrorInfoCodes.CONFIG_ALIAS_INVALID_FUNC_MAPPING, MessageCodes.CONFIG_ALIAS_INVALID_FUNC_MAPPING],
            [ErrorInfoCodes.USE_FUNCTION_TO_INSTANTIATE, MessageCodes.USE_FUNCTION_TO_INSTANTIATE],
            [ErrorInfoCodes.SERIES_INFO_ERROR, MessageCodes.SERIES_INFO_ERROR],
            [ErrorInfoCodes.SERIES_CREATE_FAIL, MessageCodes.SERIES_CREATE_FAIL],
            [ErrorInfoCodes.UNSUPPORTED_OPERATION, MessageCodes.UNSUPPORTED_OPERATION],
            [ErrorInfoCodes.INVALID_COLUMN_TYPE, MessageCodes.INVALID_COLUMN_TYPE],
            [ErrorInfoCodes.SETOP_COL_TYPE_MISMATCH, MessageCodes.SETOP_COL_TYPE_MISMATCH],
            [ErrorInfoCodes.SETOP_FAILED, MessageCodes.SETOP_FAILED],
            [ErrorInfoCodes.SETOP_INVALID_DF_COUNT, MessageCodes.SETOP_INVALID_DF_COUNT],
            [ErrorInfoCodes.AED_SETOP_INVALID_NUMBER_OF_INPUT_NODES, MessageCodes.AED_SETOP_INVALID_NUMBER_OF_INPUT_NODES],
            [ErrorInfoCodes.AED_SETOP_INPUT_TABLE_COLUMNS_COUNT_MISMATCH, MessageCodes.AED_SETOP_INPUT_TABLE_COLUMNS_COUNT_MISMATCH],
            [ErrorInfoCodes.SET_TABLE_DUPICATE_ROW, MessageCodes.SET_TABLE_DUPICATE_ROW],
            [ErrorInfoCodes.IGNORE_ARGS_WARN, MessageCodes.IGNORE_ARGS_WARN],
            [ErrorInfoCodes.FUNCTION_NOT_SUPPORTED, MessageCodes.FUNCTION_NOT_SUPPORTED],
            [ErrorInfoCodes.UNABLE_TO_GET_VANTAGE_VERSION, MessageCodes.UNABLE_TO_GET_VANTAGE_VERSION],
            [ErrorInfoCodes.ARG_VALUE_INTERSECTION_NOT_ALLOWED, MessageCodes.ARG_VALUE_INTERSECTION_NOT_ALLOWED],
            [ErrorInfoCodes.TDMLDF_LBOUND_UBOUND, MessageCodes.TDMLDF_LBOUND_UBOUND],
            [ErrorInfoCodes.ARG_VALUE_CLASS_DEPENDENCY, MessageCodes.ARG_VALUE_CLASS_DEPENDENCY],
            [ErrorInfoCodes.SET_TABLE_NO_PI, MessageCodes.SET_TABLE_NO_PI],
            [ErrorInfoCodes.INVALID_DF_LENGTH, MessageCodes.INVALID_DF_LENGTH],
            [ErrorInfoCodes.VANTAGE_WARNING, MessageCodes.VANTAGE_WARNING],
            [ErrorInfoCodes.DEPENDENT_ARG_MISSING, MessageCodes.DEPENDENT_ARG_MISSING],
            [ErrorInfoCodes.FASTLOAD_FAILS, MessageCodes.FASTLOAD_FAILS],
            [ErrorInfoCodes.REMOVE_FILE_FAILED, MessageCodes.REMOVE_FILE_FAILED],
            [ErrorInfoCodes.INPUT_FILE_NOT_FOUND, MessageCodes.INPUT_FILE_NOT_FOUND],
            [ErrorInfoCodes.INSTALL_FILE_FAILED, MessageCodes.INSTALL_FILE_FAILED],
            [ErrorInfoCodes.REPLACE_FILE_FAILED, MessageCodes.REPLACE_FILE_FAILED],
            [ErrorInfoCodes.URL_UNREACHABLE, MessageCodes.URL_UNREACHABLE],
            [ErrorInfoCodes.FROM_QUERY_SELECT_SUPPORTED, MessageCodes.FROM_QUERY_SELECT_SUPPORTED],
            [ErrorInfoCodes.INVALID_LENGTH_STRING_ARG, MessageCodes.INVALID_LENGTH_STRING_ARG],
            [ErrorInfoCodes.INVALID_LENGTH_ARG, MessageCodes.INVALID_LENGTH_ARG],
            [ErrorInfoCodes.LIST_SELECT_NONE_OR_EMPTY, MessageCodes.LIST_SELECT_NONE_OR_EMPTY],
            [ErrorInfoCodes.SANDBOX_CONTAINER_ERROR, MessageCodes.SANDBOX_CONTAINER_ERROR],
            [ErrorInfoCodes.DATAFRAME_LIMIT_ERROR, MessageCodes.DATAFRAME_LIMIT_ERROR],
            [ErrorInfoCodes.SPECIFY_AT_LEAST_ONE_ARG, MessageCodes.SPECIFY_AT_LEAST_ONE_ARG],
            [ErrorInfoCodes.NOT_ALLOWED_VALUES, MessageCodes.NOT_ALLOWED_VALUES],
            [ErrorInfoCodes.ARGUMENT_VALUE_SAME, MessageCodes.ARGUMENT_VALUE_SAME],
            [ErrorInfoCodes.UNKNOWN_INSTALL_LOCATION, MessageCodes.UNKNOWN_INSTALL_LOCATION],
            [ErrorInfoCodes.UNKNOWN_ARGUMENT, MessageCodes.UNKNOWN_ARGUMENT],
            [ErrorInfoCodes.CANNOT_USE_TOGETHER_WITH, MessageCodes.CANNOT_USE_TOGETHER_WITH],
            [ErrorInfoCodes.SCRIPT_LOCAL_RUN_ERROR, MessageCodes.SCRIPT_LOCAL_RUN_ERROR],
            [ErrorInfoCodes.SANDBOX_CONNECTION_ERROR,MessageCodes.SANDBOX_CONNECTION_ERROR],
            [ErrorInfoCodes.SANDBOX_QUERY_ERROR, MessageCodes.SANDBOX_QUERY_ERROR],
            [ErrorInfoCodes.SANDBOX_SCRIPT_ERROR, MessageCodes.SANDBOX_SCRIPT_ERROR],
            [ErrorInfoCodes.INVALID_COLUMN_RANGE_FORMAT, MessageCodes.INVALID_COLUMN_RANGE_FORMAT],
            [ErrorInfoCodes.MIXED_TYPES_IN_COLUMN_RANGE, MessageCodes.MIXED_TYPES_IN_COLUMN_RANGE],
            [ErrorInfoCodes.STORED_PROCEDURE_FAILED, MessageCodes.STORED_PROCEDURE_FAILED],
            [ErrorInfoCodes.NO_ENVIRONMENT_FOUND, MessageCodes.NO_ENVIRONMENT_FOUND],
            [ErrorInfoCodes.UNSUPPORTED_FILE_EXTENSION, MessageCodes.UNSUPPORTED_FILE_EXTENSION],
            [ErrorInfoCodes.FILE_EMPTY, MessageCodes.FILE_EMPTY],
            [ErrorInfoCodes.SANDBOX_CONTAINER_EXISTS, MessageCodes.SANDBOX_CONTAINER_EXISTS],
            [ErrorInfoCodes.SANDBOX_IMAGE_NOT_FOUND, MessageCodes.SANDBOX_IMAGE_NOT_FOUND],
            [ErrorInfoCodes.SANDBOX_CONTAINER_NOT_FOUND, MessageCodes.SANDBOX_CONTAINER_NOT_FOUND],
            [ErrorInfoCodes.SANDBOX_SKIP_IMAGE_LOAD, MessageCodes.SANDBOX_SKIP_IMAGE_LOAD],
            [ErrorInfoCodes.PYTHON_NOT_INSTALLED, MessageCodes.PYTHON_NOT_INSTALLED],
            [ErrorInfoCodes.CONTAINER_STARTED_BY_TERADATAML_EXISTS,
             MessageCodes.CONTAINER_STARTED_BY_TERADATAML_EXISTS],
            [ErrorInfoCodes.SANDBOX_CONTAINER_NOT_RUNNING, MessageCodes.SANDBOX_CONTAINER_NOT_RUNNING],
            [ErrorInfoCodes.SANDBOX_CONTAINER_CAN_NOT_BE_STARTED, MessageCodes.SANDBOX_CONTAINER_CAN_NOT_BE_STARTED],
            [ErrorInfoCodes.INT_ARGUMENT_COMPARISON, MessageCodes.INT_ARGUMENT_COMPARISON],
            [ErrorInfoCodes.EXECUTION_FAILED, MessageCodes.EXECUTION_FAILED],
            [ErrorInfoCodes.INVALID_COLUMN_DATATYPE, MessageCodes.INVALID_COLUMN_DATATYPE],
            [ErrorInfoCodes.MISSING_JSON_FIELD, MessageCodes.MISSING_JSON_FIELD],
            [ErrorInfoCodes.INVALID_JSON, MessageCodes.INVALID_JSON],
            [ErrorInfoCodes.DUPLICATE_PARAMETER, MessageCodes.DUPLICATE_PARAMETER],
            [ErrorInfoCodes.INVALID_FUNCTION_NAME, MessageCodes.INVALID_FUNCTION_NAME],
            [ErrorInfoCodes.NO_GEOM_COLUMN_EXIST, MessageCodes.NO_GEOM_COLUMN_EXIST],
            [ErrorInfoCodes.GEOSEQ_USER_FIELD_NUM, MessageCodes.GEOSEQ_USER_FIELD_NUM],
            [ErrorInfoCodes.RESERVED_KEYWORD, MessageCodes.RESERVED_KEYWORD],
            [ErrorInfoCodes.INVALID_LIST_LENGTH, MessageCodes.INVALID_LIST_LENGTH],
            [ErrorInfoCodes.EXECUTION_FAILED, MessageCodes.FUNC_EXECUTION_FAILED]
    ]

    @staticmethod
    def get_message(messagecode, *variables, **kwargs):
        """
        Generate a message associated with standard message and error code .

        PARAMETERS:
            messagecode(Required)  - Message  to be returned to the user when needed to be raised based on \
                                    the associated  MessageCode
            variables(Optional) -   List of arguments to mention if any missing arguments.
            kwargs(Optional)  - dictionary of keyword arguments for displaying the key and its desired value .

        RETURNS:
            Message with standard python message and message code.


        RAISES:

        EXAMPLES:
            from teradataml.common.messagecodes import MessageCodes
            from teradataml.common.messages import Messages
            Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_REFERENCE_TYPE, "arg_name","data")
            msg = messages._getMessage(messagecode = MessageCodes.TABLE_CREATE)
            msg = messages._getMessage(messagecode = MessageCodes.MISSING_ARGS,missArgs)

        """
        for msg in Messages.__messages:
            if msg[1] == messagecode :
                message = "{}({}) {}".format(Messages.__standard_message, msg[0].value, msg[1].value)
                if len(variables) != 0:
                    message = message.format(*variables)
                if len(kwargs) != 0 :
                    message = "{} {}".format(message, kwargs)

        return message
