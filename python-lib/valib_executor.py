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

import logging
import valib_chiSquareTest
import valib_binomialTest
import valib_parametricTest
import valib_rankTest

import valib_adaptive_histogram
import valib_association
import valib_overlap
import valib_explore
import valib_decision_tree
import valib_frequency
import valib_histogram
import valib_kmeans
import valib_KSTest
import valib_linreg
import valib_logreg
import valib_matrix
import valib_PCA
import valib_statistics
import valib_textanalyzer
import valib_values

import valib_binning
import valib_derive
import valib_labelencoder
import valib_minmaxscalar
import valib_onehotencoder
import valib_retain
import valib_sigmoid
import valib_zscore
import valib_transform

import valib_linregPredictEvaluate
import valib_logregPredictEvaluate
import valib_decision_treePredictEvaluate
import valib_PCAPredictEvaluate
import valib_kmeans_predict
import valib_xmlToHtmlReport


def valib_execution(json_contents, dss_function, dropIfExists=False, valib_query_wrapper=None):
    correct_json = {}
    label_to_name_map = json_contents["name_map"]
    label_to_type_map = json_contents["type_map"]
    label_to_choice_map = json_contents["choices_map"]
    arguments = dss_function["arguments"]
    for argument in arguments:
        label = argument["name"]
        if "value" in argument:
            value = argument["value"]
        else:
            continue
        name = label_to_name_map[label]
        parameter_type = label_to_type_map[label]
        if parameter_type == 'COLUMNS' or parameter_type == 'COLUMN':
            # Avoid passing in no columns
            if len(value) == 1 and not value[0]:
                continue
        if parameter_type == 'SELECT':
            if value in label_to_choice_map[label]:
                value = label_to_choice_map[label][value]
        
        if parameter_type == 'MULTISELECT':
            if len(value) == 0:
                continue
            if type(value) == str:
                items = value.split('\x00')
            elif type(value) == list:
                items = value
            else:
                continue
            value = []
            for item in items:
                if item in label_to_choice_map[label]:
                    item = label_to_choice_map[label][item]
                value.append(item)

        if parameter_type == 'MAP':
            map_value = {}
            if str(value) == "":
                continue
            elif "/" in str(value):
                sep = "/"
            elif ":" in str(value):
                sep = ":"
            values = value.split('\x00')

            for item in values:
                values = item.split(sep)
                map_value[values[0]] = values[1]
            value = map_value
        if parameter_type == 'STRINGS':
            if str(value) == "":
                continue
            value = value.split('\x00')
        correct_json[name] = value
    function_name = json_contents["function_name"]

    # Get Input Table Names Based on user selection
    if "input_table_names" in dss_function:
        correct_json["input_table_names"] = dss_function["input_table_names"]
    if "output_table_names" in dss_function:
        correct_json["output_table_names"] = dss_function["output_table_names"]
    if "val_location" in dss_function:
        correct_json["val_location"] = dss_function["val_location"] 

    # Execute function
    if function_name == "Chi Square Test VAL":
        result = valib_chiSquareTest.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Binomial Test VAL":
        result = valib_binomialTest.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Parametric Test VAL":
        result = valib_parametricTest.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Rank Test VAL":
        result = valib_rankTest.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    
    elif function_name == "Adaptive Histogram VAL":
        result = valib_adaptive_histogram.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Association VAL":
        result = valib_association.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Overlap VAL":
        result = valib_overlap.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Explore VAL":
        result = valib_explore.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Decision Tree VAL":
        result = valib_decision_tree.execute(correct_json, valib_query_wrapper=valib_query_wrapper)

    elif function_name == "Frequency VAL":
        result = valib_frequency.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Histogram VAL":
        result = valib_histogram.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "K Means VAL":
        result = valib_kmeans.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "KS Test VAL":
        result = valib_KSTest.execute(correct_json, valib_query_wrapper=valib_query_wrapper)

    elif function_name == "Linear Regression VAL":
        result = valib_linreg.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Logistic Regression VAL":
        result = valib_logreg.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Matrix VAL":
        result = valib_matrix.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Principal Component Analysis VAL":
        result = valib_PCA.execute(correct_json, valib_query_wrapper=valib_query_wrapper)

    elif function_name == "Statistics VAL":
        result = valib_statistics.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Text Analyzer VAL":
        result = valib_textanalyzer.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Values VAL":
        result = valib_values.execute(correct_json, valib_query_wrapper=valib_query_wrapper)


    elif function_name == "Binning VAL":
        # Add Drop if exists
        correct_json["binning_dropIfExists"] = dropIfExists
        result = valib_binning.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Derive VAL":
        # Add Drop if exists
        correct_json["derive_dropIfExists"] = dropIfExists
        result = valib_derive.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Label Encoder VAL":
        # Add Drop if exists
        correct_json["labelencoder_dropIfExists"] = dropIfExists
        result = valib_labelencoder.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Min Max Scalar VAL":
        # Add Drop if exists
        correct_json["minmaxscalar_dropIfExists"] = dropIfExists
        result = valib_minmaxscalar.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "One Hot Encoder VAL":
        # Add Drop if exists
        correct_json["onehotencoder_dropIfExists"] = dropIfExists
        result = valib_onehotencoder.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Retain VAL":
        # Add Drop if exists
        correct_json["retain_dropIfExists"] = dropIfExists
        result = valib_retain.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Sigmoid VAL":
        # Add Drop if exists
        correct_json["sigmoid_dropIfExists"] = dropIfExists
        result = valib_sigmoid.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Z Score VAL":
        # Add Drop if exists
        correct_json["zscore_dropIfExists"] = dropIfExists
        result = valib_zscore.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Transform VAL":
        # Add Drop if exists
        correct_json["transform_dropIfExists"] = dropIfExists
        result = valib_transform.execute(correct_json, valib_query_wrapper=valib_query_wrapper)


    elif function_name == "Linear Regression Evaluate VAL" or function_name == "Linear Regression Predict VAL":
        result = valib_linregPredictEvaluate.execute(correct_json, function_name, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Logistic Regression Evaluate VAL" or function_name == "Logistic Regression Predict VAL":
        result = valib_logregPredictEvaluate.execute(correct_json, function_name, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Decision Tree Evaluate VAL" or function_name == "Decision Tree Predict VAL":
        result = valib_decision_treePredictEvaluate.execute(correct_json, function_name, valib_query_wrapper=valib_query_wrapper)

    elif function_name == "Principal Component Analysis Evaluate VAL" or function_name == "Principal Component Analysis Predict VAL":
        result = valib_PCAPredictEvaluate.execute(correct_json, function_name, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "K Means Predict VAL":
        result = valib_kmeans_predict.execute(correct_json, valib_query_wrapper=valib_query_wrapper)
    elif function_name == "Xml To Html Report VAL":
        result = valib_xmlToHtmlReport.execute(correct_json, valib_query_wrapper=valib_query_wrapper)


    logging.info("VALIB " + function_name + " completed!")


    if not valib_query_wrapper:
        result = result.replace("\t", "")
        result = result.split(";")
        result = "<br>".join(result)
        result = result.replace("call VAL", "CALL VAL")
        return result
    


