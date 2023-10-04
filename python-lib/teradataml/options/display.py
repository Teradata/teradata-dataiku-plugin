"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: karthik.thelukuntla@teradata.com
Secondary Owner: mark.sandan@teradata.com

This file is for providing user configurable options.
"""
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes


class _DisplaySuper(object):

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


class _Display(_DisplaySuper):
    """
    Display options for printing teradataml DataFrames and SQLMR functions.
    """

    max_rows = _create_property('max_rows')
    precision = _create_property('precision')
    byte_encoding = _create_property('byte_encoding')
    print_sqlmr_query = _create_property('print_sqlmr_query')
    blob_length = _create_property('blob_length')
    suppress_vantage_runtime_warnings = _create_property('suppress_vantage_runtime_warnings')

    def __init__(self,
                 max_rows = 10,
                 precision = 3,
                 byte_encoding = 'base16',
                 print_sqlmr_query = False,
                 blob_length=10,
                 suppress_vantage_runtime_warnings=False):
        """
        PARAMETERS:
            max_rows:
                Specifies the maximum number of rows to display while displaying
                teradataml DataFrame. User can configure this parameter using
                display.
                Default Value: 10
                Types: int
                Example:
                    display.max_rows = 20

            precision:
                Specifies the number of decimals to use when rounding the floating
                number. So, while displaying teradataml DataFrame, floating number
                would be rounded to decimals specified by "precision" default.
                User can configure this parameter using display.
                Default Value: 3
                Types: int
                Example:
                    display.precision = 5

            byte_encoding:
                Specifies the encoding style while displaying BYTE, VARBYTE,
                or BLOB data. User can configure this parameter using display.
                Default Value: base16
                Types: str
                Example:
                    display.byte_encoding = "ascii"

            print_sqlmr_query:
                Specifies whether to print the corresponding SQL Query while displaying
                the teradataml DataFrame.
                Default Value: False
                Types: bool
                Example:
                    display.print_sqlmr_query = True

            blob_length:
                Specifies the default length of BLOB column to display in teradataml
                DataFrame. One can set this option to None to display complete BLOB
                data.
                Default Value: 10
                Types: int
                Example:
                    # Set the blob_length.
                    display.blob_length = 20

            suppress_vantage_runtime_warnings:
                Specifies whether to display the warnings raised by the Vantage or not.
                When set to True, warnings raised by Vantage are not displayed.
                Otherwise, warnings are displayed.
                Default Value: False
                Types: bool
                Example:
                    display.suppress_vantage_runtime_warnings = True
        """
        super().__init__()
        super().__setattr__('max_rows', max_rows)
        super().__setattr__('precision', precision)
        super().__setattr__('byte_encoding', byte_encoding)
        super().__setattr__('print_sqlmr_query', print_sqlmr_query)
        super().__setattr__('blob_length', blob_length)
        super().__setattr__('suppress_vantage_runtime_warnings', suppress_vantage_runtime_warnings)

    def __setattr__(self, name, value):
        if hasattr(self, name):
            if name == 'max_rows' or name == 'precision':
                if not isinstance(value, int):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'int'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
                if value <= 0:
                    raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_POSITIVE_INT, name, "greater than"),
                                              MessageCodes.TDMLDF_POSITIVE_INT)
            elif name == 'byte_encoding':
                valid_encodings = ['ascii', 'base16', 'base2', 'base8', 'base64m']
                if not isinstance(value, str):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'str'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)

                value = value.lower()
                if value not in valid_encodings:
                    raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                                   value,
                                                                   name,
                                                                   "a value in {}".format(valid_encodings)),
                                              MessageCodes.INVALID_ARG_VALUE)
            elif name == 'print_sqlmr_query':
                if not isinstance(value, bool):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'bool'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
            elif name == 'blob_length':
                if type(value) not in (int, type(None)):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'int or None'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
                if isinstance(value, int) and value <= 0:
                    raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_POSITIVE_INT, name, "greater than"),
                                              MessageCodes.TDMLDF_POSITIVE_INT)
            elif name == 'suppress_vantage_runtime_warnings':
                if not isinstance(value, bool):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'bool'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)

            super().__setattr__(name, value)
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))


display = _Display()
