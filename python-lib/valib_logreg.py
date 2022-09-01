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

    # Logreg 

    database =  input_database_name
    outputdatabase = output_database_name
    tablename = main_input_name
    outputtablename = main_output_name

    columns = ",".join(recipe_config['logreg_columns'])
    response_column = recipe_config['logreg_response_column']

    optional_args = ""

    if 'logreg_backward' in recipe_config and recipe_config['logreg_backward']:
        optional_args += "backward=" + str(recipe_config['logreg_backward']) + ";"

    if 'logreg_backward_only' in recipe_config and recipe_config['logreg_backward_only']:
        optional_args += "backwardonly=" + str(recipe_config['logreg_backward']) + ";"

    if 'logreg_cond_ind_threshold' in recipe_config and recipe_config['logreg_cond_ind_threshold']:
        optional_args += "conditionindexthreshold=" + str(recipe_config['logreg_cond_ind_threshold']) + ";"

    if 'logreg_constant' in recipe_config and recipe_config['logreg_constant']:
        optional_args += "constant=" + str(recipe_config['logreg_constant']) + ";"

    if 'logreg_convergence' in recipe_config and recipe_config['logreg_convergence']:
        optional_args += "convergence=" + str(recipe_config['logreg_convergence']) + ";"

    if 'logreg_entrance_criterion' in recipe_config and recipe_config['logreg_entrance_criterion']:
        optional_args += "enter=" + str(recipe_config['logreg_entrance_criterion']) + ";"

    if 'logreg_forward' in recipe_config and recipe_config['logreg_forward']:
        optional_args += "forward=" + str(recipe_config['logreg_forward']) + ";"

    if 'logreg_forward_only' in recipe_config and recipe_config['logreg_forward_only']:
        optional_args += "forwardonly=" + str(recipe_config['logreg_forward_only']) + ";"

    if 'logreg_group_columns' in recipe_config and recipe_config['logreg_group_columns']:
        optional_args += "groupby=" + ",".join(recipe_config['logreg_group_columns']) + ";"

    if 'logreg_lift_output' in recipe_config and recipe_config['logreg_lift_output']:
        optional_args += "lifttable=" + str(recipe_config['logreg_lift_output']) + ";"
    # matrixdatabase=DSSDB;matrixtablename=ml__valib_matrix_1645573558525563;');
    if 'logreg_matrix_data' in recipe_config and recipe_config['logreg_matrix_data']:
        optional_args += "matrix_data=" + str(recipe_config['logreg_matrix_data']) + ";"

    if 'logreg_max_iter' in recipe_config and recipe_config['logreg_max_iter']:
        optional_args += "maxiterations=" + str(recipe_config['logreg_max_iter']) + ";"

    if 'logreg_mem_size' in recipe_config and recipe_config['logreg_mem_size']:
        optional_args += "memorysize=" + str(recipe_config['logreg_mem_size']) + ";"

    if 'logreg_near_dep_report' in recipe_config and recipe_config['logreg_near_dep_report']:
        optional_args += "neardependencyreport=" + str(recipe_config['logreg_near_dep_report']) + ";"

    if 'logreg_remove_criterion' in recipe_config and recipe_config['logreg_remove_criterion']:
        optional_args += "remove=" + str(recipe_config['logreg_remove_criterion']) + ";"

    if 'logreg_response_value' in recipe_config and recipe_config['logreg_response_value']:
        optional_args += "response=" + str(recipe_config['logreg_response_value'])+ ";"

    if 'logreg_sample' in recipe_config and recipe_config['logreg_sample']:
        optional_args += "sample=" + str(recipe_config['logreg_sample']) + ";"

    if 'logreg_stats_output' in recipe_config and recipe_config['logreg_stats_output']:
        optional_args += "statstable=" + str(recipe_config['logreg_stats_output']) + ";"

    if 'logreg_stepwise' in recipe_config and recipe_config['logreg_stepwise']:
        optional_args += "stepwise=" + str(recipe_config['logreg_stepwise']) + ";"

    if 'logreg_success_output' in recipe_config and recipe_config['logreg_success_output']:
        optional_args += "successtable=" + str(recipe_config['logreg_success_output']) + ";"

    if 'logreg_start_threshold' in recipe_config and recipe_config['logreg_start_threshold']:
        optional_args += "thresholdbegin=" + str(recipe_config['logreg_start_threshold']) + ";"

    if 'logreg_end_threshold' in recipe_config and recipe_config['logreg_end_threshold']:
        optional_args += "thresholdend=" + str(recipe_config['logreg_end_threshold']) + ";"

    if 'logreg_increment_threshold' in recipe_config and recipe_config['logreg_increment_threshold']:
        optional_args += "thresholdincrement=" + str(recipe_config['logreg_increment_threshold']) + ";"

    if 'logreg_threshold_output' in recipe_config and recipe_config['logreg_threshold_output']:
        optional_args += "thresholdtable=" + str(recipe_config['logreg_threshold_output']) + ";"

    if 'logreg_variance_prop_threshold' in recipe_config and recipe_config['logreg_variance_prop_threshold']:
        optional_args += "varianceproportionthreshold=" + str(recipe_config['logreg_variance_prop_threshold']) + ";"


    query = """call {}.td_analyze('LOGISTIC', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    columns={};
    dependent={};
    {}')""".format(verifyAttribute(val_location), verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(columns), verifyAttribute(response_column), verifyAttribute(optional_args))

    
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



