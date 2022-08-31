import dataiku
# Import the helpers for custom recipes
from dataiku.customrecipe import *
import pandas as pd
import logging
from verifyTableColumns import *


# Inputs and outputs are defined by roles. In the recipe's I/O tab, the user can associate one
# or more dataset to each input and output role.
# Roles need to be defined in recipe.json, in the inputRoles and outputRoles fields.

    
def verifyOverwriteCache(overwrite_cache, model_name):
    result = ""
    # verify by checking model name
    if bool(overwrite_cache):
        result = f"OverwriteCachedModel({verifyModelName(model_name)})"
    return result

def verifyModelOutputValues(modeloutputfields_values):
    modeloutputfield_list = modeloutputfields_values.split(',')
    stripped_list = []
    for i in range(len(modeloutputfield_list)):
        # value names should not have quotes in them
        value = modeloutputfield_list[i].strip()
        if ('"' in value) or ("'" in value):
            raise Exception('Illegal Value Name', value)
        stripped_list.append(value)
    def listToString(s): 
        str1 =""
        for ele in range(len(s)):  
            str1 += s[ele] + " "
        return str1 
    modeloutputfields_values = listToString(stripped_list).strip().replace(" ","\',\'")
    return f"ModelOutputFields('{modeloutputfields_values}')"


def verifyAccumulate(columnNames):
    # Handle special case
    if columnNames == "*":
        return "Accumulate('*')"
    # column names must be not empty
    if not columnNames:
        raise Exception('Illegal Accumulate Columns', columnNames)
    lst = columnNames.split(',')
    quoted_list = []
    # check all columns are valid
    for columnName in lst:
        # verify and quote column name
        columnName = verifyColumnName(columnName, single_quotes=True)
        quoted_list.append(columnName)
    # return the quoted columns
    accumulate = ",".join(quoted_list)
    return f"Accumulate({accumulate})"



# To  retrieve the datasets of an input role named 'input_A' as an array of dataset names:
input_dataset_name = get_input_names_for_role('input_dataset')[0]
input_dataset = dataiku.Dataset(input_dataset_name)
testing_dataset = input_dataset_name.split('.')[1]
output_dataset_name = get_output_names_for_role('output_dataset')[0]
output_dataset = dataiku.Dataset(output_dataset_name) 

from dataiku import SQLExecutor2

scoring_type = str(get_recipe_config()["scoring_type"])
userDBInputChoice = str(get_recipe_config()["user_DBInput_Choice"])

if userDBInputChoice == 'db_drop_down':
    database_name = str(get_recipe_config()["model_database_name"])
elif userDBInputChoice == 'user_db_choice':
    database_name = str(get_recipe_config()["user_Typed_DBName"])


userTBLInputChoice = str(get_recipe_config()["user_TBLInput_Choice"])
if userTBLInputChoice == 'tbl_drop_down':
    table_name = str(get_recipe_config()["table_name"])
elif userTBLInputChoice == 'user_tbl_choice':
    table_name = str(get_recipe_config()["user_Typed_TBLName"])

  
model_name = str(get_recipe_config()["model_name"])

accumulate_all = bool(get_recipe_config()["accumulate_all"])
modeloutputfields_user = bool(get_recipe_config()["modeloutputfields_user"])
predict_func_dbname = str(get_recipe_config()["PMMLPredict_database_name"])
overwrite_cache = get_recipe_config()["overwrite_cache"]
modeloutputfields_values = str(get_recipe_config().get("modeloutputfields_values", ""))
    
if predict_func_dbname == 'user_choice':
    PMMLPredict_db = str(get_recipe_config()["BYOM_Predict_User_DB"])
else:
    PMMLPredict_db = "mldb"
 


if accumulate_all == True:
    accumulate = '*'
if accumulate_all == False:
    accumulate_column_names = get_recipe_config().get("accumulate_column_names", [])
    # convert list to a comma seperated string
    accumulate = ",".join(accumulate_column_names)


conn =  SQLExecutor2(dataset = input_dataset)


if scoring_type == 'dataiku':
    if modeloutputfields_user == False:
        query = f"SELECT * FROM {verifyDatabaseName(PMMLPredict_db)}.PMMLPredict ( ON (select * from {verifyDatabaseName(database_name)}.{verifyDatabaseName(testing_dataset)}) AS InputTable ON (SELECT * FROM {verifyDatabaseName(database_name)}.{verifyTableName(table_name)} WHERE model_id = {verifyModelName(model_name)}) AS ModelTable DIMENSION USING {verifyAccumulate(accumulate)} {verifyOverwriteCache(overwrite_cache, model_name)})AS td;"
    else:
        query = f"SELECT * FROM {verifyDatabaseName(PMMLPredict_db)}.PMMLPredict ( ON (select * from {verifyDatabaseName(database_name)}.{verifyDatabaseName(testing_dataset)}) AS InputTable ON (SELECT * FROM {verifyDatabaseName(database_name)}.{verifyTableName(table_name)} WHERE model_id = {verifyModelName(model_name)}) AS ModelTable DIMENSION USING {verifyAccumulate(accumulate)} {verifyModelOutputValues(modeloutputfields_values)} {verifyOverwriteCache(overwrite_cache, model_name)})AS td;"
    predicted = conn.query_to_df(query)
    
