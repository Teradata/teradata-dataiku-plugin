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


    # Decision Tree
    database = input_database_name
    tablename = main_input_name
    outputdatabase = output_database_name
    outputtablename = main_output_name

    columns = ",".join(recipe_config['decision_tree_columns'])
    response_column = recipe_config['decision_tree_response_column']

    optional_args = ""

    if 'decision_tree_algorithm' in recipe_config and recipe_config['decision_tree_algorithm']:
        optional_args += "algorithm=" + str(recipe_config['decision_tree_algorithm']) + ";"

    if 'decision_tree_binning' in recipe_config and recipe_config['decision_tree_binning'] != False:
        optional_args += "binning=" + str(recipe_config['decision_tree_binning']) + ";"

    if 'decision_tree_max_depth' in recipe_config and recipe_config['decision_tree_max_depth'] != 100:
        optional_args += "max_depth=" + str(recipe_config['decision_tree_max_depth']) + ";"

    if 'decision_tree_num_splits' in recipe_config and recipe_config['decision_tree_num_splits']:
        optional_args += "min_records=" + str(recipe_config['decision_tree_num_splits']) + ";"

    if 'decision_tree_pruning' in recipe_config and recipe_config['decision_tree_pruning']:
        optional_args += "pruning=" + str(recipe_config['decision_tree_pruning']) + ";"

    optional_args += "operatordatabase=" + val_location + ";"

    query = "call SYSLIB.td_analyze('DECISIONTREE', \
    'database={};\
    tablename={};\
    outputdatabase={};\
    outputtablename={};\
    columns={};\
    dependent={};\
    {}')"\
    .format(database, tablename, outputdatabase, outputtablename, columns, response_column, optional_args)

    query = query.replace("SYSLIB", val_location)
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



