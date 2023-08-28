# -*- coding: utf-8 -*-
import os
import sys
import json
import dataiku
import logging
from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role, get_recipe_config

def get_input_object(input_id,project_name):
    # Purpose of the function is to return the object type of a given input in a project.
    # param 1 :string: input id or name 
    # param 2 :string: project name in which input is present.
    # returns the type of input such as a dataiku.Folder or dataiku.Model or dataiku.Dataset

    # Obtaining project reference. 
    client = dataiku.api_client()
    project = client.get_project(project_name)
    # obtain list of existing objects and compare.
    models = project.list_saved_models()
    model_list = []
    for m in models:
        name = m['id']
        model_list.append(name)

    folders = project.list_managed_folders()
    folder_list = []
    for f in folders:
        name = f['id']
        folder_list.append(name)
 
    # return if found in one of the list
    if input_id in model_list:
        return 'model'
    elif input_id in folder_list:
        return 'folder'
    else:
        raise ValueError('Unacceptable data object type.')
