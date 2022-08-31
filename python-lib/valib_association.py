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
        description_data_input_name = "description_table"
        hierarchy_data_input_name = "hierarchy_table"
        left_lookup_data_input_name = "left_lookup_table"
        right_lookup_data_input_name = "right_lookup_table"
        reduced_data_input_name = "reduced_table"
    else:
        main_input_name = recipe_config["input_table_names"][0]["table"]
        input_database_name = recipe_config["input_table_names"][0]['schema']
        main_output_name = recipe_config["output_table_names"][0]["table"]
        output_database_name = recipe_config["output_table_names"][0]['schema']
        val_location = recipe_config["val_location"]

        description_data_input_name = None
        hierarchy_data_input_name = None
        left_lookup_data_input_name = None
        right_lookup_data_input_name = None
        reduced_data_input_name = None

        if len(recipe_config["input_table_names"]) >= 2:
            description_data_input_name = recipe_config["input_table_names"][1]["table"]
        if len(recipe_config["input_table_names"]) >= 3:
            hierarchy_data_input_name = recipe_config["input_table_names"][2]["table"]
        if len(recipe_config["input_table_names"]) >= 4:
            left_lookup_data_input_name = recipe_config["input_table_names"][3]["table"]
        if len(recipe_config["input_table_names"]) >= 5:
            right_lookup_data_input_name = recipe_config["input_table_names"][4]["table"]
        if len(recipe_config["input_table_names"]) >= 6:
            reduced_data_input_name = recipe_config["input_table_names"][5]["table"]


    # Association

    database = input_database_name
    tablename = main_input_name
    outputdatabase = output_database_name
    outputtablename = main_output_name

    group_column = recipe_config['association_group_column']
    item_column = recipe_config['association_item_column']

    optional_args = ""

    if 'association_combinations' in recipe_config and recipe_config['association_combinations']:
        optional_args += "combinations=" + str(recipe_config['association_combinations']) + ";"

    if 'association_description_data_exists' in recipe_config and recipe_config['association_description_data_exists'] == True:
        if 'association_description_identifier' in recipe_config and recipe_config['association_description_identifier']:
            optional_args += "descriptionidentifier=" + str(recipe_config['association_description_identifier']) + ";"

        if 'association_description_column' in recipe_config and recipe_config['association_description_column']:
            optional_args += "descriptioncolumn=" + str(recipe_config['association_description_column']) + ";"

    if 'association_group_count' in recipe_config and recipe_config['association_group_count']:
        optional_args += "groupcount=" + str(recipe_config['association_group_count']) + ";"

    if 'association_hierarchy_data_exists' in recipe_config and recipe_config['association_hierarchy_data_exists']!= False:
        if 'association_low_level_column' in recipe_config and recipe_config['association_low_level_column']:
            optional_args += "hierarchyitemcolumn=" + str(recipe_config['association_low_level_column']) + ";"

        if 'association_high_level_column' in recipe_config and recipe_config['association_high_level_column']:
            optional_args += "hierarchycolumn=" + str(recipe_config['association_high_level_column']) + ";"

    if 'association_left_lookup_data_exists' in recipe_config and recipe_config['association_left_lookup_data_exists']!= False:
        if 'association_left_lookup_column' in recipe_config and recipe_config['association_left_lookup_column']:
            optional_args += "leftlookupcolumn=" + str(recipe_config['association_left_lookup_column']) + ";"

    if 'association_right_lookup_data_exists' in recipe_config and recipe_config['association_right_lookup_data_exists']!= False:
        if 'association_right_lookup_column' in recipe_config and recipe_config['association_right_lookup_column']:
            optional_args += "rightlookupcolumn=" + str(recipe_config['association_right_lookup_column']) + ";"

    if 'association_min_confidence' in recipe_config and recipe_config['association_min_confidence']:
        optional_args += "minimumconfidence=" + str(recipe_config['association_min_confidence']) + ";"

    if 'association_min_lift' in recipe_config and recipe_config['association_min_lift']:
        optional_args += "minimumlift=" + str(recipe_config['association_min_lift']) + ";"

    if 'association_min_support' in recipe_config and recipe_config['association_min_support']:
        optional_args += "minimumsupport=" + str(recipe_config['association_min_support']) + ";"

    if 'association_min_zscore' in recipe_config and recipe_config['association_min_zscore']:
        optional_args += "minimumzscore=" + str(recipe_config['association_min_zscore']) + ";"

    if 'association_order_prob' in recipe_config and recipe_config['association_order_prob']:
        optional_args += "orderingprobability=" + str(recipe_config['association_order_prob']) + ";"

    if 'association_process_type' in recipe_config and recipe_config['association_process_type']:
        optional_args += "processtype=" + str(recipe_config['association_process_type']) + ";"

    if 'association_relaxed_order' in recipe_config and recipe_config['association_relaxed_order'] != False:
        optional_args += "relaxedordering=" + str(recipe_config['association_relaxed_order']) + ";"
        if 'association_sequence_column' in recipe_config and recipe_config['association_sequence_column']:
            optional_args += "sequencecolumn=" + str(recipe_config['association_sequence_column']) + ";"

    if 'association_filter' in recipe_config and recipe_config['association_filter']:
        association_filter = recipe_config['association_filter']
        # Santize user specified string: No double quotes or odd number of single quotes and no semicolons
        if ('"' in association_filter) or (association_filter.count("'") % 2 == 1) or (';' in association_filter):
            raise Exception('Invalid Filter', association_filter)
        optional_args += "where=" + str(association_filter) + ";"

    if 'association_no_support_results' in recipe_config and recipe_config['association_no_support_results']:
        optional_args += "dropsupporttables=" + str(recipe_config['association_no_support_results']) + ";"

    if 'association_support_result_prefix' in recipe_config and recipe_config['association_support_result_prefix']:
        association_support_result_prefix = recipe_config['association_support_result_prefix']
        # Santize user specified string: No double quotes or single quotes
        if ('"' in association_support_result_prefix) or ("'" in association_support_result_prefix):
            raise Exception('Illegal Prefix', association_support_result_prefix)
        optional_args += "resulttableprefix=" + str(association_support_result_prefix) + ";"



    query = """call SYSLIB.td_analyze('ASSOCIATION', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    groupcolumn={};
    itemcolumn={};
    {}')""".format(verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(group_column), verifyAttribute(item_column), verifyAttribute(optional_args))

    query = query.replace("SYSLIB", verifyAttribute(val_location))
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



