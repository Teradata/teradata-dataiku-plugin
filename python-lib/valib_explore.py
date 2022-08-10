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
        frequency_output = "{FREQUENCY TABLE}"
        histogram_output = "{HISTOGRAM TABLE}"
        statistics_output = "{STATISTICS TABLE}"
        values_output = "{VALUE TABLE}"
    else:
        main_input_name = recipe_config["input_table_names"][0]["table"]
        input_database_name = recipe_config["input_table_names"][0]['schema']
        main_output_name = recipe_config["output_table_names"][0]["table"]
        output_database_name = recipe_config["output_table_names"][0]['schema']
        val_location = recipe_config["val_location"]

        if len(recipe_config["output_table_names"]) != 4:
            raise RuntimeError("Need to have 4 outputs")

        frequency_output_name = recipe_config["output_table_names"][0]["table"]
        histogram_output_name = recipe_config["output_table_names"][1]["table"]
        statistics_output_name = recipe_config["output_table_names"][2]["table"]
        values_output_name = recipe_config["output_table_names"][3]["table"]

        frequency_output_database_name = recipe_config["output_table_names"][0]['schema']
        histogram_output_database_name = recipe_config["output_table_names"][1]['schema']
        statistics_output_database_name = recipe_config["output_table_names"][2]['schema']
        values_output_database_name = recipe_config["output_table_names"][3]['schema']


    # Explore 

    database =  input_database_name
    outputdatabase = frequency_output_database_name
    tablename = main_input_name
    frequency = frequency_output_name
    histogram = histogram_output_name
    statistics = statistics_output_name
    values = values_output_name


    optional_args = ""

    if 'explore_columns' in recipe_config and recipe_config['explore_columns']:
        optional_args += "columns=" + ",".join(recipe_config['explore_columns']) + ";"

    if 'explore_bins' in recipe_config and recipe_config['explore_bins'] != 10:
        optional_args += "bins=" + recipe_config['explore_bins'] + ";"

    if 'explore_bin_style' in recipe_config and recipe_config['explore_bin_style']:
        optional_args += "binstyle=" + recipe_config['explore_bin_style'] + ";"

    if 'explore_max_comb_values' in recipe_config and recipe_config['explore_max_comb_values'] != 10000:
        optional_args += "maxnumcombvalues=" + recipe_config['explore_max_comb_values'] + ";"

    if 'explore_max_unique_char_values' in recipe_config and recipe_config['explore_max_unique_char_values'] != 100:
        optional_args += "maxuniquecharvalues=" + recipe_config['explore_max_unique_char_values'] + ";"

    if 'explore_max_unique_num_values' in recipe_config and recipe_config['explore_max_unique_num_values'] != 20:
        optional_args += "maxuniquenumvalues=" + recipe_config['explore_max_unique_num_values'] + ";"

    if 'explore_min_comb_rows' in recipe_config and recipe_config['explore_min_comb_rows'] != 10:
        optional_args += "minrowsforcomb=" + recipe_config['explore_min_comb_rows'] + ";"

    if 'explore_restrict_freq' in recipe_config and recipe_config['explore_restrict_freq'] != True:
        optional_args += "restrictedfreqproc=" + recipe_config['explore_restrict_freq'] + ";"

    if 'explore_restrict_threshold' in recipe_config and recipe_config['explore_restrict_threshold'] != 1:
        optional_args += "restrictedthreshold=" + recipe_config['explore_restrict_threshold'] + ";"

    if 'explore_statistical_method' in recipe_config and recipe_config['explore_statistical_method']:
        optional_args += "statisticalmethod=" + recipe_config['explore_statistical_method'] + ";"

    if 'explore_stats_options' in recipe_config and recipe_config['explore_stats_options']:
        explore_stats_options = ",".join((recipe_config['explore_stats_options']))
        if explore_stats_options:
            optional_args += "statsoptions=" + explore_stats_options + ";"

    if 'explore_distinct' in recipe_config and recipe_config['explore_distinct'] != False:
        optional_args += "uniques=" + recipe_config['explore_distinct'] + ";"

    if 'explore_filter' in recipe_config and recipe_config['explore_filter']:
        explore_filter = recipe_config['explore_filter']
        # Santize user specified string: No double quotes or odd number of single quotes
        if ('"' in explore_filter) or (explore_filter.count("'") % 2 == 1) or (';' in explore_filter):
            raise Exception('Illegal Filter', explore_filter)
        optional_args += "where=" + str(explore_filter) + ";"


    query = "call SYSLIB.td_analyze('DATAEXPLORER',\
    'database={};\
    tablename={};\
    outputdatabase={};\
    frequencyoutputtablename= {};\
    histogramoutputtablename= {};\
    statisticsoutputtablename= {};\
    valuesoutputtablename= {};\
    {}')"\
    .format(database, tablename, outputdatabase, frequency, histogram, statistics, values, optional_args)

    query = query.replace("SYSLIB", val_location)
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



