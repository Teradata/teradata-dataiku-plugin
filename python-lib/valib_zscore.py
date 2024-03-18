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
    # zscore

    lst_zscores = []

    columns = []


    num_of_zscorebounds = 1

    for i in range(1, 1+num_of_zscorebounds):
        nullstyle = recipe_config['zscore_nullstyle'+str(i)]
        fillna_value = recipe_config.get('zscore_fillna_value'+str(i),0)
        fillna = {'nullstyle' : nullstyle, 'fillna_value' : fillna_value}
        
        columns = []
        map_dict = recipe_config['zscore_map']
        if type(map_dict) == str:
            map_dict = string_param_to_dict(map_dict)
        for key in map_dict:
            # No quotes in key or value
            if ("'" in key) or ('"' in key):
                raise Exception('Invalid Key', key)
            if ("'" in map_dict[key]) or ('"' in map_dict[key]):
                raise Exception('Invalid Value', map_dict[key])
            columns.append({'column_from': key, 'column_to': map_dict[key]})

        zscore_input = {"columns": columns, "fillna": fillna}
        lst_zscores.append(zscore_input)


    zscore_list = []
    for a_zscore in lst_zscores:
        # for columns
        lst_columns = []
        for a_column in a_zscore['columns']:
            if a_column['column_to'] != "":
                columns = str(a_column['column_from']) +"/"+ str(a_column['column_to'])
            lst_columns.append(columns)

        # for fillna
        nullstyle = a_zscore['fillna']['nullstyle']
        fillna_value = a_zscore['fillna']['fillna_value']

        zscore_dict = {"columns": lst_columns, "nullstyle": nullstyle, "fillna_value": fillna_value}
        zscore_list.append(zscore_dict)

    # zscore={columns(Jan/january, Apr/april), nullstyle(mode)}
    function_list = []

    for value in zscore_list:
        columns = ",".join(value['columns'])
        nullstyle = value['nullstyle']
        fillna_value = value['fillna_value']

        if nullstyle == "literal":
            zscore = "{columns("+str(columns)+"), nullstyle("+str(nullstyle)+", "+str(fillna_value)+")}"
        elif nullstyle == "None":
            zscore = "{columns("+str(columns)+")}"
        else: 
            zscore = "{columns("+str(columns)+"), nullstyle("+str(nullstyle)+")}"
        
        function_list.append(zscore)


    return execute_transform(recipe_config, 'zscore', function_list, "zscore_", valib_query_wrapper=valib_query_wrapper)


