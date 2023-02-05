
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

from vantage_schema import *
import pprint
import dataiku
import logging
from dataiku import pandasutils as pdu
import pandas as pd
from dataiku import Dataset
from dataiku.customrecipe import *
from dataiku.core.sql import SQLExecutor2

# Valib functions
from valib_executor import *
from query_engine_wrapper import QueryEngineWrapper


class ValibQueryEngineWrapper(QueryEngineWrapper):
    def __init__(self, executor, autocommit, pre_query, post_query):
        self.executor = executor
        self.autocommit = autocommit
        self.pre_query = None
        self.post_query = post_query
    def execute(self, query_string):
        if not self.autocommit:
            self.executor.query_to_df(self.pre_query)
        logging.info("VAL QUERY=", query_string)
        return self.executor.query_to_df(query = query_string, post_queries=self.post_query)
    def iteratable(self, result):
        return result.iterrows()
    def row_value(self, row, column_name):
        return row[1][column_name]
    def get_dataframe(datasetName):
        return dataiku.Dataset(datasetName).get_dataframe()


def dataiku_valib_execution(dss_function, connections, connectionName, executor, autocommit, pre_query, post_query, output_table_names):
    dss_function["val_location"] = get_val_location(connections, connectionName)
    json_contents = json.loads(dss_function["json_contents"])
    valib_query_wrapper = ValibQueryEngineWrapper(executor, autocommit, pre_query, post_query)
    valib_execution(json_contents, dss_function, dropIfExists=dss_function.get('dropIfExists', False), valib_query_wrapper = valib_query_wrapper)
    for output_table in output_table_names:
        outputDataset = dataiku.Dataset(output_table["datasetName"])
        outputExecutor = SQLExecutor2(dataset=outputDataset)   
        set_schema_from_vantage(output_table["table"], outputDataset, executor, post_query, autocommit, pre_query, outputDatabaseName=output_table.get("schema", ""))
    return

def get_val_location(connections, connectionName):
    if connectionName not in connections:
        return 'VAL'
    val_location = None
    if "dkuProperties" in connections[connectionName]['params']:
        dkuProperties = connections[connectionName]['params']['dkuProperties']
        for item in dkuProperties:
            if item['name'] == "VAL_DATABASE":
                val_location = item['value']
                break
    if not val_location:
        raise Exception('VAL_DATABASE is not defined in the connection')
    return val_location





