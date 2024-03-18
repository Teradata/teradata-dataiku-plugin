# -*- coding: utf-8 -*-
"""This file take the input JSON file and outputs the SQL string query."""

'''
Copyright © 2019 by Teradata.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

# SKS : Import 
from base_analytic_query_generator import BaseAnalyticQueryGenerator
from gen_uaf_sql import gen_uaf_query
from verifyTableColumns import *


def strip_quotes(input_string):
    lst =  input_string.split(",")
    for index in range(len(lst)):
        lst[index] = lst[index].strip().strip('"').strip("'")
    output_string = ",".join(lst)
    return output_string

class OpenEndedQueryGenerator():
    '''
    The OpenEndedQueryGenerator is an independent class that takes the input JSON and parses it, 
    it then calls the BaseAnalyticQueryGenerator which generates the outputted SQL.
    '''
    def __init__(self, output_table_name, config_json, verbose=False, outputDatabaseName=""):
        '''
        Constructor for the query generation based on inputted JSON.

        @param output_table_name: A variable for the 
            output table name, used for formatting when query is created.
        @type output_table_name: String.

        @param config_json: A variable that represents the configurated JSON (described in a schema document)
            Examples of a configurated JSON included in static/data. These JSONs have each of the attributes and parameters
            that the analytic function has. 
        @type config_json: JSON dictionary.
        '''
        self._output_table_name = output_table_name
        self._config_json = config_json
        self._verbose = verbose
        self._output_database_name = outputDatabaseName;


    def create_query(self):
        '''
        Method to create the query based on the different arguments from the JSON files. The BaseAnalyticQueryGenerator requires
        multiple arguments, this function gathers all those arguments accordingly and then inputs it into BaseAnalyticQueryGenerator
        in order to get back the output SQL query string.
        '''
        dss_function = self._config_json.get('function', None)
        if dss_function and 'function_type' in dss_function and dss_function['function_type'] == "uaf":
            query, error = gen_uaf_query(self._output_table_name, self._config_json, self._output_database_name)
            return query

        # SKS : Query arguments
        func_alias_name = self._config_json["function"]["function_alias_name"]
        function_name = func_alias_name
        func_input_table_view_query = [] 
        func_input_partition_by_cols= []
        func_input_order_by_cols= []
        func_input_arg_sql_names= []
        func_other_arg_json_datatypes= []
        func_other_arg_sql_names= []
        func_input_dataframe_type= []
        func_input_distribution= []
        func_input_local_order = []
        func_type= 'FFE'
        engine= 'ENGINE_SQL'

        func_other_args_values= []
        # SHOULD THIS BE THE DATA TYPE PER ATTRIBUTE ADDED????
        func_output_args_sql_names= []
        func_output_args_values= []

        required_inputs = self._config_json["function"]["required_input"]

        npath_non_quoted_args = ["SYMBOLS", "RESULT", "MODE", "FILTER"]

        input_num = 1
        for req_input in required_inputs:
            if 'value' not in req_input or req_input["value"] == "":
                continue

            # SKS : Need this otherwise it won't show up, but of course the "AS" name needs to be unique
            if "name" in req_input:
                # Added for support of 17.10 functions
                input_name = "\"" + req_input["name"] + "\""
            else:
                input_name = "\"" + "input" + str(input_num) + "\""

            if ('alternateNames' in req_input) and (req_input["alternateNames"] != []):
                input_name = str(req_input["alternateNames"]).strip('[]').replace("'", '"')
            func_input_arg_sql_names.append(input_name)
            input_num += 1

            input_table_name = req_input["value"]
            input_table_schema = ""
            if ("inputtables" in self._config_json["function"]) and (input_table_name in self._config_json["function"]["inputtables"]):
                # Use the full table name
                input_table_name = self._config_json["function"]["inputtables"][input_table_name]
            if ("inputschemas" in self._config_json["function"]) and (input_table_name in self._config_json["function"]["inputschemas"]):
                # Use the full table name
                input_table_schema = self._config_json["function"]["inputschemas"][input_table_name]
            
            input_table_name = verifyQualifiedTableName(input_table_schema, input_table_name)
            func_input_table_view_query.append(input_table_name)

            # SKS : loop through the partition attributes and append according to the type of partition
            partition_by = []
            for i in range(len(req_input["partitionAttributes"])):
                if req_input['kind'] == 'PartitionByKey' or req_input['kind'] == 'HashByKey':
                    partition_by.append(req_input["partitionAttributes"][i])
                elif req_input['kind'] == 'PartitionByAny':
                    partition_by.append("ANY")
                elif req_input['kind'] == 'PartitionByOne':
                    partition_by.append("1")
            if len(partition_by)>0:
                func_input_partition_by_cols.append(", ".join(partition_by))
            else:
                func_input_partition_by_cols.append(None)
            
            # SKS : loop through the ordering attributes and if there is a direction for the ordering then add to the end of the string
            order_by = []
            for i in range(len(req_input["orderByColumn"])):
                order_info = req_input["orderByColumn"][i]
                if order_info == "" or order_info == None:
                    continue
                # SKS: Only add valid order by cases
                if ("orderByColumnDirection" in req_input) and (req_input["orderByColumnDirection"][i] != ""):
                    order_info += " " + req_input["orderByColumnDirection"][i]
                order_by.append(order_info)

            # Dimension or None should never have order/local order by
            #if req_input['kind'].lower() == 'dimension' or req_input['kind'].lower() == 'none':
            if req_input['kind'].lower() == 'none':
                order_by = []

            if len(order_by)>0:
                if req_input['kind'] == 'HashByKey':
                    func_input_local_order.append(True)
                else:
                    func_input_local_order.append(False)

                func_input_order_by_cols.append(", ".join(order_by))
            else:
                func_input_local_order.append(False)
                func_input_order_by_cols.append(None)

            # Currently Always a TABLE
            func_input_dataframe_type.append('TABLE')

                
            # 'inputKindChoices': ['Dimension'],
            if req_input['kind'].lower() == 'dimension':
                func_input_distribution.append('DIMENSION')
            elif req_input['kind'].lower() == 'none':
                func_input_distribution.append('NONE')
            elif req_input['kind'].lower() == 'hashbykey':
                func_input_distribution.append('HASH')
            else:
                func_input_distribution.append('FACT')
            
        # SKS: loop through the arguments in the config json
        arguments = self._config_json["function"]["arguments"]
        for arg in arguments:
            # SKS : if the value attribute is not included in arg, we do not need to do anything
            if 'value' not in arg:
                continue
            # SKS : if the defaultValue exists and is equivalent to the value attribute then we don't want that to be explicilty included in the sql creation 
            # UNLESS it is a mandatory for boolean
            if (arg['value'] == '') and (arg['datatype'] == 'BOOLEAN') and ('isRequired' in arg) and arg['isRequired']:
                if ('defaultValue' in arg) and arg['defaultValue']:
                    arg['value'] = 'True'
                else:
                    arg['value'] = 'False'
            else:
                if ('defaultValue' in arg) and (arg['value'] == arg['defaultValue']) and arg.get('useDefaultInQuery', True):
                    continue
                # SKS : for columns, ignore columns that are empty
                if ('defaultValue' in arg) and (arg['datatype'] == 'COLUMNS') and arg['defaultValue'] == '' and (arg['value'] == [""] or arg['value'] == []):
                    continue
                # SKS : if the value is None then ignore
                if arg['value'] == None:
                    continue
                # SKS Boolean check - deal with when default value is not a string but value is a string
                if ('defaultValue' in arg) and arg['datatype'] == 'BOOLEAN' and arg['defaultValue']==False and type(arg['value']) == str and arg['value'].lower()=='false':
                    continue
                if ('defaultValue' in arg) and arg['datatype'] == 'BOOLEAN' and arg['defaultValue']==True and type(arg['value']) == str and arg['value'].lower()=='true':
                    continue

            # SKS : if the value is something other than empty string we want to accordingly update some of the arguments 
            if arg['value'] != '':
                func_other_arg_sql_names.append(arg['name'].upper())
                func_other_arg_json_datatypes.append(arg['datatype'])

                # SKS : we need to account for the different types of arguments and in order for the arguments to appear the same 
                # as the original sql query, we need to accordingly change to fit this criteria 
                if arg['datatype'] == 'INTEGER' and ((type(arg['value']) == str or type(arg['value']) == list) and ('\x00' in arg['value']) or arg.get("allowsLists", False)):
                    numbers = ",".join(arg['value'].split('\x00'))
                    func_other_args_values.append(numbers)
                    continue
                elif arg['datatype'] == 'INTEGER' :
                    number = int(arg['value'])
                    func_other_args_values.append(number)
                    continue
                elif arg['datatype'] == 'STRING' and ('\x00' in arg['value']):
                    # HACK for Npath: two cases - if it is an npath argument without quotes then call strip_quotes function
                    string_value = str(arg['value'].split('\x00')).strip('[]')
                    if arg['name'].upper() in npath_non_quoted_args:
                        func_other_args_values.append(strip_quotes(string_value))
                    else:
                        func_other_args_values.append(string_value)
                elif type(arg['value']) == int or type(arg['value']) == float:
                    func_other_args_values.append(arg['value'])
                elif type(arg['value']) == list:
                    func_other_args_values.append(str(arg['value']).strip("[]").replace(" ", ""))
                elif arg['datatype'] == 'DOUBLE PRECISION' and type(arg['value']) == str:
                    # SKS: Fix issues when JSON have bug that it is double precision by value is a string!
                    func_other_args_values.append(float(arg['value']))
                # Account for arguments that don't need quotations 
                elif arg['name'].upper() in npath_non_quoted_args:
                    func_other_args_values.append(str(arg['value']))
                else:
                    func_other_args_values.append('\'' + str(arg['value']) + '\'')
            
        # Check if output tables exists in InDB Json    
        if "output_tables" in self._config_json["function"]:
            output_tables = self._config_json["function"]["output_tables"]
            # For each output
            for output_index in range(len(output_tables)):
                # get output name
                output_name = output_tables[output_index]["name"]
                # now check if recipe has actually connected an extra output
                recipe_outputs = self._config_json["function"].get("output_table_names", [])
                # assume output_index+1 is needed as the zero'th output is the main output and not an extra output
                # i.e. the first optional output is at 1
                if output_index+1 < len(recipe_outputs):
                    output_full_table_name = recipe_outputs[output_index+1]["table"]
                    # now add to arguments for base query generator
                    func_output_args_sql_names.append(output_name)
                    func_output_args_values.append(output_full_table_name)

       
        # SKS: Accounts for the SQL Clauses section where the user may Modify Select Columns of Output Query 
        select_clause = ""
        if 'customSelectClause' in self._config_json["function"] and self._config_json["function"]['customSelectClause'] == True:
            select_clause = self._config_json["function"]['select_clause']

        # SKS call base query generator
        query_string_gen_unpack = BaseAnalyticQueryGenerator(func_alias_name, function_name, func_input_arg_sql_names, func_input_table_view_query, func_input_dataframe_type,
                             func_input_distribution, func_input_partition_by_cols, func_input_order_by_cols,
                             func_other_arg_sql_names, func_other_args_values, func_other_arg_json_datatypes,
                             func_output_args_sql_names, func_output_args_values, func_input_local_order, func_type,
                             engine, self._verbose)
        base_query = query_string_gen_unpack._gen_sqlmr_select_stmt_sql()

       
        CREATE_QUERY = '''CREATE TABLE {}
        AS 
        (
        {}
        )
        WITH DATA
        ;'''
        # CREATE_QUERY = '''{}'''
        result = CREATE_QUERY.format(verifyQualifiedTableName(self._output_database_name, self._output_table_name), verifyQueryExpr(base_query.replace("sqlmr", "tmp_alias")))
        return result