if scoring_type == 'h2o':
    h2o_model_type = str(get_recipe_config()["H2O_Model_Type"])
    dia_license_table_name=""
    if h2o_model_type == 'h2o_dai':
        #For H2O-DAI, Fetching the License DB name from GUI
        dia_license_db_inputType = str(get_recipe_config()["H2O_DIALicense_DB"])
        if dia_license_db_inputType == 'user_license_db_choice':
            dia_license_db_name = str(get_recipe_config()["user_Typed_License_DB_Name"])
        elif dia_license_db_inputType == 'h2o_license_db_drop_down':
            dia_license_db_name = str(get_recipe_config()["H2OLicense_DropDown_DB_Name"])
            
        #For H2O-DAI, Fetching the License Table name from GUI
        dia_license_Table_inputType = str(get_recipe_config()["H2O_DIALicense_Table"])
        
        if dia_license_Table_inputType == 'user_license_table_choice':
            dia_license_table_name = str(get_recipe_config()["user_Typed_License_Table_Name"])
        elif dia_license_Table_inputType == 'h2o_license_table_drop_down':
            dia_license_table_name = str(get_recipe_config()["H2OLicense_DropDown_Table_Name"])

        
        if modeloutputfields_user == False:
            query = f"SELECT * FROM {verifyDatabaseName(PMMLPredict_db)}.H2OPredict ( ON (select * from {verifyDatabaseName(database_name)}.{verifyDatabaseName(testing_dataset)}) AS InputTable ON (SELECT model_id, model, {verifyDatabaseName(dia_license_db_name)}.{verifyDatabaseName(dia_license_table_name)}.license FROM {verifyDatabaseName(database_name)}.{verifyTableName(table_name)} WHERE model_id = {verifyModelName(model_name)}) AS ModelTable DIMENSION USING {verifyAccumulate(accumulate)} ModelType ('DAI') {verifyOverwriteCache(overwrite_cache, model_name)})AS td;"
        else:
            query = f"SELECT * FROM {verifyDatabaseName(PMMLPredict_db)}.H2OPredict ( ON (select * from {verifyDatabaseName(database_name)}.{verifyDatabaseName(testing_dataset)}) AS InputTable ON (SELECT model_id, model, {verifyDatabaseName(dia_license_db_name)}.{verifyDatabaseName(dia_license_table_name)}.license FROM {verifyDatabaseName(database_name)}.{verifyTableName(table_name)} WHERE model_id = {verifyModelName(model_name)}) AS ModelTable DIMENSION USING {verifyAccumulate(accumulate)} ModelType ('DAI') {verifyModelOutputValues(modeloutputfields_values)} {verifyOverwriteCache(overwrite_cache, model_name)})AS td;"
    else:
        if modeloutputfields_user == False:
            query = f"SELECT * FROM {verifyDatabaseName(PMMLPredict_db)}.H2OPredict ( ON (select * from {verifyDatabaseName(database_name)}.{verifyDatabaseName(testing_dataset)}) AS InputTable ON (SELECT model_id, model FROM {verifyDatabaseName(database_name)}.{verifyTableName(table_name)} WHERE model_id = {verifyModelName(model_name)}) AS ModelTable DIMENSION USING {verifyAccumulate(accumulate)} {verifyOverwriteCache(overwrite_cache, model_name)})AS td;"
        else:
            query = f"SELECT * FROM {verifyDatabaseName(PMMLPredict_db)}.H2OPredict ( ON (select * from {verifyDatabaseName(database_name)}.{verifyDatabaseName(testing_dataset)}) AS InputTable ON (SELECT model_id, model FROM {verifyDatabaseName(database_name)}.{verifyTableName(table_name)} WHERE model_id = {verifyModelName(model_name)}) AS ModelTable DIMENSION USING {verifyAccumulate(accumulate)} {verifyModelOutputValues(modeloutputfields_values)} {verifyOverwriteCache(overwrite_cache, model_name)})AS td;"
    predicted = conn.query_to_df(query)
    
logging.info(f"Prediction Query ==> {query}")
output_dataset.write_with_schema(pd.DataFrame(predicted))
