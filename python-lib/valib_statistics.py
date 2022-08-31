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

    # Statistics

    database = input_database_name
    tablename = main_input_name
    outputdatabase = output_database_name
    outputtablename = main_output_name

    columns = ",".join(recipe_config['statistics_columns'])


    optional_args = ""

    if 'statistics_group_columns' in recipe_config and recipe_config['statistics_group_columns']:
        optional_args += "groupby=" + ",".join(recipe_config['statistics_group_columns']) + ";"

    if 'statistics_stats_options' in recipe_config and recipe_config['statistics_stats_options']:
        values = ",".join((recipe_config['statistics_stats_options']))
        if values:
            optional_args += "statsoptions=" + values + ";"

    if 'statistics_extended_options' in recipe_config and recipe_config['statistics_extended_options']:
        values = ",".join((recipe_config['statistics_extended_options']))
        if values:
            optional_args += "extendedoptions=" + values + ";"

    if 'statistics_statistical_method' in recipe_config and recipe_config['statistics_statistical_method']:
        optional_args += "statisticalmethod=" + str(recipe_config['statistics_statistical_method']) + ";"

    if 'statistics_filter' in recipe_config and recipe_config['statistics_filter']:
        statistics_filter = recipe_config['statistics_filter']
        # Santize user specified string: No double quotes or odd number of single quotes or semicolon
        if ('"' in statistics_filter) or (statistics_filter.count("'") % 2 == 1) or (';' in statistics_filter):
            raise Exception('Illegal Filter', statistics_filter)
        optional_args += "where=" + str(statistics_filter) + ";"



    query = """call SYSLIB.td_analyze('STATISTICS',
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    columns={};
    {}')""".format(verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(columns), verifyAttribute(optional_args))
    
    query = query.replace("SYSLIB", verifyAttribute(val_location))
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



