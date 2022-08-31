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

    # Linreg
    database =  input_database_name
    outputdatabase = output_database_name
    tablename = main_input_name
    outputtablename = main_output_name

    columns = ",".join(recipe_config['linreg_columns'])
    dependent = recipe_config['linreg_dependent']

    optional_args = ""
    if 'linreg_groupby' in recipe_config and recipe_config['linreg_groupby']:
        optional_args += "groupby=" + ",".join(recipe_config['linreg_groupby']) + ";"

    if 'linreg_stepwise' in recipe_config and recipe_config['linreg_stepwise']:
        optional_args += "stepwise=" + str(recipe_config['linreg_stepwise']) + ";"

    if 'linreg_backward' in recipe_config and recipe_config['linreg_backward']:
        optional_args += "backward=" + str(recipe_config['linreg_backward']) + ";"

    if 'linreg_backward_only' in recipe_config and recipe_config['linreg_backward_only']:
        optional_args += "backwardonly=" + str(recipe_config['linreg_backward']) + ";"

    if 'linreg_forward' in recipe_config and recipe_config['linreg_forward']:
        optional_args += "forward=" + str(recipe_config['linreg_forward']) + ";"

    if 'linreg_forward_only' in recipe_config and recipe_config['linreg_forward_only']:
        optional_args += "forwardonly=" + str(recipe_config['linreg_forward_only']) + ";"

    if 'linreg_use_fstat' in recipe_config and recipe_config['linreg_use_fstat']:
        optional_args += "usefstat=" + str(recipe_config['linreg_use_fstat']) + ";"

    if 'linreg_use_pvalue' in recipe_config and recipe_config['linreg_use_pvalue']:
        optional_args += "usepvalue=" + str(recipe_config['linreg_use_pvalue']) + ";"


    if 'linreg_constant' in recipe_config and recipe_config['linreg_constant']:
        optional_args += "constant=" + str(recipe_config['linreg_constant']) + ";"

    if 'linreg_matrix_input' in recipe_config and recipe_config['linreg_matrix_input']:
        optional_args += "matrixinput=" + str(recipe_config['linreg_matrix_input']) + ";"

    if 'linreg_near_dep_report' in recipe_config and recipe_config['linreg_near_dep_report']:
        optional_args += "neardependencyreport=" + str(recipe_config['linreg_near_dep_report']) + ";"

    if 'linreg_stats_output' in recipe_config and recipe_config['linreg_stats_output']:
        optional_args += "statstable=" + str(recipe_config['linreg_stats_output']) + ";"

    if 'linreg_cond_ind_threshold' in recipe_config and recipe_config['linreg_cond_ind_threshold']:
        optional_args += "conditionindexthreshold=" + str(recipe_config['linreg_cond_ind_threshold']) + ";"

    # large positive
    if 'linreg_entrance_criterion' in recipe_config and recipe_config['linreg_entrance_criterion']:
        optional_args += "enter=" + str(recipe_config['linreg_entrance_criterion']) + ";"

    # negative
    if 'linreg_remove_criterion' in recipe_config and recipe_config['linreg_remove_criterion']:
        optional_args += "remove=" + str(recipe_config['linreg_remove_criterion']) + ";"

    if 'linreg_variance_prop_threshold' in recipe_config and recipe_config['linreg_variance_prop_threshold']:
        optional_args += "varianceproportionthreshold=" + str(recipe_config['linreg_variance_prop_threshold']) + ";"


    query = """call SYSLIB.td_analyze('LINEAR', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    columns={};
    dependent={};
    {}')""".format(verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(columns), verifyAttribute(dependent), verifyAttribute(optional_args))

    query = query.replace("SYSLIB", verifyAttribute(val_location))
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)
    


