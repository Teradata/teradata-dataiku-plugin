# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: rameshchandra.d@teradata.com
Secondary Owner:

teradataml.common.teradatamllog
----------
A teradata logging interfaces for Teradatml python based clients.
"""
import logging, sys

DEBUG = logging.DEBUG
INFO = logging.INFO
ERROR = logging.ERROR

"""
Initializer for TeradataPythonLog logger.
Sets the formatter to log in the following format:
asctime level filename:lineno message

Example:
2018-02-02 14:06:56,639 DEBUG dataframe.py:157 This is a message

Users should not explicitly create a TeradataPythonLog.
Users should get a TeradataPythonLog by calling context.getLogger() or teradatapylog.getLogger()

EXAMPLE:
logger = Context.getLogger()

"""

#Create a formatter for the logger
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s')

#Use standard out for the stream handler
streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(formatter)

#Get the TeradataPythonLog logger and set the handler.
logger = logging.getLogger(__name__)
logger.addHandler(streamhandler)
#Default level is ERROR
logger.setLevel(ERROR)


def getLogger():
    """
    Get the default TeradataPythonLog for logging. This is mainly for internal use by our modules.
    Users should use context.getLogger()

    PARAMETERS:

    RETURNS:
        A TeradataPyLog logger for logging messages.

    RAISES:

    EXAMPLES:
        from TeradataPython import teradatapylog
        logger = teradatapylog.getLogger()

    """
    return logging.getLogger(__name__)
