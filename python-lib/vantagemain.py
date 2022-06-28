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

import dataiku
from dataiku import Dataset
from dataiku.customrecipe import *
from dataiku.core.sql import SQLExecutor2

# Import plugin libs
from querybuilderfacade import *
from inputtableinfo import *
from outputtableinfo import *

# SKS : Import 
from open_ended_query_generator import OpenEndedQueryGenerator
from vantage_schema import set_schema_from_vantage

def vantageDo():
    """
    Takes the parameters set by the user from the UI, creates the query, and then executes it.
    """
    # Formatting options.
    SEP_LENGTH = 80
    SEP = "=" * SEP_LENGTH
    
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
    
    # Connection properties.
    # TODO: Handle Input and Output Table connection properties.
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
    dss_function = get_recipe_config().get('function', None)
    pp = pprint.PrettyPrinter(indent=4)
    debug = False
    if debug:
    	logging.info(SEP)
    	logging.info('DSS Function:')
    	logging.info(pp.pformat(dss_function))
    	logging.info(SEP)

    logging.info(SEP)
    logging.info('get_recipe_config():')
    logging.info(pp.pformat(get_recipe_config()))
    logging.info(SEP)

    # output dataset
    try:
        outputTable = outputtableinfo(output_dataset.get_location_info()['info'], main_output_name,
                                  get_recipe_config() or {})
    except Exception as error:
        raise RuntimeError("""Error obtaining connection settings for output table."""                           
                           """ This plugin only supports Teradata tables.""")


    # input datasets
    try:
        main_input_names = get_input_names_for_role('main')
        inputTables = []
        for inputname in main_input_names:
            inconnectioninfo = dataiku.Dataset(inputname).get_location_info()['info']
            inTable = inputtableinfo(inconnectioninfo, inputname, dss_function)
            inputTables.append(inTable)

    except Exception as error:
        raise RuntimeError("""Error obtaining connection settings from one of the input tables."""                           
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



    # SKS: Create new query based on open ended approach
    sql_generator = OpenEndedQueryGenerator(outputTable.tablename, get_recipe_config(), verbose=True)
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
        err_str_list = err_str.split(" ")
        # trying to shorten the error for the modal in front-end
        if len(err_str_list) > 15:
            logging.info(SEP)
            logging.info(error)
            logging.info(SEP)
            new_err_str = err_str_list[:15]
            new_err_str.append("\n\n")
            new_err_str.append("...")
            new_err_str = " ".join(new_err_str)
            raise RuntimeError(new_err_str)
        else:
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
                # print("od2 printer")
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