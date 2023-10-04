# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: rameshchandra.d@teradata.com
Secondary Owner:

teradataml.common.exceptions
----------
An Error class for the teradataml python module
"""

class TeradataMlException(Exception):
    """
    Teradata Ml Exception class.
    All public functions and methods should only raise TeradataMlException so that
    application code need only catch TeradataMlException.
    Public functions and methods should use the following form

        try:
            # do something useful
        except TeradataMlError:
            # re-raise a TeradataMlException that was raised by one of our internal functions.
            raise
        exception Exception as err:
            # all other exceptions (like driver exceptions) are wrapped in a TeradataMlException
            raise TeradataMlException(msg, code) from err

    Both public and internal functions should raise TeradataMlException for any
    application errors like invalid argument.

    For example:
        if key is not in columnnames:
            raise TeradataMlException(msg, code)


    Internal functions should let other exceptions from the driver bubble up.
    If internal functions would like to do something in a try: except: block like logging,
    then it should use the form

        try:
            # do something useful
        except:
            logger.log ("log something useful")
            # re-raise the error so that it is caught by the calling public function.
            # the calling public function will take care of wrapping the exception in TeradataMlError
            # this will avoid a lot of unnecessary exception handling code.
            raise

    If TeradataMlException was the result of another exception, then the
    attribute __cause__ will be set with the root cause exception.

    """
    def __init__(self, msg, code):
        """
        Initializer for TeradataMlException. Call the parent class initializer and set the code.
        PARAMETERS:
            msg - The error message, should be a standard message from messages._getMessage().
            code - The code, should be from MessageCodes like MessageCodes.CONNECTION_FAILURE.

        RETURNS:
            A TeradataMlException with the error message and code.

        RAISES:

        EXAMPLES:
            if key is not in columnnames:
                raise TeradataMlException(message._getMessage(MessageCodes.CONNECTION_FAILURE), MessageCodes.CONNECTION_FAILURE)
        """
        super(TeradataMlException, self).__init__(msg)
        self.code = code
