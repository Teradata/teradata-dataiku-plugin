from teradatasqlalchemy import (BYTEINT, SMALLINT, INTEGER, BIGINT, DECIMAL, FLOAT, NUMBER)
from teradatasqlalchemy import (TIMESTAMP, DATE, TIME)
from teradatasqlalchemy import (CHAR, VARCHAR, CLOB)
from teradatasqlalchemy import (BYTE, VARBYTE, BLOB)
from teradatasqlalchemy import (PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP)
from teradatasqlalchemy import (INTERVAL_YEAR, INTERVAL_YEAR_TO_MONTH, INTERVAL_MONTH, INTERVAL_DAY,
                                INTERVAL_DAY_TO_HOUR, INTERVAL_DAY_TO_MINUTE, INTERVAL_DAY_TO_SECOND,
                                INTERVAL_HOUR, INTERVAL_HOUR_TO_MINUTE, INTERVAL_HOUR_TO_SECOND,
                                INTERVAL_MINUTE, INTERVAL_MINUTE_TO_SECOND, INTERVAL_SECOND)
from teradatasqlalchemy import (GEOMETRY, MBB, MBR)
from teradataml.common.td_coltype_code_to_tdtype import HELP_COL_TYPE_TO_TDTYPE
from teradataml.common.constants import TeradataTypes, PythonTypes
from datetime import datetime, time, date

#
# Pre-defined class for validating argument types for args that accept list or
# tuple as input.
#
class _ListOf:
    """
    A class to imitate the type - List of x-type.
    For example,
        list of str
        list of int or float
        etc.
    """
    def __init__(self, dtypes):
        """
        Constructor of the class.

        PARAMETERS:
            dtypes:
                Required Argument.
                Specifies the types, which can be part of the list.
                Types: type or tuple of types
        """
        self._type = dtypes
        self.__explicit_bool_validation = False
        self.__is_tuple = False
        self._str_repr_prefix = "list of "
        # If individual element type to be checked is int,
        # then the bool values should be handled carefully, and
        # hence set the '__explicit_bool_validation' to True.
        if isinstance(self._type, type):
            if self._type == int:
                self.__explicit_bool_validation = True
        elif isinstance(self._type, tuple):
            self.__is_tuple = True
            if int in self._type:
                self.__explicit_bool_validation = True

    def __str__(self):
        """
        Returns the string representation of the class for printing in errors.
        """
        if isinstance(self._type, type):
            # If _type is instance of type, then retrieve the type name
            # directly.
            tval = self._type.__name__
        elif isinstance(self._type, tuple):
            # If _type is instance of type, then retrieve the name
            # of the each type by joining them with " or ".
            tval = " or ".join([x.__name__ for x in list(self._type)])
        else:
            # Anything else, just use it as is.
            tval = self._type
        return "{}{}".format(self._str_repr_prefix, tval)

    def _element_instance_check(self, obj):
        """
        Function validates each and every element in "obj" against the
        expected type.

        PARAMETERS:
            obj:
                Required Arguments.
                Specifies the object containing elements to be verified.
                Types: list

        RETURNS:
            True, if all elements are of type reference by self,__type,
            False, otherwise.
        """
        inst_bools = []
        for val in obj:
            if self.__explicit_bool_validation:
                if self.__is_tuple:
                    inst_bools.append(type(val) in self._type)
                else:
                    inst_bools.append(type(val) == self._type)
            else:
                inst_bools.append(isinstance(val, self._type))
        return all(inst_bools)

    def __instancecheck__(self, obj):
        """
        Overrides a method to perform isinstance check.
        """
        if not isinstance(obj, list):
            # If obj is not instance of list, return False.
            return False

        return self._element_instance_check(obj)

class _TupleOf(_ListOf):
    """
    A class to imitate the type - Tuple of x-type.
    For example,
        tuple of str
        tuple of int or float
        etc.
    """

    def __init__(self, dtypes):
        """
        Constructor of the class.

        PARAMETERS:
            dtypes:
                Required Argument.
                Specifies the types, which can be part of the tuple.
                Types: type or tuple of types
        """
        super(_TupleOf, self).__init__(dtypes)
        self._str_repr_prefix = "tuple of "

    def __instancecheck__(self, obj):
        """
        Overrides a method to perform isinstance check.
        """
        if not isinstance(obj, tuple):
            # If obj is not instance of list, return False.
            return False

        return self._element_instance_check(obj)

