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
    # minmaxscalar
    lst_rescales = []


    num_of_rescalebounds = 1
    
    for i in range(1, 1+num_of_rescalebounds):
        columns = []
        rescale_bound_mode = recipe_config['minmaxscalar_rescale'+str(i)+'_bound_mode']
        rescale_upper_value = recipe_config['minmaxscalar_rescale'+str(i)+'_upper_value']
        rescale_lower_value = recipe_config['minmaxscalar_rescale'+str(i)+'_lower_value']
        bound = {'rescale_bound_mode' : rescale_bound_mode, 'rescale_upper_value' : rescale_upper_value, 'rescale_lower_value': rescale_lower_value}
        
        map_dict = recipe_config['minmaxscalar_map']
        for key in map_dict:
            # No quotes in key or value
            if ("'" in key) or ('"' in key):
                raise Exception('Invalid Key', key)
            if ("'" in map_dict[key]) or ('"' in map_dict[key]):
                raise Exception('Invalid Value', map_dict[key])
            
            columns.append({'column_from': key, 'column_to': map_dict[key]})

        if recipe_config['minmaxscalar_nullstyle'+str(i)+''] != "None":
            nullstyle = recipe_config['minmaxscalar_nullstyle'+str(i)+'']
            if nullstyle == "literal":
                fillna_value = recipe_config['minmaxscalar_fillna_value'+str(i)+'']
            else:
                fillna_value = None
            rescale_input = {"bound": bound, "columns": columns, "nullstyle" : nullstyle, "fillna_value": fillna_value}
        else:
            rescale_input = {"bound": bound, "columns": columns}
        
        lst_rescales.append(rescale_input)

    # rescale = '{rescalebounds(lowerbound/-1, upperbound/1), columns(Feb/Feb1)}{rescalebounds(upperbound/1), columns(Feb/FebU)}{rescalebounds(lowerbound/0), columns(Feb/FebL)}{rescalebounds(lowerbound/0, upperbound/1), columns(Jan/Jan1, Apr/Apr1), nullstyle(literal, 0)}{rescalebounds(lowerbound/0, upperbound/1), columns(Jan/Jan2, Apr/Apr2), nullstyle(median)}'

    function_list = []

    for a_rescale in lst_rescales:
        rescale_bound_mode = a_rescale['bound']['rescale_bound_mode']
        # for Bound
        if rescale_bound_mode == "upperbound":
            rescale_upper_value = a_rescale['bound']['rescale_upper_value']
            bound_string = 'rescalebounds('+rescale_bound_mode+'/'+ str(rescale_upper_value)+')'

        elif rescale_bound_mode == "lowerbound":
            rescale_lower_value = a_rescale['bound']['rescale_lower_value']
            bound_string = 'rescalebounds('+rescale_bound_mode+'/'+str(rescale_lower_value) +')'

        else: 
            rescale_bound_from = "upperbound"
            rescale_bound_from2 = "lowerbound"
            rescale_upper_value = a_rescale['bound']['rescale_upper_value']
            rescale_lower_value = a_rescale['bound']['rescale_lower_value']
            bound_string = 'rescalebounds('+rescale_bound_from+'/'+ str(rescale_upper_value) +', '+rescale_bound_from2+'/'+str(rescale_lower_value) +')'
        
        # for columns
        columns_string = ""
        for a_column in a_rescale["columns"]:
            column_from = a_column['column_from']
            column_from = str(column_from).strip("[,'',]")
            column_to = a_column['column_to']
            if a_column == a_rescale["columns"][-1]:
                columns_string += column_from+'/'+column_to
            else:
                columns_string += column_from+'/'+column_to + ', '
            
        column_string_output = 'columns('+columns_string+')'
        
        # nullstyle
        nulltype_string = ""
        if 'nullstyle' in a_rescale:
            nullstyle = a_rescale['nullstyle']
            if fillna_value == None: 
                nulltype_string = 'nullstyle('+nullstyle+')'
            else:
                fillna_value = a_rescale['fillna_value']
                nulltype_string = 'nullstyle('+nullstyle+','+str(fillna_value)+')'
        
        if nulltype_string == "":
            function_list.append('{'+bound_string+','+column_string_output+'}')
        else:
            function_list.append('{'+bound_string+','+column_string_output+','+nulltype_string +'}')

    return execute_transform(recipe_config, 'rescale', function_list, "minmaxscalar_", valib_query_wrapper=valib_query_wrapper)
