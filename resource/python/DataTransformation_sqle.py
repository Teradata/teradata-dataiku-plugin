# -*- coding: utf-8 -*-

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

import dataiku
# from dataiku import os
import json
import logging
import pprint
import os

from dataiku.customrecipe import get_recipe_resource
# SKS: Import vantage version number
import sys
sys.path.append('../../python-lib')
import vantage_version
import auth
# SKS Open Query Generator
from open_ended_query_generator import OpenEndedQueryGenerator
from query_engine_wrapper import QueryEngineWrapper

# Valib functions
from valib_executor import *

# SKD import pandas for set max column width
import pandas as pd


FUNCTION_CATEGORY="Data Transformation"
PARTNER_LIST=["EvaluateNamedEntityFinderRow","LinRegMatrix"]

def get_val_default_database(inputdataset):
    if inputdataset == None:
        return '', ''
    
    connections = {}
    connectionName = inputdataset.get_location_info()['info']['connectionName']
    connections = auth.addConnection(connections, connectionName)
    defaultDatabase = ''
    if connectionName in connections and 'defaultDatabase' in connections[connectionName]['params']:
        defaultDatabase = connections[connectionName]['params']['defaultDatabase']
    valDatabase = ''
    if connectionName in connections and "dkuProperties" in connections[connectionName]['params']:
        dkuProperties = connections[connectionName]['params']['dkuProperties']
        for item in dkuProperties:
            if item['name'] == "VAL_DATABASE":
                valDatabase = item['value']
                break
    return valDatabase, defaultDatabase



# Subclass of query engine wrapper implemented with a Dataiku SQLExecutor2
# An instance of this class will be created when we use the functions in analytic_function_utility and vantage_version
class DataikuQueryEngineWrapper(QueryEngineWrapper):
    def __init__(self, executor):
        self.executor = executor

    def execute(self, query_string):
        return self.executor.query_to_df(query_string)

    def iteratable(self, result):
        return result.iterrows()

    def row_value(self, row, column_name):
        return row[1][column_name]

