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
from valib_transform import *

def execute(recipe_config, valib_query_wrapper=None):
    # Sigmoid

    lst_sigmoids = []

    columns = []

    num_of_sigmoidbounds = 1

    for i in range(1, 1+num_of_sigmoidbounds):
        nullstyle = recipe_config['sigmoid_nullstyle'+str(i)]
        fillna_value = recipe_config['sigmoid_fillna_value'+str(i)]
        fillna = {'nullstyle' : nullstyle, 'fillna_value' : fillna_value}
        
        style = recipe_config['sigmoid_style'+str(i)]
        
        columns = []
        map_dict = recipe_config['sigmoid_map']
        for key in map_dict:
            # No quotes in key or value
            if ("'" in key) or ('"' in key):
                raise Exception('Invalid Key', key)
            if ("'" in map_dict[key]) or ('"' in map_dict[key]):
                raise Exception('Invalid Value', map_dict[key])
            columns.append({'column_from': key, 'column_to': map_dict[key]})

        sigmoid_input = {"columns": columns, "style": style, "fillna": fillna}

        lst_sigmoids.append(sigmoid_input)

    sigmoid_list = []
    for a_sigmoid in lst_sigmoids:
        # for columns
        lst_columns = []
        style = a_sigmoid['style']
        for a_column in a_sigmoid['columns']:
            if a_column['column_to'] != "":
                columns = str(a_column['column_from']) +"/"+ str(a_column['column_to'])
            lst_columns.append(columns)

        # for fillna
        nullstyle = a_sigmoid['fillna']['nullstyle']
        fillna_value = a_sigmoid['fillna']['fillna_value']

        sigmoid_dict = {"columns": lst_columns, "style": style, "nullstyle": nullstyle, "fillna_value": fillna_value}
        sigmoid_list.append(sigmoid_dict)



    # sigmoid={sigmoidstyle(logit), columns(sepal_length/sl, sepal_width/sw, petal_length/pl, petal_width/pw)}

    function_list = []

    for value in sigmoid_list:
        columns = ",".join(value['columns'])
        style = value['style']
        nullstyle = value['nullstyle']
        fillna_value = value['fillna_value']

        if nullstyle == "literal":
            sigmoid = "{sigmoidstyle("+str(style)+"), columns("+str(columns)+"), nullstyle("+str(nullstyle)+", "+str(fillna_value)+")}"
        elif nullstyle == "None":
            sigmoid = "{sigmoidstyle("+str(style)+"), columns("+str(columns)+")}"
        else: 
            sigmoid = "{sigmoidstyle("+str(style)+"), columns("+str(columns)+"), nullstyle("+str(nullstyle)+")}"

        function_list.append(sigmoid)

    return execute_transform(recipe_config, 'sigmoid', function_list, "sigmoid_", valib_query_wrapper=valib_query_wrapper)


