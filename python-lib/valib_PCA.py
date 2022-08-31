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


    # PCA
    database = input_database_name
    tablename = main_input_name
    outputdatabase = output_database_name
    outputtablename = main_output_name

    columns = ",".join(recipe_config['pca_columns'])

    optional_args = ""

    if 'pca_group_columns' in recipe_config and recipe_config['pca_group_columns']:
        optional_args += "groupby=" + ",".join(recipe_config['pca_group_columns']) + ";"

    if 'pca_cond_ind_threshold' in recipe_config and recipe_config['pca_cond_ind_threshold']:
        optional_args += "conditionindexthreshold=" + str(recipe_config['pca_cond_ind_threshold']) + ";"

    if 'pca_min_eigen' in recipe_config and recipe_config['pca_min_eigen']:
        optional_args += "eigenmin=" + str(recipe_config['pca_min_eigen']) + ";"

    if 'pca_rotation_type' in recipe_config and recipe_config['pca_rotation_type']:
        optional_args += "rotationtype=" + str(recipe_config['pca_rotation_type']) + ";"

    if 'pca_gamma' in recipe_config and recipe_config['pca_gamma']:
        optional_args += "gamma=" + str(recipe_config['pca_gamma']) + ";"

    if 'pca_matrix_input' in recipe_config and recipe_config['pca_matrix_input']:
        optional_args += "matrixinput=" + str(recipe_config['pca_matrix_input']) + ";"

    if 'pca_matrix_type' in recipe_config and recipe_config['pca_matrix_type']:
        optional_args += "matrixtype=" + str(recipe_config['pca_matrix_type']) + ";"

    if 'pca_near_dep_report' in recipe_config and recipe_config['pca_near_dep_report']:
        optional_args += "neardependencyreport=" + str(recipe_config['pca_near_dep_report']) + ";"

    if 'pca_load_report' in recipe_config and recipe_config['pca_load_report']:
        optional_args += "factorloadingsreport=" + str(recipe_config['pca_load_report']) + ";"

    if 'pca_vars_load_report' in recipe_config and recipe_config['pca_vars_load_report']:
        optional_args += "factorvariablesloadingsreport=" + str(recipe_config['pca_vars_load_report']) + ";"

    if 'pca_vars_report' in recipe_config and recipe_config['pca_vars_report']:
        optional_args += "factorvariablesreport=" + str(recipe_config['pca_vars_report']) + ";"

    if 'pca_load_threshold' in recipe_config and recipe_config['pca_load_threshold']:
        optional_args += "thresholdloading=" + str(recipe_config['pca_load_threshold']) + ";"

    if 'pca_percent_threshold' in recipe_config and recipe_config['pca_percent_threshold']:
        optional_args += "thresholdpercent=" + str(recipe_config['pca_percent_threshold']) + ";"

    if 'pca_variance_prop_threshold' in recipe_config and recipe_config['pca_variance_prop_threshold']:
        optional_args += "varianceproportionthreshold=" + str(recipe_config['pca_variance_prop_threshold']) + ";"

    query = """call SYSLIB.td_analyze('FACTOR', 
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