def load_json(json_dict, inputs):
    try:

        f = json_dict
        d = {
            "name":"",
            "function_alias_name":"",
            "output_tables":"",
            "arguments":"",
            "asterarguments":"",
            "partitionInputKind":[],
            "partitionAttributes":"",
            "isOrdered":False,
            "orderByColumn":"",
            "hasInputTable":False,
            "isQueryMode": False,
            "queries": [],
            "hasNativeJSON": True,
            "function_type" : ""
        }
        
        keys = f.keys()

        # SKS Return the original JSON contents in the dictionary
        d["json_contents"] = json.dumps(f)

        # function type used for valib extension
        d["function_type"] = f.get("function_type", "")

        
        # Get the function name and alias name, and use the function name as the alias name if the latter does not exist.
        d["name"] = f.get("function_name", "")
        d["function_alias_name"] = f.get("function_alias_name", f.get("function_name", ""))
        
        unaliased_inputs = {'desc':{}, 'values':[], 'count':0}
        required_inputs = []
        # Run through all the input tables of the function.
        if "input_tables" in keys:
            d["hasInputTable"] = True
            input_table_list = f["input_tables"]
            num_input_tables = 0
            for table in input_table_list:
                required_input_dict = {"isRequired": True, "partitionAttributes":"", "orderByColumn": ""}
                required_input_dict['isRequired'] = table.get('isRequired', True) # Assume required unless specified False.
                required_input_dict['isOrdered'] = table.get('isOrdered', False) # Assume unordered unless specified True.
                required_input_dict['alternateNames'] = table.get('alternateNames', []) # Assume no alternate names unless specified.
                
                requiredInputKind = table.get("requiredInputKind", [])
                if (type(requiredInputKind) == list and len(requiredInputKind) == 1 and requiredInputKind[0] == "PartitionByKey") or requiredInputKind == []:
                    requiredInputKind = ["PartitionByKey", "HashByKey", "None"]

                #requiredInputKind = table.get("requiredInputKind", ["PartitionByAny"]) # All element of the requiredInputKind list.
                partitionByKey = requiredInputKind[0] if requiredInputKind else "" # partitionByKey is the first element of the requiredInputKind list.
                if 'partitionByOne' in table.keys() and table['partitionByOne']:
                    if 'partitionByOneInclusive' in table.keys() and table['partitionByOneInclusive']:  # Checks if partitionByOneInclusive is a key.
                        requiredInputKind.append("PartitionByOne") # If it is a key, we append PartitionByOne to the inputKindChoices.
                    else:
                        partitionByKey = "PartitionByOne" # If partitionByOneInclusive is not a key, we override the partitionByKey to be partitionByOne.
                required_input_dict['kind'] = partitionByKey
                required_input_dict['inputKindChoices'] = requiredInputKind

                if "uaf" in table:
                    required_input_dict["uaf"] = table["uaf"]
                if "uafType" in table:
                    required_input_dict["uafType"] = table["uafType"]
                
                # Check if the table is named (= required input) or not (unaliased input).
                if 'name' in table.keys() or ('Dimension' in table.get('requiredInputKind',[]) and 0 < unaliased_inputs.get('count',0)):
                    required_input_dict['name'] = table.get('name', 'Dimension')
                    required_input_dict['value'] = ""
                    # Set the Table Value if single Input case for first Table Property
                    if len(inputs) == 1 and num_input_tables == 0:
                        required_input_dict['value'] = inputs[0]['fullName'].split('.')[1]
                    required_inputs.append(required_input_dict)
                else:
                    unaliased_inputs['count'] += 1
                    d["isOrdered"] = table.get("isOrdered", False)
                    if 'partitionByOne' in table.keys() and table['partitionByOne']:
                        d['partitionInputKind'] = ['PartitionByOne']
                    else:
                        d['partitionInputKind'] = table.get("requiredInputKind", [])





                num_input_tables += 1
                        
        d["required_input"] = required_inputs
        d["unaliased_inputs"] = unaliased_inputs
        
        # Run through all output tables.
        if 'output_tables' in keys:
            ot = []
            out_table_list = f["output_tables"]
            for table in out_table_list:
                outtbl = {"name":"","isRequired":"","value":"", "datatype": "", "allowsLists":True}
                if table.get('alternateNames', []):
                    outtbl["name"] = table.get('alternateNames', [''])[0]
                outtbl["name"] = table.get("name", "")
                outtbl["isRequired"] = table.get("isRequired", False)
                outtbl["datatype"] = table.get("datatype", "")

                # SKS: Add upper and lower bounds
                outtbl["lowerBound"] = table.get("lowerBound", "")
                outtbl["upperBound"] = table.get("upperBound", "")

                # fixes future problem where the type in JSON is both numeric and string
                #if outtbl["datatype"].contains("STRING") and outtbl["datatype"] != "STRING":
                #    outtbl["datatype"] = "STRING"

                outtbl["allowsLists"] = table.get("allowsLists", True)
                outtbl["targetTable"] = table.get("targetTable", [])
                outtbl["isOutputTable"] = table.get("isOutputTable", False)
                outtbl["permittedValues"] = table.get("permittedValues", [])
                if 'defaultValue' in table:
                    outtbl["value"] = defaultValuesFromArg(table)
                    # SKS: 
                    outtbl["defaultValue"] = outtbl["value"]
                ot.append(outtbl)
            d["output_tables"] = ot
        
        # Similar to output tables.
        if 'argument_clauses' in keys:
            args = []
            arg_lst = f['argument_clauses']
            for argument in arg_lst:
                arg = {"name":"","isRequired":"","value":"", "datatype": "", "allowsLists":True}
                if argument.get('alternateNames', []):
                    arg["name"] = argument.get('alternateNames', [''])[0]
                arg["name"] = argument.get("name", "")
                arg["isRequired"] = argument.get("isRequired", False)
                arg["datatype"] = argument.get("datatype", "")
                #if arg["datatype"] == "GROUPEND":
                #    continue
                if type(arg["datatype"]) != str:
                    arg["datatype"] = "STRING"
                arg["datatype"] = arg["datatype"].upper()
                if arg["datatype"] == "NUMERIC":
                    arg["datatype"] = "DOUBLE PRECISION"
                if arg["datatype"] == "COLUMN":
                    arg["datatype"] = "COLUMNS"

                if "useDefaultInQuery" in argument:
                    arg["useDefaultInQuery"] = argument["useDefaultInQuery"]

                # SKS: Add upper and lower bounds
                arg["lowerBound"] = str(argument.get("lowerBound", ""))
                arg["upperBound"] = str(argument.get("upperBound", ""))

                # SKS: fixes future problem where the type in JSON is both numeric and string
                #if arg["datatype"].contains("STRING") and arg["datatype"] != "STRING":
                #    arg["datatype"] = "STRING"


                arg["allowsLists"] = argument.get("allowsLists", True)
                arg["targetTable"] = argument.get("targetTable", [])
                arg["isOutputTable"] = argument.get("isOutputTable", False)
                arg["permittedValues"] = argument.get("permittedValues", [])
                if 'defaultValue' in argument:
                    arg["value"] = defaultValuesFromArg(argument)
                    # SKS: Added Default Value for frontend to use as well
                    arg["defaultValue"] = arg["value"]

                if "Type" in argument:
                    arg["Type"] = argument["Type"]

                # arg["inNative"] = True # Setting to True because all files should be native and not MLE.
                args.append(arg)
                
            d['arguments'] = args
            # f_native = json.loads(open('%s/data/%s' % (os.getenv("DKU_CUSTOM_RESOURCE_FOLDER"), f.get("native"))).read())
            f_native = f
            keys_native = f_native.keys()
            if 'argument_clauses' in keys_native:
                a_n = []
                arg_lst_native = f_native['argument_clauses']
                for argument_native in arg_lst_native:
                    arg_n = {}
                    arg_n["alternateNames"] = argument_native.get("alternateNames", [""])[0] if argument_native.get("alternateNames", []) else ""
                    arg_n["name"] = argument_native.get("name", "")
                    a_n.append(arg_n)                                                           
                args = inNativeCheck(args, a_n)
        return d
        
    except ValueError:
        logging.info("%s is not a valid json file." % file_name)
   

