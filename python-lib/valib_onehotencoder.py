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

    # onehotencoder
    lst_designcodes = []

    num_of_designcodebounds = 1

    for i in range(1, 1+num_of_designcodebounds):
        columns = []
        style = recipe_config['onehotencoder_style'+str(i)]
        value = recipe_config['onehotencoder_value'+str(i)]
        
        style = {'style': style, 'value': value}
        
        map_dict = recipe_config['onehotencoder_map']
        for key in map_dict:
            # No quotes in key or value
            if ("'" in key) or ('"' in key):
                raise Exception('Invalid Key', key)
            if ("'" in map_dict[key]) or ('"' in map_dict[key]):
                raise Exception('Invalid Value', map_dict[key])
            columns.append({'column_from': key, 'column_to': map_dict[key]})

        designvalues = recipe_config['onehotencoder_values']
        print("SKS designvalues", designvalues, type(designvalues))
        for design_value in designvalues:
            # No quotes in key or value
            if ("'" in design_value) or ('"' in design_value):
                raise Exception('Invalid Design Value', design_value)
        
        nullstyle = recipe_config['onehotencoder_nullstyle'+str(i)+'']
        if nullstyle == "literal":
            fillna_value = recipe_config['onehotencoder_fillna_value'+str(i)+'']
            designcode_input = {"designvalues": designvalues, "style": style, "columns": columns, "nullstyle" : nullstyle, "fillna_value": fillna_value}

        elif nullstyle == 'None':
            designcode_input = {"designvalues": designvalues, "style": style, "columns": columns}
        
        else:
            fillna_value_empty = None
            designcode_input = {"designvalues": designvalues, "style": style, "columns": columns, "nullstyle" : nullstyle, "fillna_value": fillna_value_empty}
        

        lst_designcodes.append(designcode_input)

    function_list = []

    for a_designcode in lst_designcodes:
        
        designvalues = "designvalues(" + ",".join(a_designcode["designvalues"]) + ")"
        
        style = a_designcode['style']['style']

        if style == "contrastcode":
            value = a_designcode['style']['value']
            designstyle = 'designstyle('+str(style) + "," + str(value)+')'

        else:
            designstyle = 'designstyle('+str(style)+')'
        # for columns
        columns_string = ""
        for a_column in a_designcode["columns"]:
            column_from = a_column['column_from']
            column_from = str(column_from).strip("[,'',]")
            column_to = a_column['column_to']
            if a_column == a_designcode["columns"][-1]:
                columns_string += column_from+'/'+column_to
            else:
                columns_string += column_from+'/'+column_to + ', '
            
        column_string_output = 'columns('+columns_string+')'
        
        # nullstyle
        nulltype_string = ""
        if 'nullstyle' in a_designcode:
            nullstyle = a_designcode['nullstyle']
            if a_designcode['fillna_value'] == None: 
                nulltype_string = 'nullstyle('+nullstyle+')'
            else:
                fillna_value = a_designcode['fillna_value']
                nulltype_string = 'nullstyle('+nullstyle+','+str(fillna_value)+')'

        if nulltype_string == "":
            function_list.append('{'+designstyle +',' +designvalues+',' +column_string_output+'}')
        else:
            function_list.append('{'+designstyle +','+designvalues+',' +column_string_output+','+nulltype_string +'}')


    return execute_transform(recipe_config, 'designcode', function_list, "onehotencoder_", valib_query_wrapper=valib_query_wrapper)



