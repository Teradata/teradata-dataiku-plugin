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


# Pretty-printing of Dictionaries.
import pprint
import logging
import json
import dataiku
from dataiku import Dataset
from dataiku.customrecipe import *
from dataiku.core.sql import SQLExecutor2

# Import plugin libs
from querybuilderfacade import *
from inputtableinfo import *
from outputtableinfo import *

# SQLE functions via Open ended query generation
from open_ended_query_generator import OpenEndedQueryGenerator
from vantage_schema import set_schema_from_vantage

# Valib functions
from teradata_valib import *


def vantageDo():

    """
    Takes the parameters set by the user from the UI, creates the query, and then executes it.
    """
    # Formatting options.
    SEP_LENGTH = 80
    SEP = "=" * SEP_LENGTH
    pp = pprint.PrettyPrinter(indent=4)
    
    # Recipe inputs
    main_input_name = get_input_names_for_role('main')[0]
    input_dataset = dataiku.Dataset(main_input_name)

    # Recipe outputs
    main_output_name = get_output_names_for_role('main')[0]
    output_dataset =  dataiku.Dataset(main_output_name)
    
    # Daitaiku DSS params
    client = dataiku.api_client()
    projectkey = main_input_name.split('.')[0]
    project = client.get_project(projectkey)
    connections = client.list_connections()

    recipe_config = get_recipe_config()

    # Datasets
    input_table_names = []
    output_table_names = []
    try:
        # Map dataset names to table names
        inputtables = {}
        inputschemas = {}
        datasetnames = {}
        input_names = get_input_names()
        for input_name in input_names:
            inputDataset = dataiku.Dataset(input_name)
            user_table_name = input_name.split('.')[1]
            connectionInfo = inputDataset.get_location_info()['info']
            connectionName = connectionInfo['connectionName']
            defaultDatabase = inputDataset.get_config()['params'].get('schema', '')
            if not defaultDatabase:
                defaultDatabase = connections[connectionName]['params']['defaultDatabase']
            full_table_name = connectionInfo['table']
            inputtables[user_table_name] = full_table_name
            inputschemas[user_table_name] = defaultDatabase
            datasetnames[user_table_name] = input_name
        recipe_config["function"]["inputtables"] = inputtables

        # generate parameter inputs tables map: name, datasetName, table and schema
        required_inputs = recipe_config["function"]["required_input"]
        for required_input in required_inputs:
            user_table_name = ""
            if "value" in required_input:
                user_table_name = required_input["value"]
            if user_table_name == "":
                if ("isRequired" in required_input) and required_input["isRequired"]:
                    raise RuntimeError("Input is missing - " + required_input["name"])
                # No input set by user, so keep empty
                input_table_names.append({})
                continue
            full_table_name = inputtables[user_table_name]
            defaultDatabase = inputschemas[user_table_name]
            table_map = {}
            table_map["name"] = user_table_name
            table_map["table"] = full_table_name
            table_map["schema"] = defaultDatabase
            table_map["datasetName"] = datasetnames[user_table_name]
            input_table_names.append(table_map)
        recipe_config["function"]["input_table_names"] = input_table_names

        # generate parameter output tables map: name, datasetName, table and schema
        for output_name in get_output_names_for_role('main'):
            outputDataset = dataiku.Dataset(output_name)
            user_table_name = output_name.split('.')[1]
            connectionInfo = outputDataset.get_location_info()['info']
            connectionName = connectionInfo['connectionName']
            defaultDatabase = inputDataset.get_config()['params'].get('schema', '')
            if not defaultDatabase:
                defaultDatabase = connections[connectionName]['params']['defaultDatabase']
            full_table_name = connectionInfo['table']
            table_map = {}
            table_map["name"] = user_table_name
            table_map["table"] = full_table_name
            table_map["schema"] = defaultDatabase
            table_map["datasetName"] = output_name
            output_table_names.append(table_map)
        recipe_config["function"]["output_table_names"] = output_table_names

    except Exception as error:
        raise RuntimeError("""Error obtaining connection settings from one of the input tables."""                           
                           """ This plugin only supports Teradata tables.""")

    
    # Connection properties.
    properties = input_dataset.get_location_info(sensitive_info=True)['info'].get('connectionParams').get('properties')
    autocommit = input_dataset.get_location_info(sensitive_info=True)['info'].get('connectionParams').get('autocommitMode')
    
    # SQL Executor.
    executor = SQLExecutor2(dataset=input_dataset)   
    
    # Handle pre- and post-query additions.
    # Assume autocommit TERA mode by default.
    pre_query = None
    post_query = None
    
    logging.info(SEP)
    if not autocommit:
        logging.info("NOT AUTOCOMMIT MODE.")
        logging.info("Assuming TERA mode.")
        pre_query = ["BEGIN TRANSACTION;"]
        post_query = ["END TRANSACTION;"]
        for prop in properties:
            if prop['name'] == 'TMODE':
                if prop['value'] == 'ANSI':
                    logging.info("ANSI mode.")
                    pre_query = [";"]
                    post_query = ["COMMIT WORK;"]
    
    else:
        logging.info("AUTOCOMMIT MODE.")
        logging.info("No pre- and post-query.")
    logging.info(SEP)

    # Recipe function param
    debug = False
    if debug:
    	logging.info(SEP)
    	logging.info('DSS Function:')
    	logging.info(pp.pformat(dss_function))
    	logging.info(SEP)

    logging.info(SEP)
    logging.info('get_recipe_config():')
    logging.info(pp.pformat(recipe_config))
    logging.info(SEP)


    # VALIB     
    dss_function = recipe_config.get('function', None)
    if dss_function and 'function_type' in dss_function and dss_function['function_type'] == "valib":
        dataiku_valib_execution(dss_function, connections, connectionName, executor, autocommit, pre_query, post_query, output_table_names)
        return

    # output dataset
    try:
        outputTable = outputtableinfo(output_dataset.get_location_info()['info'], main_output_name,
                                  recipe_config or {})
    except Exception as error:
        raise RuntimeError("""Error obtaining connection settings for output table."""                           
                           """ This plugin only supports Teradata tables.""")

    # Handle dropping of output tables.
    if dss_function.get('dropIfExists', False):
        logging.info("Preparing to drop tables.")
        drop_query = dropTableStatement(outputTable)
        
        logging.info(SEP)
        logging.info("DROP query:")
        logging.info(drop_query)
        logging.info(SEP)
        try:
            # dataiku's query_to_df's pre_query parameter seems to not work. This is a work-around to ensure that the 
            # "START TRANSACTION;" block applies for non-autocommit TERA mode connections.
            if not autocommit: 
                executor.query_to_df(pre_query)
            executor.query_to_df(drop_query, post_queries=post_query)
        except Exception as e:
            logging.info(e)
        
        # Drop other output tables if they exist.
        drop_all_query = getDropOutputTableArgumentsStatements(dss_function.get('output_tables', []))
        
        logging.info(SEP)
        logging.info('Drop ALL Query:')
        logging.info(drop_all_query)
        logging.info(SEP)
           
        for drop_q in drop_all_query:
            # dataiku's query_to_df's pre_query parameter seems to not work. This is a work-around to ensure that the 
            # "START TRANSACTION;" block applies for non-autocommit TERA mode connections.
            if not autocommit:
                executor.query_to_df(pre_query)
            executor.query_to_df(drop_q, post_queries=post_query)



    # Create new query based on open ended approach
    sql_generator = OpenEndedQueryGenerator(outputTable.tablename, recipe_config, verbose=True)
    logging.info(SEP)
    logging.info("OpenEndedQueryGenerator query:")
    my_query = sql_generator.create_query()
    logging.info(my_query)
    logging.info(SEP)

        
    # Detect error
    try:
        # dataiku's query_to_df's pre_query parameter seems to not work. This is a work-around to ensure that the 
        # "START TRANSACTION;" block applies for non-autocommit TERA mode connections.
        if not autocommit:
            executor.query_to_df(pre_query)
        executor.query_to_df(my_query, post_queries=post_query)
    except Exception as error:
        err_str = str(error)
        index = err_str.index("[Teradata Database]")
        if index != -1:
            err_str = err_str[index:]
        raise RuntimeError(err_str)

    logging.info('Moving results to output...')

    # Call method for mapping Teradata types to the Dataiku types needed
    set_schema_from_vantage(outputTable.tablename, output_dataset, executor, post_query, autocommit, pre_query)

    # Additional Tables
    outtables = dss_function.get('output_tables', [])
    if(outtables != []):
        tableCounter = 1
        logging.info('Working on output tables')
        logging.info(get_output_names_for_role('main'))
        logging.info(outtables)
        for table in outtables:
            if table.get('value') != '' and table.get('value') != None:
                # try:
                logging.info('Table')
                logging.info(table)
                #Need to change this to max of split in order for multiple database or no-database table inputs
                #Change below might fix issue 4 of Jan 4 2018 for Nico. For non-drop tables
                try:
                    main_output_name2 = list(filter(lambda out_dataset: out_dataset.split('.')[len(out_dataset.split('.'))-1] == table.get('value').split('.')[len(table.get('value').split('.'))-1].strip('\"'),get_output_names_for_role('main')))[0]
                except Exception as error:
                    # logging.info(error.message)                    
                    raise RuntimeError('Unable to find an output dataset for '+table.get('value')+ 'It may not exist as an output Dataset: '+table.get('value')+"\n\Runtime Error:"+ error.message)
                logging.info('Output name 2')
                logging.info(main_output_name2)
                output_dataset2 =  dataiku.Dataset(main_output_name2)   
                # logging.info("od2 logging.infoer")
                tableNamePrefix = output_dataset2.get_location_info(sensitive_info=True)['info'].get('connectionParams').get('namingRule').get('tableNameDatasetNamePrefix')
                if tableNamePrefix != None or tableNamePrefix != '':
                    logging.info('Table prefix is not empty:' + tableNamePrefix)
                # except:
                #     #Need to change this error
                #     logging.info('Error: Dataset for' + table.get('name') + ' not found')  
                #     raise Value  

                # Call method for mapping Teradata types to the Dataiku types needed
                set_schema_from_vantage(outputTable.tablename, output_dataset2, executor, post_query, autocommit, pre_query)

                tableCounter += 1

    logging.info('Complete!')  


# Uncomment end