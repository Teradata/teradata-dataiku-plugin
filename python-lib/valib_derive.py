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
    # derive
    lst = []

    formula_1 = recipe_config['derive_formula']
    # Santize user specified string: No double quotes or odd number of single quotes
    if ('"' in formula_1) or (formula_1.count("'") % 2 == 1):
        raise Exception('Illegal Formula', formula_1)

    outputname_1 = recipe_config['derive_outputname']
    # Santize user specified string: No double quotes or odd number of single quotes
    if ('"' in outputname_1) or (outputname_1.count("'") % 2 == 1):
        raise Exception('Illegal Output Name', outputname_1)


    arguments_columns_1 = ",".join(recipe_config['derive_arguments_columns'])
    nullstyle_1 = recipe_config['derive_nullstyle1']
    fillna_value_1 = recipe_config['derive_fillna_value1']

    first_dict = {'formula': formula_1, 'arguments_columns': arguments_columns_1, 'outputname': outputname_1,'nullstyle': nullstyle_1, 'fillna_value': fillna_value_1}
    lst.append(first_dict)
    
    function_list = []

    for value in lst:
        # added two single quotes around to match the original query
        value_formula =  value['formula']
        # Santize user specified string: No double quotes or odd number of single quotes
        if ('"' in value_formula) or (value_formula.count("'") % 2 == 1):
            raise Exception('Illegal Formula', value_formula)
        formula = "\""+value_formula+"\""
        
        outputname = value['outputname']
        # Santize user specified string: No double quotes or single quotes
        if ('"' in outputname) or ('"' in outputname):
            raise Exception('Illegal Output Name', outputname)

        arguments_columns = value['arguments_columns']  
        nullstyle = value['nullstyle']
        fillna_value = value['fillna_value']
        
        if nullstyle == "literal":
            derive = "{formula("+str(formula)+"), arguments("+str(arguments_columns)+"), outputname("+str(outputname)+"), nullstyle("+str(nullstyle)+", "+str(fillna_value)+")}"
        elif nullstyle == "None":
            derive = "{formula("+str(formula)+"), arguments("+str(arguments_columns)+"), outputname("+str(outputname)+")}"
        else: 
            derive = "{formula("+str(formula)+"), arguments("+str(arguments_columns)+"), outputname("+str(outputname)+"), nullstyle("+str(nullstyle)+")}"

        function_list.append(derive)


    return execute_transform(recipe_config, 'derive', function_list, 'derive_', valib_query_wrapper=valib_query_wrapper)




