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
from teradata_valib import *

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


    # XmlToHtmlReport
    database = input_database_name
    outputdatabase = output_database_name
    outputtablename = main_output_name
    # fix 
    tablename = main_input_name

    analysis_type = recipe_config['xmlToHtmlReport_analysis_type']

    optional_args = ""

    if 'xmlToHtmlReport_filter' in recipe_config and recipe_config['xmlToHtmlReport_filter']:
        xmlToHtmlReport_filter = recipe_config['xmlToHtmlReport_filter']
        # Santize user specified string: No double quotes or odd number of single quotes and no semicolons
        if ('"' in xmlToHtmlReport_filter) or (xmlToHtmlReport_filter.count("'") % 2 == 1) or (';' in xmlToHtmlReport_filter):
            raise Exception('Illegal Filter', xmlToHtmlReport_filter)
        optional_args += "where=" + str(xmlToHtmlReport_filter) + ";"

    # call VAL.td_analyze('REPORT', 'database=DSSDB;tablename=ml__valib_logreg_164852919855423;
    # outputdatabase=DSSDB;outputtablename=ml__valib_xmltohtmlreport_164853966752436;
    # analysistype=logistic;');

    query = """call {}.td_analyze('REPORT', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    analysistype={};
    {}')""".format(verifyAttribute(val_location), verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(analysis_type), verifyAttribute(optional_args))
    
    
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