# Some predefined types for list and tuples
_str_list = _ListOf(str)
_int_list = _ListOf(int)
_float_list = _ListOf(float)
_int_float_list = _ListOf((int, float))
_tuple_list = _ListOf(tuple)
_int_float_tuple_list = _ListOf(_TupleOf((int, float)))

# DataTypes mapper to store various categories of DataTypes.
_GET_DATATYPES = {
    'NON_NUMERIC': [BLOB, BYTE, CHAR, CLOB, DATE, INTERVAL_DAY, INTERVAL_DAY_TO_HOUR, INTERVAL_DAY_TO_MINUTE,
                    INTERVAL_DAY_TO_SECOND, INTERVAL_HOUR, INTERVAL_HOUR_TO_MINUTE, INTERVAL_HOUR_TO_SECOND,
                    INTERVAL_MINUTE, INTERVAL_MINUTE_TO_SECOND, INTERVAL_MONTH, INTERVAL_SECOND, INTERVAL_YEAR,
                    INTERVAL_YEAR_TO_MONTH, PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP, TIME, TIMESTAMP, VARBYTE,
                    VARCHAR, GEOMETRY, MBB, MBR],
    'NON_NUM_DATE_INTERVAL': [BLOB, BYTE, CHAR, CLOB, PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP, TIME, TIMESTAMP,
                              VARBYTE, VARCHAR, GEOMETRY, MBB, MBR],
    'NON_NUM_INTERVAL': [BLOB, BYTE, CHAR, CLOB, DATE, PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP, TIME, TIMESTAMP,
                         VARBYTE, VARCHAR, GEOMETRY, MBB, MBR],
    'LOB_PERIOD': [BLOB, CLOB, PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP, GEOMETRY, MBB, MBR],
    'INTERVAL': [INTERVAL_YEAR, INTERVAL_YEAR_TO_MONTH, INTERVAL_MONTH, INTERVAL_DAY,
                 INTERVAL_DAY_TO_HOUR, INTERVAL_DAY_TO_MINUTE, INTERVAL_DAY_TO_SECOND,
                 INTERVAL_HOUR, INTERVAL_HOUR_TO_MINUTE, INTERVAL_HOUR_TO_SECOND,
                 INTERVAL_MINUTE, INTERVAL_MINUTE_TO_SECOND, INTERVAL_SECOND],
    'PERIOD': [PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP],
    'DATETIME': [DATE, TIME, TIMESTAMP],
    'LOB_PERIOD_BYTE_GEOM': [BLOB, CLOB, BYTE, VARBYTE, PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP, GEOMETRY, MBB, MBR]
}


