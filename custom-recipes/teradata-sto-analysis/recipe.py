# -*- coding: utf-8 -*-
'''
Copyright © 2018 by Teradata.
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
# To finish creating your custom recipe from your original PySpark recipe, you need to:
#  - Declare the input and output roles in recipe.json
#  - Replace the dataset names by roles access in your code
#  - Declare, if any, the params of your custom recipe in recipe.json
#  - Replace the hardcoded params values by acccess to the configuration map

# See sample code below for how to do that.
# The code of your original recipe is included afterwards for convenience.
# Please also see the "recipe.json" file for more information.

# import the classes for accessing DSS objects from the recipe
import dataiku
# Import the helpers for custom recipes
from dataiku.customrecipe import *
import logging

#CALL Subprocess for BTEQ script
from subprocess import call

from auth import *
from pynbExtractor import *
from re import search
from shutil import copyfile

#import nbformat
#from nbconvert import PythonExporter


#def convertNotebook(notebookPath, modulePath):
#    with open(notebookPath) as fh:
#        nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)
#    exporter = PythonExporter()
#    source, meta = exporter.from_notebook_node(nb)
#    with open(modulePath, 'w+') as fh:
#        fh.writelines(source)

# Inputs and outputs are defined by roles. In the recipe's I/O tab, the user can associate one
# or more dataset to each input and output role.
# Roles need to be defined in recipe.json, in the inputRoles and outputRoles fields.

# To  retrieve the datasets of an input role named 'input_A' as an array of dataset names:
input_A_names = get_input_names_for_role('main')
# The dataset objects themselves can then be created like this:
input_A_datasets = [dataiku.Dataset(name) for name in input_A_names]

# To  retrieve the datasets of an input role named 'input_B_names' as an array of dataset names:
script_role = 'language_scripts'
input_B_names = get_input_names_for_role(script_role)
if not input_B_names:
    # backward compatible support
    script_role = 'sto_scripts'
    input_B_names = get_input_names_for_role(script_role)

# The dataset objects themselves can then be created like this:
input_B_datasets = [dataiku.Dataset(name) for name in input_B_names]

# For outputs, the process is the same:
output_A_names = get_output_names_for_role('main')
output_A_datasets = [dataiku.Dataset(name) for name in output_A_names]




# The configuration consists of the parameters set up by the user in the recipe Settings tab.

# Parameters must be added to the recipe.json file so that DSS can prompt the user for values in
# the Settings tab of the recipe. The field "params" holds a list of all the params for wich the
# user will be prompted for values.

# The configuration is simply a map of parameters, and retrieving the value of one of them is simply:
# my_variable = get_recipe_config()['parameter_name']

# For optional parameters, you should provide a default value in case the parameter is not present:
# my_variable = get_recipe_config().get('parameter_name', None)

# config variable
function_config = get_recipe_config().get('function', None)

# Note about typing:
# The configuration of the recipe is passed through a JSON object
# As such, INT parameters of the recipe are received in the get_recipe_config() dict as a Python float.
# If you absolutely require a Python int, use int(get_recipe_config()["my_int_param"])


#############################
# Your original recipe
#############################

# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
import os
from dataiku import pandasutils as pdu
from dataiku.core.sql import SQLExecutor2
from verifyTableColumns import *


def executor_query(executor, query_string):
    logging.info('Query : ' + query_string)
    return executor.query_to_df(query_string)

def executor_query2(executor, query_string, pre_queries):
    logging.info('PreQuery : ', pre_queries)
    logging.info('Query : ', query_string)
    return executor.query_to_df(query_string, pre_queries)


#DataIku Managed Folder Handler (Specifically language_scripts as of now)
handle = dataiku.Folder(script_role) if input_B_names else None


logging.info('Getting STO Database')
def sto_database():
    #result =  getConnectionParamsFromDataset(output_A_datasets[0]).get('defaultDatabase', "");
    client = dataiku.api_client()
    connections = client.list_connections()
    connectionName = input_A_datasets[0].get_location_info()['info']['connectionName']
    result = None
    if "dkuProperties" in connections[connectionName]['params']:
        dkuProperties = connections[connectionName]['params']['dkuProperties']
        for item in dkuProperties:
            if item['name'] == "STO_DATABASE":
                result = item['value']
                break
    if not result:
        raise Exception('Error: Missing database search path for SCRIPT. To use this recipe, specify first a database name for the STO_DATABASE custom property in your connection settings. ')
    return result



def getConnectionDetails(dataset=input_A_datasets[0]):
    return getConnectionParamsFromDataset(input_A_datasets[0]);


properties = getConnectionDetails(input_A_datasets[0]).get('properties')
autocommit = getConnectionDetails(input_A_datasets[0]).get('autocommitMode')
tmode = ''

for prop in properties:
    if prop['name'] == 'TMODE' and prop['value'] == 'TERA':
        #Detected TERA
        logging.info('I am in TERA MODE')
        tmode = 'TERA'
        stTxn = 'BEGIN TRANSACTION;'
        edTxn = 'END TRANSACTION;'

    elif prop['name'] == 'TMODE' and prop['value'] == 'ANSI':
        #Detected ANSI
        logging.info('I am in ANSI MODE')
        tmode = 'ANSI'
        stTxn = ';'
        edTxn = 'COMMIT WORK;'

empty_table = input_A_datasets[0]
#SQL Executor
executor = SQLExecutor2(dataset=empty_table)


defaultDB = sto_database()
#if sto_database(input_A_datasets[0]) != sto_database():
#    raise RuntimeError('Input dataset and output dataset have different connection details')

output_location = output_A_datasets[0].get_location_info()['info']

logging.info('Getting Function Config')
scriptAlias = function_config.get('script_alias', '')
scriptFileName = function_config.get('script_filename', '')
scriptLocation = function_config.get('script_location', '')
searchPath = sto_database()
outputTable = output_A_datasets[0].get_location_info()['info'].get('table', '')
partitionOrHash = function_config.get('partitionOrHash', '')


performFileLoad = True

cleanupFiles = []

#Script Location for main script
if(scriptLocation == 'sz'):
    scriptFileLocation = function_config.get('script_filelocation')
elif 'czp' == scriptLocation:
    if '..' in scriptLocation:
        raise Exception("Illegal Path", scriptLocation)
    scriptFileLocation = pynbDestinationPath(scriptFileName)
    writePythonNotebookToResourceFolder(output_A_names[0].split('.')[0], scriptFileName)
    scriptFileName = scriptFileName.replace("'", "")
    scriptFileName = scriptFileName.replace(" ", "")
# notebook conversion will be available in a future release
elif 'cz' == scriptLocation:
    scriptFileLocation = handle.file_path(scriptFileName)
    # We do not support python notebooks in this release
    #    if scriptFileLocation.endswith(".ipynb"):
    #        logging.info("Convert Notebook to Python Script")  
    #        logging.info("Input Notebook", scriptFileName, scriptFileLocation)  
    #        pythonScript = scriptFileLocation.replace(".ipynb", ".py")
    #        convertNotebook(scriptFileLocation, pythonScript)
    #        scriptFileLocation = pythonScript
    #        scriptFileName = scriptFileName.replace(".ipynb", ".py")
    #        logging.info("Output Python", scriptFileName, scriptFileLocation)  
    #        cleanupFiles.append(scriptFileLocation)
else:
    performFileLoad = False
    


scriptLocation = scriptLocation[:2]

commandType = function_config.get('command_type', '')
returnClause = ', '.join((x.get('name', '') + ' ' + x.get('type', ''))
                         for x in function_config.get('return_clause', []))
scriptArguments = ', '.join(x.get('value', '')
                            for x in function_config.get('arguments', []))
additionalFiles = function_config.get('files')




def getHashClause(hasharg):
    return hasharg and ('\n             HASH BY {hasharg}'.format(hasharg=hasharg))
def getPartitionClause(partitionarg):
    return partitionarg and ('\n             PARTITION BY {partitionarg}'\
                             .format(partitionarg=partitionarg))
def getOrderClause(orderarg):
    return orderarg and ('\n             ORDER BY {orderarg}'.format(orderarg=orderarg))

def getLocalOrderClause(localorderarg):
    return localorderarg and ('\n             LOCAL ORDER BY {localorderarg}'.format(localorderarg=localorderarg))

def getAdditionalClauses(arg):
    return arg and ('\n{arg}'.format(arg=arg))

def getSelectInstalledFileQuery(databasename, fileAlias):
    return """select * from dbc.tables
where databasename = {dataset}
and TableName = {table}
and TableKind = 'Z';""".format(dataset=verifyDatabaseName(databasename, single_quotes=True), table=verifyTableName(fileAlias, single_quotes=True))

def verifyReturnClause(returnClause):
    # return clause should not have any quotes
    if returnClause and ('"' not in returnClause) and ("'" not in returnClause):
        return returnClause
    else:
        raise Exception('Illegal Return clause', returnClause)

def verifyPartitionClause(partitionbycolumns):
    # verify that each column name is valid
    if(partitionOrHash == 'part'):
        partitionClause = []
        for d in partitionbycolumns:
            if not d["value"]:
                continue
            partitionClause.append(verifyColumnName(d["value"]))
        partitionClause = ", ".join(partitionClause)
        partitionClause = getPartitionClause(partitionClause)
    else:
        partitionClause = ''
    return partitionClause
    
def verifyOrderClause(partitionorderbycolumns):
    # verify that each column name is valid
    if(partitionOrHash == 'part'):
        orderClause = []
        for d in partitionorderbycolumns:
            if not d["value"]:
                continue
            sequence = "ASC"
            if d["type"] == "Descending":
                sequence = "DESC"
            orderClause.append(verifyColumnName(d["value"]) + " " + sequence)
        orderClause = ", ".join(orderClause)
        orderClause = getOrderClause(orderClause)
    else:
        orderClause = '' 
    return orderClause

def verifyHashClause(partitionbycolumns):
    # verify that each column name is valid
    if(partitionOrHash == 'hash'):
        hashClause = []
        for d in function_config.get('partitionbycolumns', ''):
            if not d["value"]:
                continue
            hashClause.append(verifyColumnName(d["value"]))
        hashClause = ", ".join(hashClause)
        hashClause = getHashClause(hashClause)
    else:
        hashClause = ''
    return hashClause
    
def verifyLocalOrderClause(partitionorderbycolumns):
    # verify that each column name is valid
    if(partitionOrHash == 'hash'):
        localOrderByClause = []
        for d in function_config.get('partitionorderbycolumns', ''):
            if not d["value"]:
                continue
            sequence = "ASC"
            if d["type"] == "Descending":
                sequence = "DESC"
            localOrderByClause.append(verifyColumnName(d["value"]) + " " + sequence)
        localOrderByClause = ", ".join(localOrderByClause)
        localOrderByClause = getLocalOrderClause(localOrderByClause)
    else:
        localOrderByClause = '' 
    return localOrderByClause

def verifyWhereClause(whereClause):
    # No quotes single or double or semicolons
    if whereClause != "":
        if (";" in whereClause) or ("'" in whereClause) or ('"' in whereClause):
            raise Exception('Invalid Clause', whereClause)
        else:
            whereClause = "WHERE " + whereClause
    return whereClause

def verifyOnClause(inputs):
    onClause = []
    for d in inputs:
        if d.get("value", ""):
            onClause.append(d["value"])
    if onClause:
        onClause = ",".join(onClause)
    else:
        onClause = "*"
    if not onClause == "*":
        onClause_InputList = onClause.split(",")
        onClause_OutputList = []
        for clause in onClause_InputList:
            onClause_OutputList.append(verifyColumnName(clause))
        onClause = ",".join(onClause_OutputList)
    return onClause

def verifyInputTable(inputTable):
    inputTable = verifyTableName(inputTable)
    inputSchema = input_A_datasets[0].get_config()['params']['schema']
    if inputSchema != "":
        inputTable = inputSchema + "." + inputTable
    else:
        # now check if there is a default database
        defaultDatabase =  getConnectionParamsFromDataset(input_A_datasets[0]).get('defaultDatabase', "");
        if defaultDatabase != "":
            inputTable = defaultDatabase + "." + inputTable
    return inputTable


def verifySelectClause(output_all, return_clause):
    # Vverify all column names are valid
    selectClause = "*"
    if not output_all:
        selectClause = []
        for d in return_clause:
            if d.get("name", "") and d.get("output", False):
                selectClause.append(verifyColumnName(d["name"]))
        if selectClause:
            selectClause = ",".join(selectClause)
        else:
            selectClause = "*"
    return selectClause

def verifyScriptCommand():
    script_command = ''
    # search path should have no quotes
    if ('"' in searchPath) or ("'" in searchPath):
        raise Exception('Illegal Search Path', searchPath)
    # script file name should have no quotes
    if ('"' in scriptFileName) or ("'" in scriptFileName):
        raise Exception('Illegal Script File Name', scriptFileName)
    # script arguments should have no quotes
    if ('"' in scriptArguments) or ("'" in scriptArguments):
        raise Exception('Illegal Script Arguments', scriptArguments)
    if commandType != 'r':
        script_command = """'export PATH; tdpython3 ./"""+searchPath+"""/"""+scriptFileName+""" """+scriptArguments+"""'"""
    elif commandType == 'r':
        script_command = """'R --vanilla ./"""+searchPath+"""/"""+scriptFileName+""" """+scriptArguments+"""'"""
    return script_command



partitionbycolumns = function_config.get('partitionbycolumns', '')
partitionorderbycolumns = function_config.get('partitionorderbycolumns', '')


logging.info('Building STO Script Command')

logging.info("""Script Command: """+verifyScriptCommand())

# select query
logging.info('Building Database Query')
databaseQuery = 'DATABASE {database};'.format(database=sto_database())
print("""Database Query: """+databaseQuery)
executor_query(executor, databaseQuery)
logging.info('Build Session SearchUIFDBPath Query')
setSessionQuery = 'SET SESSION SEARCHUIFDBPATH = {searchPath};'.format(searchPath=searchPath)
logging.info("""Set Session Query: """ + setSessionQuery)
etQuery = 'COMMIT WORK;'

#File Related:

removeFileQuery = """CALL SYSUIF.REMOVE_FILE('""" + scriptAlias + """',1);"""
logging.info('Building Script installation query')
installFileQuery = """CALL SYSUIF.INSTALL_FILE('""" + escape(scriptAlias) + """','""" + escape(scriptFileName) + """','"""+escape(scriptLocation)+"""!"""+escape(scriptFileName)+"""');"""
replaceFileQuery = """CALL SYSUIF.REPLACE_FILE('""" + escape(scriptAlias) + """','""" + escape(scriptFileName) + """','"""+escape(scriptLocation)+"""!"""+escape(scriptFileName)+"""', 0);"""
scriptDoesExist = """select * from dbc.tables
where databasename = '{searchPath}'
and TableKind = 'Z';""".format(searchPath=searchPath)

#File Copy to DIST
dkuinstalldir = os.environ['DKUINSTALLDIR']
newPath = dkuinstalldir + """/dist/"""+scriptFileName
logging.info(newPath)
# logging.info(replaceFileQuery)
#COPY FILE TEST
if(performFileLoad):
    copyfile(escape(scriptFileLocation.rstrip()), newPath)

#ADDITIONAL FILES
#INSTALL Additional files
logging.info('Building Additional File INSTALLATION/REPLACEMENT')
# installAdditionalFiles = """"""
installAdditionalFilesArray = []
for item in additionalFiles:
    address = item.get('file_address', '').rstrip() if\
        ('s' == item.get('file_location', '')) else handle.file_path(item.get('filename', ''))
    newPath = dkuinstalldir + """/dist/"""+item.get('filename')
    logging.info(newPath)
    # logging.info(replaceFileQuery)
    logging.info(address)
    #COPY FILE TEST
    copyfile(address, newPath)
    if item.get('replace_file'):
        # installAdditionalFiles = installAdditionalFiles + """\nCALL SYSUIF.REPLACE_FILE('""" + item.get('file_alias') + """','""" + item.get('filename') + """','"""+item.get('file_location')+item.get('file_format')+"""!"""+address+"""',0);"""
        query_check = getSelectInstalledFileQuery(defaultDB,item.get('file_alias'))
    
        tableCheck = executor_query(executor, query_check)
        logging.info(tableCheck)
        logging.info(tableCheck.shape)
        if(tableCheck.shape[0] < 1):
            logging.info("""File Alias:"""+ item.get('file_alias'))
            logging.info('Was not able to find the file in the table list. Attempting to use INSTALL_FILE')        
            installAdditionalFilesArray.append("""\nCALL SYSUIF.INSTALL_FILE('""" + item.get('file_alias') + """','""" + item.get('filename') + """','"""+item.get('file_location')+item.get('file_format')+"""!"""+item.get('filename')+"""');""")
        else:    
            logging.info("""File Alias:"""+ item.get('file_alias'))
            logging.info('Was able to find the file in the table list. Attempting to use REPLACE_FILE')                
            installAdditionalFilesArray.append("""\nCALL SYSUIF.REPLACE_FILE('""" + item.get('file_alias') + """','""" + item.get('filename') + """','"""+item.get('file_location')+item.get('file_format')+"""!"""+item.get('filename')+"""',0);""")
    else:
        installAdditionalFilesArray.append("""\nCALL SYSUIF.INSTALL_FILE('""" + item.get('file_alias') + """','""" + item.get('filename') + """','"""+item.get('file_location')+item.get('file_format')+"""!"""+item.get('filename')+"""');""")
logging.info("""Additional Files Installation Query/ies: """)
logging.info(installAdditionalFilesArray)

#MOVE ADDITIONAL FILES


logging.info(output_A_names[0])

# Gather inputs to generate onClause
inputs = function_config.get('inputs', "")


whereClause = function_config.get('where', "")

# gather ouputs to build selectClause
return_clause = function_config.get('return_clause', "")
output_all = function_config.get('outputAll', True)


# Prefix the input table with the correct database
inputTable = function_config.get('input_table')



STOQuery = """SELECT {selectClause}
FROM SCRIPT (ON (SELECT {onClause} FROM {inputTable} {whereClause}){hashClause}{localOrderClause}{partitionClause}{orderClause}
             SCRIPT_COMMAND({script_command})
             RETURNS ('{returnClause}')
            );""".\
            format(inputTable=verifyInputTable(inputTable),
                   outputTable=outputTable, # Not verified as not user specificed, instead it is from Dataiku output data set information
                   selectClause=verifySelectClause(output_all, return_clause),
                   onClause=verifyOnClause(inputs),
                   whereClause=verifyWhereClause(whereClause),
                   script_command=verifyScriptCommand(),
                   hashClause=verifyHashClause(partitionbycolumns),
                   partitionClause=verifyPartitionClause(partitionbycolumns),
                   orderClause=verifyOrderClause(partitionorderbycolumns),
                   localOrderClause=verifyLocalOrderClause(partitionorderbycolumns),
                   returnClause=verifyReturnClause(returnClause))

def getSelectTableQuery(databasename, fileAlias):
    return """select * from dbc.tables
where databasename = '{dataset}'
and TableName = '{table}'
and TableKind = 'T';""".format(dataset=databasename, table=fileAlias)

def database():
    # for now, database name = db user name
    return sto_database()
    

#File Loading
if(performFileLoad):
    if function_config.get("replace_script"):
        logging.info('performing replacefile')
        query_check = getSelectInstalledFileQuery(defaultDB, scriptAlias)
  
        tableCheck = executor_query(executor, query_check)
        logging.info('Checking table list for previously installed files')
        logging.info(tableCheck)
        logging.info(tableCheck.shape)
        if(tableCheck.shape[0] < 1):
            logging.info('Was not able to find the file in the table list. Attempting to use INSTALL_FILE')
            if autocommit:
                logging.info('Auto commit is true')
                executor_query2(executor, installFileQuery, [databaseQuery, setSessionQuery])
            else:
                logging.info('Auto commit is false')
                executor_query2(executor, edTxn, [stTxn, databaseQuery, setSessionQuery, installFileQuery])
        else:    
            logging.info('Was able to find the file in the table list. Attempting to use REPLACE_FILE')
            if autocommit:
                logging.info('Auto commit is true')
                executor_query2(executor, replaceFileQuery,[databaseQuery, setSessionQuery])
            else:
                logging.info('Auto commit is false')
                executor_query2(executor, edTxn,[stTxn, databaseQuery, setSessionQuery, replaceFileQuery])
    else:
        logging.info('performing installfile')
        executor_query2(executor, edTxn,[stTxn, databaseQuery, setSessionQuery, installFileQuery])

if(installAdditionalFilesArray != []):
    logging.info('Installing additional files...')
    if autocommit:
        placeholderQuery = "SELECT 1;" #Placeholder so that a query is still executed.
        executor_query2(executor, placeholderQuery,[databaseQuery,setSessionQuery]+installAdditionalFilesArray);
    else:
        executor_query2(executor, edTxn,[stTxn, databaseQuery, setSessionQuery]+installAdditionalFilesArray)


    
# Recipe outputs                                                          
logging.info('setSessionQuery')
logging.info(setSessionQuery)
logging.info('replaceFileQuery')
logging.info(replaceFileQuery)
logging.info('Executing SELECT Query...')
logging.info(STOQuery)
selectResult = executor_query2(executor, STOQuery,[databaseQuery, setSessionQuery])
logging.info('Moving results to output...')
pythonrecipe_out = output_A_datasets[0]
pythonrecipe_out.write_with_schema(selectResult)
if cleanupFiles:
    # deleting autogenerated files
    for filePath in cleanupFiles:
        os.remove(filePath)
logging.info('Complete!')  
