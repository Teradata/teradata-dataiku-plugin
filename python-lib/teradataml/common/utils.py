# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: mounika.kotha@teradata.com
Secondary Owner:

This is a common class to include common functionality required
by other classes which can be reused according to the need.

Add all the common functions in this class like creating temporary table names, getting
the datatypes etc.
"""
from pathlib import Path
import os
import requests

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes

from teradataml.options.configure import configure
from teradataml.common.constants import HTTPRequest

import warnings
from teradataml.utils.validators import _Validators




class UtilFuncs():


    @staticmethod
    def _as_list(obj):
        """
        Function to convert an object to list, i.e., just enclose the value passed to the
        function in a list and return the same, if it is not of list type.
        PARAMETERS:
            obj:
                Required Argument.
                Specifies the object to be enclosed in a list.
                Types: Any type except list.
        RETURNS:
            list
        RAISES:
            None.
        EXAMPLES:
            obj = UtilFuncs._as_list("vantage1.0")
        """
        return obj if isinstance(obj, list) else [obj]




    @staticmethod
    def _get_positive_infinity():
        """
        Description:
            Function to get the positive infinity.

        RETURNS:
            float

        RAISES:
            None

        EXAMPLES:
            inf = UtilFuncs._get_positive_infinity()
        """
        return float("inf")
    
    @staticmethod
    def _get_function_mappings_from_config_file(alias_config_file):
        """
        Function to return the function mappings given the location of configuration file in
        argument 'alias_config_file'.

        PARAMETERS:
            alias_config_file:
                Required Argument.
                Specifies the location of configuration file to be read.

        RETURNS:
            Function mappings as a dictionary of function_names to alias_names.

        RAISES:
            TeradataMLException

        EXAMPLES:
            UtilFuncs._get_function_mappings_from_config_file("config_file_location")

        """
        repeated_function_names = []
        function_mappings = {}
        invalid_function_mappings = []
        invalid_function_mappings_line_nos = []
        # Reading configuration files
        with open(alias_config_file, 'r') as fread:
            for line_no, line in enumerate(fread.readlines()):
                line = line.strip()

                # Ignoring empty lines in the config files.
                if line == "":
                    continue

                # If the separator ":" is not present.
                if ':' not in line:
                    invalid_function_mappings.append(line)
                    invalid_function_mappings_line_nos.append(str(line_no + 1))
                else:
                    func_name, alias_name = line.split(":")
                    func_name = func_name.strip()
                    alias_name = alias_name.strip()

                    # First line of 'alias_config_file' has header "functionName:aliasName".
                    if line_no == 0 and func_name == "functionName" and alias_name == "aliasName":
                        continue

                    if func_name == "" or alias_name == "":
                        invalid_function_mappings.append(line)
                        invalid_function_mappings_line_nos.append(str(line_no + 1))
                        continue

                    if func_name.lower() in function_mappings:
                        repeated_function_names.append(func_name.lower())

                    # Loading function maps with lower values for key.
                    function_mappings[func_name.lower()] = alias_name

        # Presence of Invalid function mappings in the 'alias_config_file'.
        if len(invalid_function_mappings) > 0:
            err_ = Messages.get_message(MessageCodes.CONFIG_ALIAS_INVALID_FUNC_MAPPING)
            err_ = err_.format("', '".join(invalid_function_mappings),
                               ", ".join(invalid_function_mappings_line_nos),
                               alias_config_file)
            raise TeradataMlException(err_, MessageCodes.CONFIG_ALIAS_INVALID_FUNC_MAPPING)

        # Raising teradataml exception if there are any duplicates in function names.
        if len(repeated_function_names) > 0:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.CONFIG_ALIAS_DUPLICATES).format(alias_config_file,
                                                             ", ".join(repeated_function_names)),
                                      MessageCodes.CONFIG_ALIAS_DUPLICATES)

        return function_mappings
    
    @staticmethod
    def _check_alias_config_file_exists(vantage_version, alias_config_file):
        """
        Function to validate whether alias_config_file exists for the current vantage version.

        PARAMETERS:
            vantage_version:
                Required Argument.
                Specifies the current vantage version.

            alias_config_file:
                Required Argument.
                Specifies the location of configuration file to be read.

        RETURNS:
            True, if the file 'alias_config_file' is present in the
            teradataml/config directory for the current vantage version.

        RAISES:
            TeradataMLException

        EXAMPLES:
            UtilFuncs._check_alias_config_file_exists("vantage1.0", "config_file_location")

        """
        # Raise exception if alias config file is not defined.
        if not Path(alias_config_file).exists():
            raise TeradataMlException(Messages.get_message(
                MessageCodes.CONFIG_ALIAS_CONFIG_FILE_NOT_FOUND).format(alias_config_file,
                                                                        vantage_version),
                                      MessageCodes.CONFIG_ALIAS_CONFIG_FILE_NOT_FOUND)


    @staticmethod
    def _get_file_size(file_path, in_mb=True):
        """
        Description:
            Function to get the size of file, given absolute file path.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute file path of the file.
                Types: str

            in_mb:
                Optional Argument.
                Specifies whether to get the file size in mega bytes or not.
                If True, size of the file returns in MB's. Otherwise, returns
                in bytes.
                Default value: True
                Types: bool

        RETURNS:
            int OR float

        RAISES:
            TeradataMlException

        EXAMPLES:
            file_size = UtilFuncs._get_file_size("/abc/xyz.txt")
        """
        size_in_bytes = os.path.getsize(file_path)

        return size_in_bytes/(1024*1024.0) if in_mb else size_in_bytes
    
    @staticmethod
    def _get_file_contents(file_path, read_in_binary_mode=False):
        """
        Description:
            Function to get the file content from a file, given absolute
            file path.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute file path of the file.
                Types: str

            read_in_binary_mode:
                Optional Argument.
                Specifies whether to read the file in binary format or not.
                If True, read the file in binary mode.
                If False, read the file in ASCII mode.
                Default value: False
                Types: bool

        RETURNS:
            str OR bytes

        RAISES:
            TeradataMlException

        EXAMPLES:
            obj = UtilFuncs._get_file_contents("/abc/xyz.txt")
            obj = UtilFuncs._get_file_contents("/abc/xyz.txt", True)
        """
        try:
            mode = 'r'
            if read_in_binary_mode:
                mode = 'rb'
            with open(file_path, mode) as file_data:
                _Validators._check_empty_file(file_path)
                return file_data.read()
        except TeradataMlException:
            raise
        except FileNotFoundError:
            raise
        except Exception as err:
            msg_code = MessageCodes.EXECUTION_FAILED
            raise TeradataMlException(
                Messages.get_message(msg_code, "read contents of file '{}'".format(file_path), str(err)), msg_code)

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