def getConnectionParamsFromDataset(inputDataset):
    return inputDataset.get_location_info(sensitive_info=True)['info']

def do(payload, config, plugin_config, inputs):
    """
    Returns a dictionary of possible functions based on the configuration. 
    
    :param payload: Unused.
    :param config: Contains the category to filter functions from.
    :param plugin_config: Unused.
    :param inputs: Input Datasets. Used to find the schemas to be used.
    """
    
    # SKS : in order to show the query results in the UI front-end button
    if "query" in payload:

        # Valib
        try:
            dss_function = config.get('function', None)
            if dss_function and 'function_type' in dss_function and dss_function['function_type'] == "valib":
                json_contents = json.loads(dss_function["json_contents"])
                result = valib_execution(json_contents, dss_function, valib_query_wrapper=None)
                return {'result' : result}

            # create a open_ended_query_generator pass in "output" for the output_table_name argument and 'config' as the config_json
            sql_generator = OpenEndedQueryGenerator('output', config)
            result = sql_generator.create_query()
        except:
            result = "No query present to report."
        return {'result' : result}

    #SKS: Test code to check if I can run a query against the capability table
    # The input_table_name and input_dataset is from the code from below
    sql_query_worked = False

    # SKS initiate Dataset/SQLExecuter2
    input_table_name = inputs[0]['fullName'].split('.')[1]
    input_dataset =  dataiku.Dataset(input_table_name)
    # Create the Dataiku SQL Executor
    executor = dataiku.core.sql.SQLExecutor2(dataset=input_dataset) 


    # SKS: Get vantage version number
    use_version_jsons = True
    vantage_version_number = vantage_version.get_vantage_version(  DataikuQueryEngineWrapper(executor)  )
    

    if "explain" in payload:
        try:
            sql_generator = OpenEndedQueryGenerator('output', config)
            my_query = sql_generator.create_query()
            my_query_explanation = executor.query_to_df('EXPLAIN ' + my_query)
            pd.set_option("display.max_colwidth", 150)
            explain_string = my_query_explanation.to_string(index= False, justify='left')
            return {'result' : explain_string}
        except:
            return {'result' : "Error"}

    # Recipe inputs
    #env = os.getenv("DKU_CUSTOM_RESOURCE_FOLDER")
    env = get_recipe_resource()
    
    # The purpose of this will be given a filepath load in the JSON as json_dict 
    if "load_json" in payload:
        try:
            json_file_path = payload["load_json"]
            json_file_path = os.path.join(env, 'data', json_file_path)
            with open(json_file_path) as f:
                result = load_json(json.load(f), inputs)
                return {'result' : result}
        except:
            return {'result' : "Error"}


    # SKS Should there be other plugin names?
    plugin_name = "Advanced SQL Engine Functions"
    if env.find("MLE") != -1:
        plugin_name = "Advanced MLE Engine Functions"


    #category_names = config["category"].split(";")
    category_names = []
    if "SQLE" not in category_names:
        category_names += ["SQLE"]
    if "VALIB" not in category_names:
        category_names += ["VALIB"]
    
    choices = []
    plugin_version_number = vantage_version_number
    for category in category_names:
        if category == "VALIB":
            fallback_directory = os.path.join(env, 'data', category)
        else:
            fallback_directory = os.path.join(env, 'data', plugin_version_number, category)
    
        # Check if fallback directory exists
        if not os.path.isdir(fallback_directory):
            version_directory = os.path.join(env, 'data')
            difference_map = {}
            for version in os.listdir(version_directory):
                if version == "VALIB":
                    continue
                if not os.path.isdir(os.path.join(env, 'data', version)):
                    continue
                if float(version) > float(plugin_version_number):
                    continue
                difference_map[version] = float(plugin_version_number) - float(version)
            
            if len(difference_map)>0: 
                best_version = min(difference_map, key=difference_map.get)
                plugin_version_number = best_version
            else:
                # Default if nothing is found
                plugin_version_number = "17.05"
            fallback_directory = os.path.join(env, 'data', plugin_version_number, category)

    
        # SKS : Call common code to query all JSONs of this category
        fallback_files = os.listdir(fallback_directory)
        fallback_files.sort()
        for filename in fallback_files:
            if not filename.endswith(".json"):
                continue
            function_dict = {}
            if category == "VALIB":
                filepath = os.path.join(category, filename)
            else:
                filepath = os.path.join(plugin_version_number, category, filename)
            function_dict["name"] = filename.replace(".json", "")
            function_dict["function_alias_name"] = function_dict["name"]
            function_dict["json_file_path"] = filepath
            function_dict["keyword"] = category
            choices.append(function_dict)


    # SKS : caluclate the versionInfo used in the version dialog
    versionInfo = ""

    enable_vantage_capability = False
    if enable_vantage_capability:
        if sql_query_worked:
            versionInfo += "Vantage Capability Supported"
        else:
            versionInfo += "Vantage Capability Not Available"
        versionInfo += "</br>" + "</br>"
    versionInfo += "The connected Analytics Database version is: " + vantage_version_number
    versionInfo += "<br>"
    versionInfo += "The plugin displays all analytic function titles released through version: " + plugin_version_number

                
         
    input_table_name = inputs[0]['fullName'].split('.')[1]
    input_dataset =  dataiku.Dataset(input_table_name)
    schema = input_dataset.read_schema()
    
    inputschemas = {}
    for inputdataset in inputs:
        inputtablename = inputdataset['fullName'].split('.')[1]
        inputdataset = dataiku.Dataset(inputtablename)
        inputschemas[inputtablename] = inputdataset.read_schema()
    
    connection = getConnectionParamsFromDataset(input_dataset)
    if connection:
        aafschema = ([property.get('value', '') for property in connection.\
                      get('connectionParams', {}).get('properties', {})
              if 'aafschema_700' == property.get('name', '')] or ['']).pop()
    
    # schema = None # Debugging.
    # inputschemas = None
    # aafschema = None
    
    val_db, default_db = get_val_default_database(inputdataset)

    print('I am done')
    return {'choices' : choices,
            'schema': schema,
            'inputs': inputs,
            'inputschemas': inputschemas,
            'aafschema': aafschema,
            'valDatabase' : val_db,
            'defaultDatabase' : default_db,
            'versionInfo' : versionInfo}

