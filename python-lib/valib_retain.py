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
from valib_transform import *

def execute(recipe_config, valib_query_wrapper=None):
    # retain

    lst_retains = []

    columns = []


    num_of_retainbounds = 1

    for i in range(1, 1+num_of_retainbounds):
        
        columns = []
        map_dict = recipe_config['retain_map']
        for key in map_dict:
            # No quotes in key or value
            if ("'" in key) or ('"' in key):
                raise Exception('Invalid Key', key)
            if ("'" in map_dict[key]) or ('"' in map_dict[key]):
                raise Exception('Invalid Value', map_dict[key])
            columns.append({'column_from': key, 'column_to': map_dict[key]})
            

        retain_input = {"columns": columns}

        lst_retains.append(retain_input)

    retain_list = []
    columns = ""
    for a_retain in lst_retains:
        # for columns
        lst_columns = []
        for a_column in a_retain['columns']:
            if a_column['column_to'] != "":
                columns = str(a_column['column_from']) +"/"+ str(a_column['column_to'])
            lst_columns.append(columns)


        retain_dict = {"columns": lst_columns}
        retain_list.append(retain_dict)



    function_list = []

    # retain={columns(accounts, Feb)}{columns(Jan/january)}{columns(Mar/march, Apr/april), datatype(bigint)}

    for value in retain_list:
        columns = ",".join(value['columns'])

        retain = "{columns("+str(columns).replace("'", '"')+")}"
     
        function_list.append(retain)


    return execute_transform(recipe_config, 'retain', function_list, "retain_", valib_query_wrapper=valib_query_wrapper)


