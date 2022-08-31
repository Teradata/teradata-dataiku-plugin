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
    # label encoder
    lst_recodecodes = []

    num_of_labelencoders = 1

    for i in range(1, 1+num_of_labelencoders):
        lst = []

        columns = recipe_config['labelencoder_columns'+str(i)]
        
        map_dict = recipe_config['labelencoder_map']

        recodeother = recipe_config['labelencoder_recodeother']
        # Santize user specified string: No double quotes or odd number of single quotes
        if ('"' in recodeother) or (recodeother.count("'") % 2 == 1):
            raise Exception('Illegal Recode Other', recodeother)
        
        
        for key in map_dict:
            # No quotes in key or value
            if ("'" in key) or ('"' in key):
                raise Exception('Invalid Key', key)
            if ("'" in map_dict[key]) or ('"' in map_dict[key]):
                raise Exception('Invalid Value', map_dict[key])
            
            lst.append({'recodevalues_from': key, 'recodevalues_to': map_dict[key], 'recodeother': recodeother})

        nullstyle = recipe_config['labelencoder_nullstyle'+str(i)+'']
        if nullstyle == "literal":
            fillna_value = recipe_config['labelencoder_fillna_value'+str(i)+'']
        else:
            fillna_value = None
        
        recode_input = {"recode": lst, "columns": columns, "nullstyle" : nullstyle, "fillna_value": fillna_value}

        lst_recodecodes.append(recode_input)


    function_list = []

    # value {'recode': [{'recodevalues_from': 'Advanced', 'recodevalues_to': '0', 'recodeother': 'NULL'},
    # {'recodevalues_from': 'Beginner', 'recodevalues_to': '1', 'recodeother': 'NULL'}], 
    # 'nullstyle': 'None', 'fillna_value': None}
    for value in lst_recodecodes:
        recodevalues = ""
        i = 0
        for a_rescale in value["recode"]:
            recodevalues_from = value['recode'][i]['recodevalues_from']
            recodevalues_to = value['recode'][i]['recodevalues_to']
            recodeother = value['recode'][i]['recodeother']
            if a_rescale == value["recode"][-1]:
                recodevalues += str(recodevalues_from)+'/'+str(recodevalues_to)
            else:
                recodevalues += str(recodevalues_from)+'/'+str(recodevalues_to) + ', '
            i += 1

       
        columns = ",".join(value['columns'])
        nullstyle = value['nullstyle']
        fillna_value = value['fillna_value']


        if nullstyle == "literal":
            labelencoder = "{recodevalues("+str(recodevalues)+"), recodeother("+str(recodeother)+"), columns("+str(columns)+"), nullstyle("+str(nullstyle)+", "+str(fillna_value)+")}"
        elif nullstyle == "None":
            labelencoder = "{recodevalues("+str(recodevalues)+"), recodeother("+str(recodeother)+"), columns("+str(columns)+")}"
        else: 
            labelencoder = "{recodevalues("+str(recodevalues)+"), recodeother("+str(recodeother)+"), columns("+str(columns)+"), nullstyle("+str(nullstyle)+")}"
        
        function_list.append(labelencoder)


    return execute_transform(recipe_config, 'recode', function_list, "labelencoder_", valib_query_wrapper=valib_query_wrapper)


