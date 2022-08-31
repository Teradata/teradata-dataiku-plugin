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


def execute(recipe_config, function_name, valib_query_wrapper=None):
    if not valib_query_wrapper:
        input_database_name = "{INPUT DATABASE}"
        main_input_name = "{INPUT TABLE}"
        output_database_name = "{OUTPUT DATABASE}"
        main_output_name = "{OUTPUT TABLE}"
        val_location = "{VAL DATABASE}"
        linreg_input_name = "{MODEL TABLE}"
    else:
        main_input_name = recipe_config["input_table_names"][0]["table"]
        input_database_name = recipe_config["input_table_names"][0]['schema']
        main_output_name = recipe_config["output_table_names"][0]["table"]
        output_database_name = recipe_config["output_table_names"][0]['schema']
        val_location = recipe_config["val_location"]
        linreg_input_name = recipe_config["input_table_names"][1]["table"]
        

    # Linreg predict/score
    database =  input_database_name
    outputdatabase = output_database_name
    modeldatabase = output_database_name
    tablename = main_input_name
    outputtablename = main_output_name


    model = linreg_input_name

    # predict
    if 'Predict' in function_name:

        index_columns = ",".join(recipe_config['linreg2_index_columns'])
        response_column = recipe_config['linreg2_response_column']

        if 'linreg2_accumulate' in recipe_config and recipe_config['linreg2_accumulate']:
            accumulate = "retain=" + ",".join(recipe_config['linreg2_accumulate']) + ";"

        query = """call SYSLIB.td_analyze('LINEARSCORE', 
        'database={};
        tablename={};
        outputdatabase={};
        outputtablename={};
        modeldatabase={};
        modeltablename={};
        index={};
        predicted={};
        {}')""".format(verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(modeldatabase), verifyAttribute(model), verifyAttribute(index_columns), verifyAttribute(response_column), verifyAttribute(accumulate))
        
    else: 
        query = """call SYSLIB.td_analyze('LINEARSCORE', 
        'database={};
        tablename={};
        outputdatabase={};
        outputtablename={};
        modeldatabase={};
        modeltablename={};
        scoringmethod=scoreandevaluate;')""".format(verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(modeldatabase), verifyAttribute(model))

    query = query.replace("SYSLIB", verifyAttribute(val_location))
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