def isMultipleTagsInput(item):
    """
    Returns True if the argument datatype is not a column or a table, and if it allows lists and if it has no permitted value.
    
    This function is used to check whether the argument values have to be delimited by the null character (returns True) or not.
    :param item: Table argument.
    """
    return item.get('datatype', 'STRING') in ['STRING','DOUBLE','INTEGER','DRIVER','SQLEXPR', 'LONG']\
        and item.get('allowsLists', False)\
        and not item.get('permittedValues', [])
        
def defaultValuesFromArg(item):
    """
    Returns the default value for the given item.
    
    If the argument is not a required argument and not a boolean, we reset the default value to the empty string.
    :param item: Table argument.
    """
    defaultvalues = item.get('defaultValue', '')    
    
    # SKS : Always have defaults
    #if not item['isRequired'] and item["datatype"] != 'BOOLEAN':
    #    return ""
    
    if isMultipleTagsInput(item) and isinstance(defaultvalues, (list, tuple)):
        DELIMITER = chr(0)
        return DELIMITER.join(str(x) for x in defaultvalues)
        # print('B - returning defaultvalues from ' + item.get('name', ''))
    # print('C - returning defaultvalues from ' + item.get('name', ''))
    #if isinstance(defaultvalues, basestring):
    #   defaultvalues = json.dumps(defaultvalues)
    return defaultvalues

def inNativeCheck(a, a_n):
    """
    Checks if each argument in `a` is in the native function's list of arguments `a_n`.
    
    :param a: List of arguments.
    :param a_n: List of native arguments.
    """
    print("Native check.")
    arg_native_names = map(lambda d: d.get('name'), a_n)
    arg_native_alt_names = map(lambda d: d.get('alternateNames'), a_n)
    for arg in a:                
        if arg.get('name') in arg_native_names or arg.get('name') in arg_native_alt_names:
            print(arg.get('name'))
            arg["inNative"] = True
    return a 


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(do(None, {"category": "Data Transformation"}, None, None)['choices'][1])