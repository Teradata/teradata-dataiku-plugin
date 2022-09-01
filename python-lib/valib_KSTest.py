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

from query_engine_wrapper import QueryEngineWrapper
from verifyTableColumns import *


def execute(recipe_config, valib_query_wrapper=None):
    if not valib_query_wrapper:
        input_database_name = "{INPUT DATABASE}"
        main_input_name = "{INPUT TABLE}"
        output_database_name = "{OUTPUT DATABASE}"
        main_output_name = "{OUTPUT TABLE}"
        val_location = "{VAL DATABASE}"
    else:
        main_input_name = recipe_config["input_table_names"][0]["table"]
        input_database_name = recipe_config["input_table_names"][0]['schema']
        main_output_name = recipe_config["output_table_names"][0]["table"]
        output_database_name = recipe_config["output_table_names"][0]['schema']
        val_location = recipe_config["val_location"]

    # KSTest

    database = input_database_name
    tablename = main_input_name
    outputdatabase = output_database_name
    outputtablename = main_output_name


    dependent_column = recipe_config['ks_test_dependent_column']

    optional_args = ""

    if 'ks_test_columns' in recipe_config and  recipe_config['ks_test_columns']:
        optional_args += "columns=" + ",".join(recipe_config['ks_test_columns']) + ";"

    if 'ks_test_fallback' in recipe_config and  recipe_config['ks_test_fallback']:
        optional_args += "fallback=" + str(recipe_config['ks_test_fallback']) + ";"

    if 'ks_test_group_columns' in recipe_config and  recipe_config['ks_test_group_columns']:
        optional_args += "groupby=" + ",".join(recipe_config['ks_test_group_columns']) + ";"

    if 'ks_test_allow_duplicates' in recipe_config and  recipe_config['ks_test_allow_duplicates']:
        optional_args += "multiset=" + str(recipe_config['ks_test_allow_duplicates']) + ";"

    optional_args += "statsdatabase=" + val_location + ";"

    if 'ks_test_style' in recipe_config and  recipe_config['ks_test_style']:
        optional_args += "teststyle=" + str(recipe_config['ks_test_style']) + ";"

    if 'ks_test_probability_threshold' in recipe_config and  recipe_config['ks_test_probability_threshold']:
        optional_args += "thresholdprobability=" + str(recipe_config['ks_test_probability_threshold']) + ";"


    query = """call {}.td_analyze('KSTEST', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    columnofinterest={};
    {}')""".format(verifyAttribute(val_location), verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(dependent_column), verifyAttribute(optional_args))

    
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



