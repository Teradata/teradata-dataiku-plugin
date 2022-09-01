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

import xml.etree.ElementTree as ET
from query_engine_wrapper import QueryEngineWrapper
from verifyTableColumns import *



def execute(recipe_config, function_name, valib_query_wrapper=None):
    if not valib_query_wrapper:
        input_database_name = "{INPUT DATABASE}"
        main_input_name = "{INPUT TABLE}"
        output_database_name = "{OUTPUT DATABASE}"
        main_output_name = "{OUTPUT TABLE}"
        val_location = "{VAL DATABASE}"
        logreg_input_name = "{MODEL TABLE}"
    else:
        main_input_name = recipe_config["input_table_names"][0]["table"]
        input_database_name = recipe_config["input_table_names"][0]['schema']
        main_output_name = recipe_config["output_table_names"][0]["table"]
        output_database_name = recipe_config["output_table_names"][0]['schema']
        val_location = recipe_config["val_location"]
        logreg_input_name = recipe_config["input_table_names"][1]["table"]


    # Logreg predict/score
    database =  input_database_name
    outputdatabase = output_database_name
    modeldatabase = output_database_name
    tablename = main_input_name
    outputtablename = main_output_name


    model = logreg_input_name

    # common for both
    estimate_column = recipe_config['logreg2_estimate_column']

    optional_args = ""

    if 'logreg2_index_columns' in recipe_config and recipe_config['logreg2_index_columns']:
        optional_args += "index=" + ",".join(recipe_config['logreg2_index_columns']) + ";"

    if 'logreg2_prob_column' in recipe_config and recipe_config['logreg2_prob_column']:
        optional_args += "probability=" + recipe_config['logreg2_prob_column'] + ";"

    if 'logreg2_accumulate' in recipe_config and recipe_config['logreg2_accumulate']:
        optional_args = "retain=" + ",".join(recipe_config['logreg2_accumulate']) + ";"

    if 'logreg2_prob_threshold' in recipe_config and recipe_config['logreg2_prob_threshold']:
        optional_args += "threshold=" + str(recipe_config['logreg2_prob_threshold']) + ";"


    # evaluate
    if 'Evaluate' in function_name:

        if 'logreg2_start_threshold' in recipe_config and recipe_config['logreg2_start_threshold']:
            optional_args += "thresholdbegin=" + str(recipe_config['logreg2_start_threshold']) + ";"

        if 'logreg2_end_threshold' in recipe_config and recipe_config['logreg2_end_threshold']:
            optional_args += "thresholdend=" + str(recipe_config['logreg2_end_threshold']) + ";"

        if 'logreg2_increment_threshold' in recipe_config and recipe_config['logreg2_increment_threshold']:
            optional_args += "thresholdincrement=" + str(recipe_config['logreg2_increment_threshold']) + ";"

        optional_args += "scoringmethod=scoreandevaluate"

    else:

        optional_args += "scoringmethod=score"

    # Verify that all attributes do not have quotes
    query = """call {}.td_analyze('LOGISTICSCORE', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    modeldatabase={};
    modeltablename={};
    estimate={};
    {}')""".format(verifyAttribute(val_location), verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(modeldatabase), verifyAttribute(model), verifyAttribute(estimate_column), verifyAttribute(optional_args))

    
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)

    # Evaulate we must transform the report table into the output table
    if 'Evaluate' in function_name:
        # Need to Copy the values into the table
        output_table_name = main_output_name
        # The report table is same as output table but with prefix _txt
        output_table_name_rpt = main_output_name + "_txt"

        # Drop the output table that has the predictions as we do not need this
        query = "DROP TABLE {};".format(verifyTableName(output_table_name))
        valib_query_wrapper.execute(query)

        # Lets try to cleanup a report 
        cleanupReport = True
        if cleanupReport:
            # Get the XML contents from the report table
            query = "SELECT * FROM {};".format(verifyTableName(output_table_name_rpt))
            result_df = valib_query_wrapper.execute(query)
            xmlModel = None
            for row in valib_query_wrapper.iteratable(result_df):
                xmlModel = valib_query_wrapper.row_value(row, "XmlModel")
            try:
                # Use Python library ElementTree to load root of XML
                root = ET.fromstring(xmlModel)
                # Contents are three nodes deep
                reports = root[0]
                confusionMatrix = reports[0]
                # Build a list of each row we want to add
                outputRows = []
                for lineItem in confusionMatrix:
                    outputRows.append({"Desc" : lineItem.attrib["Desc"], "Percent" : lineItem.attrib["Percent"].strip("%"), "count" : lineItem.attrib["count"]})
                if outputRows:
                    # Create the output table with the 3 columns
                    query = "CREATE TABLE {} (Description varchar(255), Percentage float, TotalCount int);\n".format(verifyTableName(output_table_name))
                    valib_query_wrapper.execute(query)
                    insert = ""
                    # Create and execute the INSERT where we insert each row into the output table
                    for row in outputRows:
                        insert += "INSERT INTO {} VALUES  ('{}', {}, {});".format(verifyTableName(output_table_name), verifyAttribute(row["Desc"]), verifyAttribute(row["Percent"]), verifyAttribute(row["count"]))
                    query = insert
                    valib_query_wrapper.execute(query)
                else:
                    # Failed to cleanup the report
                    cleanupReport = False
            except:
                # Failed to cleanup the report
                cleanupReport = False

        if not cleanupReport:
            # If we failed to cleanup report then just output the XML into the output table (i.e output is a duplicate of the report table)
            query = "CREATE TABLE {} AS (SELECT * FROM {}) WITH DATA NO PRIMARY INDEX;".format(verifyTableName(output_table_name), verifyTableName(output_table_name_rpt))
            valib_query_wrapper.execute(query)


