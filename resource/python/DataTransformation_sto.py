import dataiku
import json
import os
import logging

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

import sys
sys.path.append('../../python-lib')
import auth


FUNCTION_CATEGORY="Data Transformation"

def sto_database(inputdataset):
    if inputdataset == None:
        return ''
    connections = {}
    connectionName = inputdataset.get_location_info()['info']['connectionName']
    connections = auth.addConnection(connections, connectionName)
    result = None
    if "dkuProperties" in connections[connectionName]['params']:
        dkuProperties = connections[connectionName]['params']['dkuProperties']
        for item in dkuProperties:
            if item['name'] == "STO_DATABASE":
                result = item['value']
                break
    if not result:
        return ''
    return result


def get_auth_token(inputdataset):
    if inputdataset == None:
        return ''
    connections = {}
    connectionName = inputdataset.get_location_info()['info']['connectionName']
    connections = auth.addConnection(connections, connectionName)
    result = None
    if "dkuProperties" in connections[connectionName]['params']:
        dkuProperties = connections[connectionName]['params']['dkuProperties']
        for item in dkuProperties:
            if item['name'] == "Auth_token":
                result = item['value']
                break
    if not result:
        return ''
    return result
    

def getCurrentConnectionName(inputDataset):
    #input Dataset is the output of dataiku.Dataset("dataset name"
    return inputDataset.get_location_info().get('info', {}).get('connectionName',
                                                                '')

def getConnectionParams(name):
    client = dataiku.api_client()
    mydssconnection = client.get_connection(name)
    return mydssconnection.get_definition().get('params', {})

def getConnectionParamsFromDataset(inputDataset):
    return inputDataset.get_location_info(sensitive_info=True)['info']

# paylaod is sent from the javascript's callPythonDo()
# config and plugin_config are the recipe/dataset and plugin configured values
# inputs is the list of input roles (in case of a recipe)
def do(payload, config, plugin_config, inputs):
    inputDataSets = []
    # print(inputtablename)
    connection = {}
    project = ''
    inputFolderLocation = None
    inputdataset = None
    for input in inputs:
        if(input.get('role') == 'main'):
            inputtablename = input['fullName'].split('.')[1]
            project = input['fullName'].split('.')[0]
            inputDataSets.append(inputtablename)
            if not connection:
                inputdataset = dataiku.Dataset(inputtablename)
                connection = getConnectionParamsFromDataset(inputdataset).get('connectionParams', {})
        else:
            inputfoldername = input['fullName'].split('.')[1]       
            inputFolderLocation =  dataiku.Folder(inputfoldername)

    folderpath = inputFolderLocation.get_path() if inputFolderLocation else ''

    fileList = os.listdir(folderpath) if folderpath else []
    DATA_DIR = os.environ["DIP_HOME"]
    PYNBDIR = "config/ipython_notebooks/"
    pypath = os.path.join(DATA_DIR, PYNBDIR, project)
    pynbList = filter(lambda f: not f.startswith('.'), os.listdir(pypath)) if\
        os.path.exists(pypath) else []

    sto_db = sto_database(inputdataset)

    # Find Vantage Version
    vantage_version = ""
    if inputdataset:
        # Execute query to find out the version and establish if it is Vantage Cloud or not
        executor = dataiku.core.sql.SQLExecutor2(dataset=inputdataset) 
        query_string = "SELECT InfoData FROM DBC.DBCInfoV where InfoKey = 'VERSION'"
        query_results = executor.query_to_df(query_string)
        for row in query_results.iterrows():
            vantage_version = row[1]["InfoData"]
            # This code should be made more robust
            logging.info("teradata_analytic_lib: the pm.versionInfo table returns", vantage_version)
            break

    # Find if Vantage Cloud based on vantage version
    auth_token = get_auth_token(inputdataset)
    is_vantage_cloud = False
    if auth_token:
        is_vantage_cloud = True
        
    return {'inputfolder':folderpath,
            'fileList':fileList,
            'nbList':pynbList,
            'connection': connection,
            'stoDatabase' : sto_db,
            'inputDataSets':inputDataSets ,
            'inputs': inputs,
            'isVantageCloudLake' : is_vantage_cloud,
            'vantageVersion' : vantage_version,
            'auth_token' : auth_token}
