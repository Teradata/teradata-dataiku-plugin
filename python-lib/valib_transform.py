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

import logging
from query_engine_wrapper import QueryEngineWrapper
from verifyTableColumns import *

def execute_transform(recipe_config, function_name, function_list, unique_name="", valib_query_wrapper=None):

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

        dropIfExists = recipe_config.get(unique_name + 'dropIfExists', False)

        if dropIfExists:
            outputTable = main_output_name
            drop_query = "DROP TABLE {};".format(verifyTableName(outputTable))
            try:
                valib_query_wrapper.execute(drop_query)
            except Exception as e:
                pass

    delayquery = recipe_config.get(unique_name + 'delayquery', True)

    if delayquery:
        select = ""
        for i in range(len(function_list)):
            select += "INSERT INTO {} ( DELAYTRANSFORM ) VALUES  ('{}={}');".format(verifyTableName(main_output_name), function_name, function_list[i])
        query = "CREATE TABLE {} (DELAYTRANSFORM varchar(255));\n".format(verifyTableName(main_output_name))
        if not valib_query_wrapper:
            return query + "<br>" + select
        valib_query_wrapper.execute(query)
        query = select
        valib_query_wrapper.execute(query)
    else:
        # Do transform
        database = input_database_name
        tablename = main_input_name
        outputdatabase = output_database_name
        outputtablename = main_output_name
        keycolumns = ",".join(recipe_config[unique_name+'key_columns'])

        function_string = ""
        for f in function_list:
            function_string += f

        query = """call SYSLIB.td_analyze('VARTRAN', 
        'outputstyle={};{}={};database={};tablename={};outputdatabase={};outputtablename={};keycolumns={};');""".format('table', verifyAttribute(function_name), verifyAttribute(function_string), verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(keycolumns))

        if not valib_query_wrapper:
            return query

        # change double quotes to two single quotes
        query = query.replace('"', "''")

        query = query.replace("SYSLIB", verifyAttribute(val_location))
        if not valib_query_wrapper:
            return query
        
        valib_query_wrapper.execute(query)



def execute(recipe_config, valib_query_wrapper=None):

    if not valib_query_wrapper:
        input_database_name = "{INPUT DATABASE}"
        main_input_name = "{INPUT TABLE}"
        output_database_name = "{OUTPUT DATABASE}"
        main_output_name = "{OUTPUT TABLE}"
        val_location = "{VAL DATABASE}"
        # binning
        bincode = "..bincode rows.."
        # derive
        derive = "..derive rows.."
        # labelencoder 
        recode = "..recode rows.."
        # minmaxscalar
        rescale = "..rescale rows.."
        # onehotencoder  
        designcode = "..designcode rows.."
        # retain
        retain = "..retain rows.."
        # sigmpoid
        sigmoid = "..sigmoid rows.." 
        # zscore 
        zscore = "..zscore rows.."
    else:
        main_input_name = recipe_config["input_table_names"][0]["table"]
        input_database_name = recipe_config["input_table_names"][0]['schema']
        main_output_name = recipe_config["output_table_names"][0]["table"]
        output_database_name = recipe_config["output_table_names"][0]['schema']
        val_location = recipe_config["val_location"]

        # binning
        bincode = ""
        # derive
        derive = ""
        # labelencoder 
        recode = ""
        # minmaxscalar
        rescale = ""
        # onehotencoder  
        designcode = ""
        # retain
        retain = ""
        # sigmpoid
        sigmoid = "" 
        # zscore 
        zscore = ""

        try:
            delay_table = recipe_config["input_table_names"][1]["datasetName"]
            if delay_table:
                delay_df = valib_query_wrapper.get_dataframe(delay_table)
                for row in valib_query_wrapper.iterrows(delay_df):
                    value = row[1][0]
                    if "bincode=" in value:
                        bincode += value.replace("bincode=","")
                    if "derive=" in value:
                        derive += value.replace("derive=","")
                    if "recode=" in value:
                        recode += value.replace("recode=","")
                    if "rescale=" in value:
                        rescale += value.replace("rescale=","")
                    if "designcode=" in value:
                        designcode += value.replace("designcode=","")
                    if "retain=" in value:
                        retain += value.replace("retain=","")
                    if "sigmoid=" in value:
                        sigmoid += value.replace("sigmoid=","")
                    if "zscore=" in value:
                        zscore += value.replace("zscore=","")
        except:
            logging.info("No delayed functions")


        # transform
        lst = []


        # Handle dropping of output tables.
        if recipe_config.get('dropIfExists', False):
            outputTable = main_output_name
            drop_query = "DROP TABLE {};".format(verifyTableName(outputTable))
            try:
                valib_query_wrapper.execute(drop_query)
            except Exception as e:
                logging.info(e)


    database = input_database_name
    tablename = main_input_name
    outputdatabase = output_database_name
    outputtablename = main_output_name
    keycolumns =  ",".join(recipe_config['transform_key_columns'])

    available_functions = ""
    if bincode != "":
        available_functions += "bincode={};".format(bincode)

    if derive != "":
        available_functions += "derive={};".format(derive)

    if recode != "":
        available_functions += "recode={};".format(recode)

    if rescale != "":
        available_functions += "rescale={};".format(rescale)

    if designcode != "":
        available_functions += "designcode={};".format(designcode)

    if retain != "":
        available_functions += "retain={};".format(retain)

    if sigmoid != "":
        available_functions += "sigmoid={};".format(sigmoid)

    if zscore != "":
        available_functions += "zscore={};".format(zscore)


    query = """call SYSLIB.td_analyze('VARTRAN', 
    'outputstyle={};
    {};
    database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    keycolumns={};');""".format('table', verifyAttribute(available_functions), verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(keycolumns))
    
    # change double quotes to two single quotes
    query = query.replace('"', "''")


    query = query.replace("SYSLIB", verifyAttribute(val_location))
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



