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

        lst_input_tablename = []
        lst_input_tablename.append(main_input_name)
        lst_columns = []
        columns1 = "{"+ ",".join(recipe_config['overlap_columns1']) +"}"
        lst_columns.append(columns1)

        lst_input_datasets = []
        lst_input_datasets.append(input_database_name)


    num_of_datasets = int(recipe_config['overlap_num_datasets'])

    for i in range(2, 1+num_of_datasets):
        data_input_name = recipe_config["input_table_names"][i-1]["name"]
        if data_input_name:
            table_name = recipe_config["input_table_names"][i-1]["table"]
            lst_input_tablename.append(table_name)
            input_database_name = recipe_config["input_table_names"][i-1]['schema']
            lst_input_datasets.append(input_database_name)
            columns = "{"+ ",".join(recipe_config['overlap_columns'+str(i)]) +"}"
            lst_columns.append(columns)


    # overlap
    database = ",".join(lst_input_datasets)
    tablename = ",".join(lst_input_tablename)
    outputdatabase = output_database_name
    outputtablename = main_output_name

    columns = ",".join(lst_columns)


    query = """call SYSLIB.td_analyze('OVERLAP', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    columns={};')""".format(verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(columns))

    query = query.replace("SYSLIB", verifyAttribute(val_location))
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



