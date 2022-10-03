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
        pca_model_input_name = "{MODEL TABLE}"
    else:
        main_input_name = recipe_config["input_table_names"][0]["table"]
        input_database_name = recipe_config["input_table_names"][0]['schema']
        main_output_name = recipe_config["output_table_names"][0]["table"]
        output_database_name = recipe_config["output_table_names"][0]['schema']
        val_location = recipe_config["val_location"]
        pca_model_input_name = recipe_config["input_table_names"][1]["table"]


    # pca_model predict/score
    database =  input_database_name
    outputdatabase = output_database_name
    modeldatabase = output_database_name
    tablename = main_input_name
    outputtablename = main_output_name


    model = pca_model_input_name



    # common for both
    optional_args = ""

    if 'pca2_index_columns' in recipe_config and recipe_config['pca2_index_columns']:
        optional_args += "index=" + ",".join(recipe_config['pca2_index_columns']) + ";"

    if 'pca2_accumulate' in recipe_config and recipe_config['pca2_accumulate']:
        optional_args = "retain=" + ",".join(recipe_config['pca2_accumulate']) + ";"


    # evaluate
    if 'Evaluate' in function_name:
        optional_args += "scoringmethod=scoreandevaluate" + ";"
    else:
        optional_args += "scoringmethod=score" + ";"



    query = """call {}.td_analyze('FACTORSCORE', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    modeldatabase={};
    modeltablename={};
    {}')""".format(verifyAttribute(val_location), verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(modeldatabase), verifyAttribute(model), verifyAttribute(optional_args))

    
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)

    # Evaulate we must transform the report table into the output table
    if 'Evaluate' in function_name:
        # Need to Copy the values into the table
        output_table_name = main_output_name
        # The report table is same as output table but with prefix _rpt
        output_table_name_rpt = main_output_name + "_rpt"

        # Drop the output table that has the predictions as we do not need this
        query = "DROP TABLE {};".format(verifyQualifiedTableName(output_database_name,output_table_name))
        valib_query_wrapper.execute(query)

        # Lets try to cleanup a report 
        cleanupReport = True
        if cleanupReport:
            # Get the XML contents from the report table
            query = "SELECT * FROM {};".format(verifyQualifiedTableName(output_database_name,output_table_name_rpt))
            result_df = valib_query_wrapper.execute(query)
            xmlModel = None
            for row in valib_query_wrapper.iteratable(result_df):
                xmlModel = valib_query_wrapper.row_value(row, "XmlModel")
            try:
                # Use Python library ElementTree to load root of XML
                root = ET.fromstring(xmlModel)
                # Contents are three nodes deep
                Variables = root[0][0][0]

                # Contents are three nodes deep
                outputRows = []
                for node in Variables:
                    outputRows.append({"Name" : node[0].text, "StandardErrorOfEstimates" : node[1].text})
                if outputRows:
                    # Create the output table with the 2 columns
                    query = "CREATE TABLE {} (Name varchar(255), StandardErrorOfEstimates float);\n".format(verifyQualifiedTableName(output_database_name,output_table_name))
                    valib_query_wrapper.execute(query)
                    # Create and execute the INSERT where we insert each row into the output table
                    insert = ""
                    for row in outputRows:
                        insert += "INSERT INTO {} VALUES  ('{}', {});".format(verifyQualifiedTableName(output_database_name,output_table_name), verifyAttribute(row["Name"]),  verifyAttribute(row["StandardErrorOfEstimates"]))
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
            query = "CREATE TABLE {} AS (SELECT * FROM {}) WITH DATA NO PRIMARY INDEX;".format(verifyQualifiedTableName(output_database_name,output_table_name), verifyQualifiedTableName(output_database_name,output_table_name_rpt))
            valib_query_wrapper.execute(query)


