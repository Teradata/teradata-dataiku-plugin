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

    # binning
    lst_bincodes = []


    num_of_bincodebounds = 1

    for i in range(1, 1+num_of_bincodebounds):
        columns = []
        style = recipe_config['binning_style'+str(i)]
        value = recipe_config['binning_value'+str(i)]
        try:
            boundaries_option = recipe_config['binning_boundaries_option'+str(i)]
            style = {'style': style, 'boundaries_option': boundaries_option, 'value': value}

        except:
            style = {'style': style, 'value': value}
        
        bincode_bound_mode = recipe_config['binning_bincode'+str(i)+'_bound_mode']
        bincode_upper_value = recipe_config['binning_bincode'+str(i)+'_upper_value']
        bincode_lower_value = recipe_config['binning_bincode'+str(i)+'_lower_value']
        bound = {'bincode_bound_mode' : bincode_bound_mode, 'bincode_upper_value' : bincode_upper_value, 'bincode_lower_value': bincode_lower_value}
        
        map_dict = recipe_config['binning_map']
        for key in map_dict:
            # No quotes in key or value
            if ("'" in key) or ('"' in key):
                raise Exception('Invalid Key', key)
            if ("'" in map_dict[key]) or ('"' in map_dict[key]):
                raise Exception('Invalid Value', map_dict[key])
            columns.append({'column_from': key, 'column_to': map_dict[key]})

        if recipe_config['binning_nullstyle'+str(i)+''] != "None":
            nullstyle = recipe_config['binning_nullstyle'+str(i)+'']
            if nullstyle == "literal":
                fillna_value = recipe_config['binning_fillna_value'+str(i)+'']
            else:
                fillna_value = None
            bincode_input = {"style": style, "bound": bound, "columns": columns, "nullstyle" : nullstyle, "fillna_value": fillna_value}
        else:
            bincode_input = {"style": style, "bound": bound, "columns": columns}

        lst_bincodes.append(bincode_input)

    # bincode = '{bincodebounds(lowerbound/-1, upperbound/1), columns(Feb/Feb1)}{bincodebounds(upperbound/1), columns(Feb/FebU)}{bincodebounds(lowerbound/0), columns(Feb/FebL)}{bincodebounds(lowerbound/0, upperbound/1), columns(Jan/Jan1, Apr/Apr1), nullstyle(literal, 0)}{bincodebounds(lowerbound/0, upperbound/1), columns(Jan/Jan2, Apr/Apr2), nullstyle(median)}'

    # bincode= {binstyle(binswithboundaries, 5, DATE 1962-01-01, DATE 1962-06-01), columns(period)}{binstyle(boundaries, DATE 1962-01-01, DATE 1962-06-01, DATE 1962-12-31), columns(period/period2)};database=DSSDB;
    function_list = []

    for a_bincode in lst_bincodes:
        style = a_bincode['style']['style']
        if style == 'boundaries':
            style = a_bincode['style']['boundaries_option']

        value = a_bincode['style']['value']

        bincode_bound_mode = a_bincode['bound']['bincode_bound_mode']
        # for Bound
        if bincode_bound_mode == "upperbound":
            bincode_upper_value = a_bincode['bound']['bincode_upper_value']
            bound_string = bincode_bound_mode+'/'+ str(bincode_upper_value)
            binstyle = 'binstyle('+str(style) + "," + str(value)+ "," + str(bound_string)+')'

        elif bincode_bound_mode == "lowerbound":
            bincode_lower_value = a_bincode['bound']['bincode_lower_value']
            bound_string = bincode_bound_mode+'/'+str(bincode_lower_value)
            binstyle = 'binstyle('+str(style) + "," + str(value)+ "," + str(bound_string)+')'
        else: 
            bincode_bound_from = "upperbound"
            bincode_bound_from2 = "lowerbound"
            bincode_upper_value = a_bincode['bound']['bincode_upper_value']
            bincode_lower_value = a_bincode['bound']['bincode_lower_value']
            bound_string = bincode_bound_from+'/'+ str(bincode_upper_value) +', '+bincode_bound_from2+'/'+str(bincode_lower_value)
            binstyle = 'binstyle('+str(style) + "," + str(value)+ str(bincode_lower_value)+ ','+ str(bound_string)+')'


        # for columns
        columns_string = ""
        for a_column in a_bincode["columns"]:
            column_from = a_column['column_from']
            column_from = str(column_from).strip("[,'',]")
            column_to = a_column['column_to']
            if a_column == a_bincode["columns"][-1]:
                columns_string += column_from+'/'+column_to
            else:
                columns_string += column_from+'/'+column_to + ', '
        
        column_string_output = 'columns('+columns_string+')'

        # nullstyle
        nulltype_string = ""
        if 'nullstyle' in a_bincode:
            nullstyle = a_bincode['nullstyle']
            if fillna_value == None: 
                nulltype_string = 'nullstyle('+nullstyle+')'
            else:
                fillna_value = a_bincode['fillna_value']
                nulltype_string = 'nullstyle('+nullstyle+','+str(fillna_value)+')'

        if nulltype_string == "":
            function_list.append('{'+binstyle +',' +column_string_output+'}')
        else:
            function_list.append('{'+binstyle +','+column_string_output+','+nulltype_string +'}')

    if not columns_string:
        raise Exception('No columns specified')


    return execute_transform(recipe_config, 'bincode', function_list, "binning_", valib_query_wrapper=valib_query_wrapper)



