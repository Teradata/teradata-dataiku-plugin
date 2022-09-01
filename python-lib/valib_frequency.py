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
        input_database_name = "{IN DATABASE}"
        main_input_name = "{IN TABLE}"
        output_database_name = "{OUT DATABASE}"
        main_output_name = "{OUT TABLE}"
        val_location = "{VAL DATABASE}"
    else:
        main_input_name = recipe_config["input_table_names"][0]["table"]
        input_database_name = recipe_config["input_table_names"][0]['schema']
        main_output_name = recipe_config["output_table_names"][0]["table"]
        output_database_name = recipe_config["output_table_names"][0]['schema']
        val_location = recipe_config["val_location"]

    # Frequency
    database = input_database_name
    tablename = main_input_name
    outputdatabase = output_database_name
    outputtablename = main_output_name

    columns = ",".join(recipe_config['frequency_columns'])

    optional_args = ""

    if 'frequency_cumulative_option' in recipe_config and recipe_config['frequency_cumulative_option']:
        optional_args += "cumulativeoption=" + str(recipe_config['frequency_cumulative_option']) + ";"

    if 'frequency_agg_filter' in recipe_config and recipe_config['frequency_agg_filter']:
        frequency_agg_filter = recipe_config['frequency_agg_filter']
        # Santize user specified string: No double quotes or odd number of single quotes
        if ('"' in frequency_agg_filter) or (frequency_agg_filter.count("'") % 2 == 1) or (';' in frequency_agg_filter):
            raise Exception('Illegal Filter', frequency_agg_filter)
        optional_args += "having=" + str(frequency_agg_filter) + ";"

    if 'frequency_min_percentage' in recipe_config and recipe_config['frequency_min_percentage']:
        optional_args += "minimumpercentage=" + str(recipe_config['frequency_min_percentage']) + ";"

    if 'frequency_style' in recipe_config and recipe_config['frequency_style']:
        optional_args += "style=" + recipe_config['frequency_style'] + ";"

    if 'frequency_pairwise_columns' in recipe_config and recipe_config['frequency_pairwise_columns']:
        optional_args += "pairwisecolumns=" + ",".join(recipe_config['frequency_pairwise_columns']) + ";"

    if 'frequency_stats_columns' in recipe_config and recipe_config['frequency_stats_columns']:
        optional_args += "statisticscolumns=" + ",".join(recipe_config['frequency_stats_columns']) + ";"

    if 'frequency_top_n' in recipe_config and recipe_config['frequency_top_n']:
        optional_args += "topvalues=" + str(recipe_config['frequency_top_n']) + ";"

    if 'frequency_filter_where' in recipe_config and recipe_config['frequency_filter_where']:
        frequency_filter_where = recipe_config['frequency_filter_where']
        # Santize user specified string: No double quotes or odd number of single quotes
        if ('"' in frequency_filter_where) or (frequency_filter_where.count("'") % 2 == 1) or (';' in frequency_filter_where):
            raise Exception('Illegal Filter', frequency_filter_where)
        optional_args += "where=" + str(frequency_filter_where) + ";"




    query = """call {}.td_analyze('FREQUENCY', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    columns={};
    {}')""".format(verifyAttribute(val_location), verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(columns), verifyAttribute(optional_args))

    
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