class _DtypesMappers:
    AGGREGATE_UNSUPPORTED_TYPES = {
        'avg': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'mavg': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'bottom': _GET_DATATYPES["NON_NUMERIC"],
        'bottom with ties': _GET_DATATYPES["NON_NUMERIC"],
        'count': [],
        'first': _GET_DATATYPES["NON_NUMERIC"],
        'kurtosis': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'last': _GET_DATATYPES["NON_NUMERIC"],
        'mad': _GET_DATATYPES["NON_NUMERIC"],
        'max': _GET_DATATYPES["LOB_PERIOD"],
        'mean': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'median': _GET_DATATYPES["NON_NUMERIC"],
        'min': _GET_DATATYPES["LOB_PERIOD"],
        'mode': _GET_DATATYPES["NON_NUMERIC"],
        'percentile': _GET_DATATYPES["NON_NUMERIC"],
        'percentile_cont': _GET_DATATYPES["NON_NUMERIC"],
        'percentile_disc': _GET_DATATYPES["NON_NUMERIC"],
        'skew': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'sum': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'csum': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'msum': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'mdiff': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'mlinreg': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'std': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'stddev_pop': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'stddev_samp': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'top': _GET_DATATYPES["NON_NUMERIC"],
        'top with ties': _GET_DATATYPES["NON_NUMERIC"],
        'unique': [],
        'var': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'var_pop': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'var_samp': _GET_DATATYPES["NON_NUM_DATE_INTERVAL"],
        'corr': _GET_DATATYPES["NON_NUMERIC"],
        'regr_avgx': _GET_DATATYPES["NON_NUMERIC"],
        'regr_avgy': _GET_DATATYPES["NON_NUMERIC"],
        'regr_count': _GET_DATATYPES["NON_NUMERIC"],
        'regr_intercept': _GET_DATATYPES["NON_NUMERIC"],
        'regr_r2': _GET_DATATYPES["NON_NUMERIC"],
        'regr_slope': _GET_DATATYPES["NON_NUMERIC"],
        'regr_sxx': _GET_DATATYPES["NON_NUMERIC"],
        'regr_sxy': _GET_DATATYPES["NON_NUMERIC"],
        'regr_syy': _GET_DATATYPES["NON_NUMERIC"],
        'covar_pop': _GET_DATATYPES["NON_NUMERIC"],
        'covar_samp': _GET_DATATYPES["NON_NUMERIC"]
    }

    WINDOW_AGGREGATE_UNSUPPORTED_TYPES = {
        'count': [PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP],
        'max': [BYTE, VARBYTE, BLOB, CLOB, PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP,
                GEOMETRY, MBB, MBR],
        'min': [BYTE, VARBYTE, BLOB, CLOB, PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP,
                GEOMETRY, MBB, MBR],
        'lead': _GET_DATATYPES["LOB_PERIOD_BYTE_GEOM"],
        'lag': _GET_DATATYPES["LOB_PERIOD_BYTE_GEOM"],
        'first_value': _GET_DATATYPES["LOB_PERIOD_BYTE_GEOM"],
        'last_value': _GET_DATATYPES["LOB_PERIOD_BYTE_GEOM"]
    }

    DESCRIBE_AGGREGATE_UNSUPPORTED_TYPES = {
        'bottom': _GET_DATATYPES["NON_NUMERIC"],
        'bottom with ties': _GET_DATATYPES["NON_NUMERIC"],
        'count': [],
        'first': _GET_DATATYPES["NON_NUMERIC"],
        'last': _GET_DATATYPES["NON_NUMERIC"],
        'mad': _GET_DATATYPES["NON_NUMERIC"],
        'max': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'mean': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'avg': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'median': _GET_DATATYPES["NON_NUMERIC"],
        'min': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'mode': _GET_DATATYPES["NON_NUMERIC"],
        'percentile_cont': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'percentile': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'std': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'stddev_samp': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'sum': _GET_DATATYPES["NON_NUM_INTERVAL"],
        'top': _GET_DATATYPES["NON_NUMERIC"],
        'top with ties': _GET_DATATYPES["NON_NUMERIC"],
        'unique': [BYTEINT, SMALLINT, INTEGER, BIGINT, DECIMAL, FLOAT, NUMBER]
    }
    PY_TD_MAPPER = {int: INTEGER,
                    float: FLOAT,
                    str: VARCHAR(1024),
                    bool: BYTEINT,
                    datetime: TIMESTAMP,
                    date: DATE,
                    time: TIME
                    }

    # Mapper which stores the mapping between TD type specified in in analytic JSON files to Python type.
    JSON_TD_TO_PYTHON_TYPE_MAPPER = {"BOOLEAN": bool,
                                     "STRING": str,
                                     "INTEGER": int,
                                     "NUMERIC": (int, float),
                                     "DOUBLE PRECISION": float,
                                     "double precision": float,
                                     "DOUBLE": float,
                                     "FLOAT": float,
                                     "LONG": int,
                                     "ARGLIST": list,
                                     "COLUMNS": str,
                                     "COLUMN": str,
                                     "<TD_FORMULA>": str,
                                     "COLUMN_NAMES": str,
                                     "TIMESTAMPWZ": str,
                                     "TIME-DURATION": str
                                     }

    DATETIME_PERIOD_TYPES = _GET_DATATYPES["PERIOD"] + _GET_DATATYPES["DATETIME"]
    INTERVAL_TYPES = _GET_DATATYPES["INTERVAL"]

    TDSQLALCHEMY_DATATYPE_TO_VAL_STRING_MAPPER = {
        BIGINT: lambda x: x.__class__.__name__,
        BYTEINT: lambda x: x.__class__.__name__,
        CHAR: lambda x: "{0},{1}".format(x.__class__.__name__, x.length),
        DATE: lambda x: x.__class__.__name__,
        DECIMAL: lambda x: "{0},{1},{2}".format(x.__class__.__name__, x.precision, x.scale),
        FLOAT: lambda x: x.__class__.__name__,
        NUMBER: lambda x: ','.join(map(str, (filter(None, [x.__class__.__name__, x.precision, x.scale])))),
        INTEGER: lambda x: x.__class__.__name__,
        SMALLINT: lambda x: x.__class__.__name__,
        TIME: lambda x: "{0},{1}".format(x.__class__.__name__, x.precision),
        TIMESTAMP: lambda x: "{0},{1}".format(x.__class__.__name__, x.precision),
        VARCHAR: lambda x: "{0},{1}".format(x.__class__.__name__, x.length)
    }

class _SuppArgTypes:
    VAL_ARG_DATATYPE = (str, BIGINT, BYTEINT, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMBER, SMALLINT, TIME,
                        TIMESTAMP, VARCHAR)

class _Dtypes:

    @staticmethod
    def _get_numeric_datatypes():
        """
        Returns the numeric data types used in Teradata Vantage
        **From : https://www.info.teradata.com/HTMLPubs/DB_TTU_16_00/
        index.html#page/General_Reference/B035-1091-160K/psa1472241434371.html

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of numeric data types used in Teradata Vantage
        """
        return [BYTEINT, SMALLINT, INTEGER, BIGINT, DECIMAL, FLOAT, NUMBER]

    @staticmethod
    def _get_timedate_datatypes():
        """
        Returns a list of TimeDate data types.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of TimeDate data types used in Teradata Vantage
        """
        return [TIMESTAMP, DATE, TIME]

    @staticmethod
    def _get_character_datatypes():
        """
        Returns a list of Character data types.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of Character data types used in Teradata Vantage
        """
        return [CHAR, VARCHAR, CLOB]

    @staticmethod
    def _get_byte_datatypes():
        """
        Returns a list of byte like data types.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of Byte data types used in Teradata Vantage
        """
        return [BYTE, VARBYTE, BLOB]

    @staticmethod
    def _get_categorical_datatypes():
        """
        Returns a list of containing Character and TimeDate data types.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of Character and TimeDate data types used in Teradata Vantage
        """
        return list.__add__(_Dtypes._get_character_datatypes(), _Dtypes._get_timedate_datatypes())

    @staticmethod
    def _get_all_datatypes():
        """
        Returns a list of Character, Numeric and TimeDate data types.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of Character, Numeric and TimeDate data types used in Teradata Vantage
        """
        return list.__add__(_Dtypes._get_categorical_datatypes(), _Dtypes._get_numeric_datatypes())

    @staticmethod
    def _get_unsupported_data_types_for_aggregate_operations(operation,
                                                             as_time_series_aggregate=False,
                                                             is_window_aggregate=False):
        """
        Returns the data types on which aggregate operations cannot
        be performed eg : min, max, avg

        PARAMETERS:
            operation:
                Required Argument.
                Specifies an aggregate operation to be performed on the dataframe.
                Types: str

            as_time_series_aggregate:
                Optional Argument.
                Specifies whether aggregate operation is a Time Series aggregate or not.
                Default Values: False
                Types: bool

            is_window_aggregate:
                Optional Argument.
                Specifies whether aggregate operation is a Window aggregate or not.
                Default Values: False
                Types: bool

        RAISES:
            None

        RETURNS:
            List of unsupported data types for aggregate operation in
            Teradata Vantage eg : min, max, avg
        """
        if operation == 'median' and not as_time_series_aggregate:
            # For median as regular aggregate unsupported types are different than the ones
            # mentioned in _DtypesMappers.AGGREGATE_UNSUPPORTED_TYPES
            return [BLOB, BYTE, CHAR, CLOB, DATE, PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP, TIME, TIMESTAMP, VARCHAR]

        # Return the unsupported types list, if key with 'operation' is found.
        # If 'operation' is not found, return empty list which means all types
        # are supported.
        if is_window_aggregate:
            # If operation is not present in WINDOW_AGGREGATE_UNSUPPORTED_TYPES
            # then return the value from the AGGREGATE_UNSUPPORTED_TYPES mapper.
            return _DtypesMappers.WINDOW_AGGREGATE_UNSUPPORTED_TYPES.get(operation,
                    _DtypesMappers.AGGREGATE_UNSUPPORTED_TYPES.get(operation, []))
        return _DtypesMappers.AGGREGATE_UNSUPPORTED_TYPES.get(operation, [])

    @staticmethod
    def _get_unsupported_data_types_for_describe_operations(operation):
        """
        Returns the data types on which the specified describe aggregate 'operation' cannot
        be performed. This function is used by the method DataFrame.describe().

        PARAMETERS:
            operation : String. An aggregate operation to be performed on the dataframe.
                        possible values are 'sum', 'min', 'max', 'mean','std', 'percentile',
                        'count', and 'unique'.

        RAISES:
            None

        RETURNS:
            List of unsupported data types for describe operation in
            Teradata Vantage eg : min, max, avg
        """
        try:
            # Return the unsupported types list, if key with operation 'operation' is found.
            return _DtypesMappers.DESCRIBE_AGGREGATE_UNSUPPORTED_TYPES[operation]
        except KeyError:
            # We are here means, there are not unsupported types mentioned in
            # _DtypesMappers.DESCRIBE_AGGREGATE_UNSUPPORTED_TYPES, so that means all types are supported.
            return []

    @staticmethod
    def _get_sort_unsupported_data_types():
        """
        Returns the data types on which sorting is invalid.

        RAISES:
            None

        RETURNS:
            list of teradatasqlalchemy.types

        EXAMPLES:
            _Dtypes._get_sort_unsupported_data_types()
        """
        return [CLOB, BLOB]

    @staticmethod
    def _teradata_type_to_python_type(td_type):
        """
        Translate the Teradata type from metaexpr to Python types.
        PARAMETERS:
            td_type - The Teradata type from metaexpr.

        RETURNS:
            The Python type for the given td_type.

        RAISES:

        EXAMPLES:
            # o is an instance of INTEGER
            pytype = _Dtypes._teradata_type_to_python_type(o)

        """

        # loggerlogger.debug("_help_col_to_python_type td_type = {0} ".format(td_type))
        if type(td_type) in TeradataTypes.TD_INTEGER_TYPES.value:
            return PythonTypes.PY_INT_TYPE.value
        elif type(td_type) in TeradataTypes.TD_FLOAT_TYPES.value:
            return PythonTypes.PY_FLOAT_TYPE.value
        elif type(td_type) in TeradataTypes.TD_DECIMAL_TYPES.value:
            return PythonTypes.PY_DECIMAL_TYPE.value
        elif type(td_type) in TeradataTypes.TD_BYTE_TYPES.value:
            return PythonTypes.PY_BYTES_TYPE.value
        elif type(td_type) in TeradataTypes.TD_DATETIME_TYPES.value:
            return PythonTypes.PY_DATETIME_TYPE.value
        elif type(td_type) in TeradataTypes.TD_TIME_TYPES.value:
            return PythonTypes.PY_TIME_TYPE.value
        elif type(td_type) in TeradataTypes.TD_DATE_TYPES.value:
            return PythonTypes.PY_DATE_TYPE.value

        return PythonTypes.PY_STRING_TYPE.value

    @staticmethod
    def _python_type_to_teradata_type(py_type):
        """
        DESCRIPTION:
            Translate the Python types to Teradata type.

        PARAMETERS:
            py_type:
               Required Argument.
               Specifies the Python type.
               Types: type

        RETURNS:
            The teradatasqlalchemy type for the given py_type.

        RAISES:
            None

        EXAMPLES:
            tdtype = _Dtypes._python_type_to_teradata_type(int)

        """

        return _DtypesMappers.PY_TD_MAPPER.get(py_type)

    @staticmethod
    def _help_col_to_python_type(col_type, storage_format):
        """
        Translate the 1 or 2 character TD type codes from HELP COLUMN to Python types.
        PARAMETERS:
            col_type - The 1 or 2 character type code from HELP COLUMN command.
            storage_format - The storage format from HELP COLUMN command.

        RETURNS:
            The Python type for the given col_type.

        RAISES:

        EXAMPLES:
            pytype = _Dtypes._help_col_to_python_type('CV', None)
            pytype = _Dtypes._help_col_to_python_type('DT', 'CSV')

        """
        if col_type in TeradataTypes.TD_INTEGER_CODES.value:
            return PythonTypes.PY_INT_TYPE.value
        elif col_type in TeradataTypes.TD_FLOAT_CODES.value:
            return PythonTypes.PY_FLOAT_TYPE.value
        elif col_type in TeradataTypes.TD_DECIMAL_CODES.value:
            return PythonTypes.PY_DECIMAL_TYPE.value
        elif col_type in TeradataTypes.TD_BYTE_CODES.value:
            return PythonTypes.PY_BYTES_TYPE.value
        elif col_type in TeradataTypes.TD_DATETIME_CODES.value:
            return PythonTypes.PY_DATETIME_TYPE.value
        elif col_type in TeradataTypes.TD_TIME_CODES.value:
            return PythonTypes.PY_TIME_TYPE.value
        elif col_type in TeradataTypes.TD_DATE_CODES.value:
            return PythonTypes.PY_DATE_TYPE.value
        elif col_type == "DT":
            sfmt = storage_format.strip()
            if sfmt == "CSV":
                return PythonTypes.PY_STRING_TYPE.value
            elif sfmt == "AVRO":
                return PythonTypes.PY_BYTES_TYPE.value

        return PythonTypes.PY_STRING_TYPE.value

    @staticmethod
    def _help_col_to_td_type(col_type, udt_name, storage_format):
        """
        Translate the 2 character TD type codes from HELP COLUMN to Teradata types.
        PARAMETERS:
            col_type - The 2 character type code from HELP COLUMN command.
            udt_name - The UDT name from the HELP COLUMN command.
            storage_format - The storage format from HELP COLUMN command.

        RETURNS:
            The Teradata type for the given colType.

        RAISES:

        EXAMPLES:
            tdtype = _Dtypes._help_col_to_td_type('CV', None, None)

        """
        # logger.debug("helpColumnToTeradataTypeName colType = {0} udtName = {1} storageFormat {2}".format(colType, udtName, storageFormat))
        if col_type in HELP_COL_TYPE_TO_TDTYPE:
            return HELP_COL_TYPE_TO_TDTYPE[col_type]

        if col_type == "DT":
            return "DATASET STORAGE FORMAT {0}".format(storage_format.strip())

        if col_type in ["UD", "US", "UT", "A1", "AN"]:
            if udt_name:
                return udt_name

        return col_type

    @staticmethod
    def _anly_json_type_to_python_type(json_td_type):
        """
        DESCRIPTION:
            Get the Python type equivalent to the specified type in analytic
            JSON files.

        PARAMETERS:
            json_td_type:
               Required Argument.
               Specifies the TD type specified in analytic function json file.
               Types: type

        RETURNS:
            type

        EXAMPLES:
            tdtype = _Dtypes._anly_json_type_to_python_type("NUMBER")

        """
        from teradataml.dataframe.dataframe import TDSeries, TDMatrix, TDGenSeries, TDAnalyticResult
        _DtypesMappers.JSON_TD_TO_PYTHON_TYPE_MAPPER.update({"SERIES": TDSeries,
                        "MATRIX": TDMatrix,
                        "ART": TDAnalyticResult,
                        "GENSERIES": TDGenSeries})


        return _DtypesMappers.JSON_TD_TO_PYTHON_TYPE_MAPPER.get(json_td_type.upper())


    @staticmethod
    def _get_interval_data_types():
        """
        Returns the INTERVAL data types.

        RAISES:
            None

        RETURNS:
            list of teradatasqlalchemy.types

        EXAMPLES:
            _Dtypes._get_interval_data_types()
        """
        return _DtypesMappers.INTERVAL_TYPES

    @staticmethod
    def _get_datetime_period_data_types():
        """
        Returns the PERIOD and DATETIME data types.

        RAISES:
            None

        RETURNS:
            list of teradatasqlalchemy.types

        EXAMPLES:
            _Dtypes._get_datetime_period_data_types()
        """
        return _DtypesMappers.DATETIME_PERIOD_TYPES

