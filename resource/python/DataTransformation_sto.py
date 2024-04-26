'''
Copyright Â© 2018 by Teradata.
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

import platform
import dataiku
from dataiku.customrecipe import *
import json
import os
import logging
import sys
import httpx as requests
from time import time, sleep
import time
import keyring as kr 
sys.path.append('../../python-lib')

from teradataml.scriptmgmt import list_base_envs, list_user_envs, create_env, remove_env,get_env
from teradataml.scriptmgmt import UserEnv,set_auth_token
from teradataml.options import configure
from teradataml.datetime_helpers import (
    datetime_from_iso_string,
    datetime_plus_seconds,
    now_datetime,
)
from query_engine_wrapper import QueryEngineWrapper
import auth
import jwt
from keyrings.cryptfile.cryptfile import CryptFileKeyring 
import warnings


def get_access_token():
            """
            Sets the access token
            """
            #warnings.simplefilter('error')

            jwt_first_half=kr.get_password("openAF", "jwt_first_half")
            jwt_second_half=kr.get_password("openAF", "jwt_second_half")
            jwt_expiry=float(kr.get_password("openAF", "expiry_time"))
            
            if jwt_first_half and jwt_second_half:
                    jwt = jwt_first_half + jwt_second_half
            # if JWT is not expired setting it to CONFIGURE and use it in OPENAF service calls
                    if ( jwt_expiry and time.time() < jwt_expiry):
                        configure.auth_token=jwt
                        jwt="0000"
                    else:
                        # if JWT is expired deleting JWT and JWT_EXPIRY from key ring
                        if jwt_first_half:
                            kr.delete_password(
                                "openAF", "jwt_first_half"
                            )
                        if jwt_second_half:
                            kr.delete_password(
                                "openAF", "jwt_second_half"
                            )
                        if jwt_expiry:
                            kr.delete_password(
                                "openAF", "expiry_time")
                        jwt = None
                    
                    if jwt is None:
                        raise Exception
                
                    jwt="0000"
                    


FUNCTION_CATEGORY="Data Transformation"

# client is a dataikuapi.DSSClient
client = dataiku.api_client()
auth_info = client.get_auth_info(with_secrets=True)

# Subclass of query engine wrapper implemented with a Dataiku SQLExecutor2
# An instance of this class will be created when we use the functions in analytic_function_utility and vantage_version
class DataikuQueryEngineWrapper(QueryEngineWrapper):
    def __init__(self, executor):
        self.executor = executor


    def execute(self, query_string):
        return self.executor.query_to_df(query_string)

    def iteratable(self, result):
        return result.iterrows()

    def row_value(self, row, column_name):
        return row[1][column_name]

def sto_database(inputdataset):
    if inputdataset == None:
        return ''
    connections = {}
    connectionName = inputdataset.get_location_info()['info']['connectionName']
    connections = auth.addConnection(connections, connectionName)
    result = None
    if "dkuProperties" in connections[connectionName]['params']:
        dkuProperties = connections[connectionName]['params']['dkuProperties']
        for item in dkuProperties:
            if item['name'] == "STO_DATABASE":
                result = item['value']
                break
    if not result:
        return ''
    return result


def getCurrentConnectionName(inputDataset):
    #input Dataset is the output of dataiku.Dataset("dataset name")
    return inputDataset.get_location_info().get('info', {}).get('connectionName',
                                                                '')

def getConnectionParams(name):
    client = dataiku.api_client()
    mydssconnection = client.get_connection(name)
    return mydssconnection.get_definition().get('params', {})

def getConnectionParamsFromDataset(inputDataset):
    return inputDataset.get_location_info(sensitive_info=True)['info']

# paylaod is sent from the javascript's callPythonDo()
# config and plugin_config are the recipe/dataset and plugin configured values
# inputs is the list of input roles (in case of a recipe)
def do_execute(payload, config, plugin_config, inputs):

    inputDataSets = []
    # print(inputtablename)
    connection = {}
    project = ''
    inputFolderLocation = None
    inputdataset = None
    
    # SKS initiate Dataset/SQLExecuter2
    input_table_name = inputs[0]['fullName'].split('.')[1]
    input_dataset =  dataiku.Dataset(input_table_name)
    

    for input in inputs:
        if(input.get('role') == 'main'):
            inputtablename = input['fullName'].split('.')[1]
            project = input['fullName'].split('.')[0]
            inputDataSets.append(inputtablename)
            if not connection:
                inputdataset = dataiku.Dataset(inputtablename)
                connection = getConnectionParamsFromDataset(inputdataset).get('connectionParams', {})
        else:
            inputfoldername = input['fullName'].split('.')[1]       
            inputFolderLocation =  dataiku.Folder(inputfoldername)

    folderpath = inputFolderLocation.get_path() if inputFolderLocation else ''


    def get_username():
        try:
            warnings.simplefilter('error')
            user_name=connection['user']
            return user_name
        except:
            return None
    
    if "tabs_auth" in payload:
       try:
           
           #values = set_auth_token(payload.get('db_user'),payload.get('pat_token'),payload.get('pvt_key'))
           FOLDER_ID = input['fullName'].split('.')[1]

           REPO = dataiku.Folder(FOLDER_ID)
           file = REPO.file_path(payload.get('pvt_key'))
           with open(file, "r") as f:
               private_key = f.read()
           values = set_auth_token(ues_url= payload.get('ues_url'), token=payload.get('pat_token'), pem_file=private_key,pem_file_name=payload.get('pvt_key'),username= get_username(),jwt_expiration=int(payload.get('exp_time')))
           access_token = values['token']
           current_epoch_time = time.time()
           expiry_epoch_time = current_epoch_time + float(payload.get('exp_time'))
           expires_at = str(expiry_epoch_time)
           if platform.system()=='Linux' or platform.system()=='Darwin':
                    # cryptfile as backend only for  Linux
                    cryptfile = CryptFileKeyring()
                    cryptfile.keyring_key = "tdextroutine_key"
                    kr.set_keyring(cryptfile)
           jwt_first_half, jwt_second_half = (
           access_token[: len(access_token) // 2],
                        access_token[len(access_token) // 2 :],
                        )
           kr.set_password(
                            "openAF",
                            "jwt_first_half",
                            jwt_first_half,
                        )
           kr.set_password(
                           "openAF",
                            "jwt_second_half",
                            jwt_second_half,
                        )
           kr.set_password(
                           "openAF",
                            "expiry_time",
                            expires_at,
                        )
           jwt_first_half="000000"
           jwt_second_half="000000"
           if access_token:
                    access_token="00000"
                    return {'result' : "Authentication has been completed successfully."}
           else:
                    return {'result' : "Authentication Failed. Please try again."}
           
           

       except:
           return {'result' : "Authentication has been completed successfully."}
           
    if "delete_env" in payload:
        try:
                try:
                    get_access_token()

                       
                except Exception as e:
                    return {'result' : "Authentication Failed. Please try again."}                
                remove_env(env_name=payload['environment_name'],user=get_username())
                result = "User environment  " + payload["environment_name"] + " has been removed."
                configure.auth_token="0000"
                return {'result' : result}
            
        except Exception as e:
               return {'result' :  str(e).replace("<"," ").replace(">", " ")}

    
    if "base_env" in payload:
       try:
           get_access_token()
           a = list_base_envs()
           a=a.to_dict('split')
           result =[]
           for l in a['data']:
               result.append(l[0])
           result.append("Click to refresh list")
           configure.auth_token="0000"
           return {'choices' : result}
       
       except Exception as e:
               return {'choices' : ["N/A","Click to refresh list"]}
    if "environment_name" in payload:
       try:
           get_access_token()

           a=list_user_envs(user=get_username())
           a=a.to_dict('split')
           result =[]
           for l in a['data']:
            env_version=platform.python_version()
            if float(env_version[:3]) <= 3.7:
               result.append(l[3])
            else:
                result.append(l[0])
           result.append("Click to refresh list")
           configure.auth_token="0000"


           return {'names' : result}
       
       except:
               return {'names' : ['N/A',"Click to refresh list"]}

    if "create_env" in payload:
        try:
            try:
                get_access_token()
            except Exception as e:
                    return {'result' : "Authentication failed. Please try again."}
            demo_env = create_env(env_name = payload["envName"] ,
                          base_env = payload["baseEnv"],
                          desc = payload["des"],user=get_username())
            if demo_env:
                result = "User environment  " + payload["envName"] + " has been created."
                configure.auth_token="0000"

                return {'result' : result}
        except Exception as e:
               return {'result' :  str(e).replace("<"," ").replace(">", " ")}
            
            

    if "file_name" in payload:
       try:
           
           get_access_token()
           env=get_env(env_name=payload["envName"],user=get_username())
           
           a=env.files(user=get_username())
           a=a.values.tolist()
           
           result =[]
           
           for l in a:
               
            env_version=platform.python_version()
            if float(env_version[:3]) <= 3.7:
               result.append(l[2])
            else:
                result.append(l[0])
           result.append("Click to refresh list")
           
           configure.auth_token="0000"
           return {'files' : result}
       
       
       except:
           return {'files' : ["N/A","Click to refresh list"]}
       
       

    if "lib_name" in payload:
       try:
           get_access_token()
           env=get_env(env_name=payload["envName"],user=get_username())
           
           a=env.libs(user=get_username())
           a=a.values.tolist()

           result =[]
           
           for l in a:
               i=0
               j=1
               result.append(""+l[i]+"=="+l[j])
               i+=1
               j+=1
           result.append("Click to refresh list")
           configure.auth_token="0000"

           return {'libs' : result}
       
       except:
           return {'libs' : ["N/A","Click to refresh list"]}
    
    if "install_libs" in payload:
        try:
                try:
                    get_access_token()
                       
                except Exception as e:
                    return {'result' : "Authentication failed. Please try again."}
                libs=payload.get("libs")
                env=get_env(env_name=payload["envName"],user=get_username())
                if len(libs)==0:
                    file_path= os.path.join(folderpath,payload.get("req_lib"))
                    claim_id=env.install_lib(libs_file_path=file_path, asynchronous=True,user=get_username())
                    
                else:
                    # Split the string into a list of strings based on commas
                    libs = libs.split(',')
                    claim_id=env.install_lib(libs, asynchronous=True,user=get_username())

                df=env.status(payload.get('claim_id'),user=get_username())
                df_string = ""
                # To directly convert the output to html:
                #df = df[['Claim Id','File/Libs', 'Method Name', 'Timestamp']]
                #df_string=df.to_html(border=1)+""
                for index, row in df.iterrows():
                    for column_name, value in row.items():
                        if column_name in ['Claim Id','File/Libs', 'Method Name', 'Timestamp']:
                            df_string += f"{column_name}: {value} <br>"
                    df_string+=f"<br>"
                result="Installation is initiated. Check the status using 'Status' button with the claim id:"+ claim_id 
                configure.auth_token="0000"

                return {'result': result,'status':df_string}
        except Exception as e:
               return {'result' : str(e).replace("<"," ").replace(">", " ")}
           
    if "uninstall_libs" in payload:
        try:
            try:
                get_access_token()
                       
            except Exception as e:
                    return {'result' : "Authentication failed. Please try again."}
            libs=payload.get("libs")
            libs = libs.split(',')
            env=get_env(env_name=payload["envName"],user=get_username())
            claim_id=env.uninstall_lib(libs, asynchronous=True,user=get_username())
            result="Uninstallation is initiated. Check the status using 'Status' button with the claim id:" +claim_id
            df=env.status(payload.get('claim_id'),user=get_username())
            df_string=""
            status=''
                # To directly convert the output to html:

                #df = df[['Claim Id','File/Libs', 'Method Name', 'Timestamp']]
                #df_string=df.to_html(border=1)+""
                
            for index, row in df.iterrows():
                for column_name, value in row.items():
                    if column_name in ['Claim Id','File/Libs', 'Method Name', 'Timestamp']:
                        df_string += f"{column_name}: {value} <br>"
                df_string+=f"<br>"
                
            configure.auth_token="0000"

            return {'result': result, 'status':df_string}
        except Exception as e:
               return {'result' :  str(e).replace("<"," ").replace(">", " ")}
  
    if "update_libs" in payload:
        try:
                try:
                    get_access_token()
                       
                except Exception as e:
                    return {'result' : "Authentication failed. Please try again."}                
                libs=payload.get("libs")
                env=get_env(env_name=payload["envName"],user=get_username())
                claim_id=env.update_lib(libs, asynchronous=True,user=get_username())
                result="Update request is initiated. Check the status using 'Status' button with the claim id:"+ claim_id
                df=env.status(payload.get('claim_id'),user=get_username())
                
                df_string=""
                # To directly convert the output to html:
                #df = df[['Claim Id','File/Libs', 'Method Name', 'Timestamp']]
                #df_string=df.to_html(border=1)+""
                for index, row in df.iterrows():
                    for column_name, value in row.items():
                        if column_name in ['Claim Id','File/Libs', 'Method Name', 'Timestamp']:
                            df_string += f"{column_name}: {value} <br>"
                    df_string+=f"<br>"
                configure.auth_token="0000"

                return {'result': result, 'status':df_string}
        except Exception as e:
               return {'result' : str(e).replace("<"," ").replace(">", " ")}
           
    if "install_file" in payload:
         try:
                 try:
                    get_access_token()
                       
                 except Exception as e:
                    return {'result' : "Authentication failed. Please try again."}                
                 #file=payload.get("file")
                 env=get_env(env_name=payload["envName"],user=get_username())
                 file_path= os.path.join(folderpath,payload.get("file"))
                 res=env.install_file(file_path,user=get_username())
                 status = ''
                 df_string=''
                 if res is True:
                     result= payload.get("file")+" uploaded successfully to the remote user environment "+payload.get("envName")
                 elif res is not bool:
                     result="Installation is initiated.As the file size is larger than 10mb, kindly check the status using 'Status' button with the claim id:"+ claim_id
                     df=env.status(payload.get('claim_id'),user=get_username())
                     # To directly convert the output to html:

                     #df = df[['Claim Id','File/Libs', 'Method Name', 'Timestamp']]
                     #df_string=df.to_html(border=1)+""
                     for index, row in df.iterrows():
                        for column_name, value in row.items():
                            if column_name in ['Claim Id','File/Libs', 'Method Name', 'Timestamp']:
                                df_string += f"{column_name}: {value} <br>"
                        df_string+=f"<br>"
                 configure.auth_token="0000"

                 return {'result': result, 'status':df_string}
         except Exception as e:
                return {'result' : str(e).replace("<"," ").replace(">", " ")}            
                       
           
           
    if "uninstall_file" in payload:
        try:
                try:
                    get_access_token()
                       
                except Exception as e:
                    return {'result' : "Authentication failed. Please try again."}                
                file=payload.get("file")
                env=get_env(env_name=payload["envName"],user=get_username())
                res=env.remove_file(file,user=get_username())
                if res is True:
                    result= payload.get("file")+" removed successfully from the remote user environment "+payload.get("envName")
                configure.auth_token="0000"

                return {'result': result}
        except Exception as e:
               return {'result' : str(e).replace("<"," ").replace(">", " ")}            
           

           
    if "refresh" in payload:
        try:
                try:
                    get_access_token()
                       
                except Exception as e:
                    return {'result' : "Authentication failed. Please try again."}                
                env=get_env(env_name=payload["envName"],user=get_username())
                env.refresh()
                result="User environment: " + payload.get('envName') + " has been refreshed"
                configure.auth_token="0000"

                return {'result': result}
        except Exception as e:
               return {'result' : str(e).replace("<"," ").replace(">", " ")}
           
            
    if "status" in payload:
        try:
                try:
                    get_access_token()
                       
                except Exception as e:
                    return {'result' : "Authentication failed. Please try again."}                
                env=get_env(env_name=payload.get('envName'),user=get_username())
                if payload.get('claim_id'):
                    df=env.status(payload.get('claim_id'),user=get_username())
                    # To directly convert the output to html:
                    #df = df[['Claim Id', 'Stage', 'Timestamp','Additional Details']]
                    #result=df.to_html()+""
                    result=''
                    for index, row in df.iterrows():
                        for column_name, value in row.items():
                            if column_name in ['Claim Id', 'Stage', 'Timestamp','Additional Details']:
                                result += f"{column_name}: {value} <br>"
                        result+=f"<br>"
                else:
                    all_status=payload.get('all_status')
                    if len(all_status)==0:
                        result="No Claim ID available for the current session."
                    else:
                        result=payload.get('all_status')
                configure.auth_token="0000"

                return {'result': result}
        except Exception as e:
               return {'result' :  str(e).replace("<"," ").replace(">", " ")}
           
    if "view" in payload:
        try:
                try:
                    get_access_token()
                       
                except Exception as e:
                    return {'result' : "Authentication failed. Please try again."}               
                env=get_env(env_name=payload.get("envName"),user=get_username())
                a=env.libs(user=get_username())
                lib =[]
                lib_str=""
                if a is not None:
                    a=a.values.tolist()

                    for l in a:
                        i=0
                        j=1
                        lib.append(""+l[i]+"=="+l[j])
                        i+=1
                        j+=1
                
                    lib_str=" , "
                    lib_str=lib_str.join(lib)
                
                name=env.env_name
                des=env.desc
                base=env.base_env
                
                File =[]
                File_str=""
                
                try:
                    a=env.files(user=get_username())

                    a=a.values.tolist() 

                    for l in a:
                        env_version=platform.python_version()
                        if float(env_version[:3]) <= 3.7:
                            File.append(l[2])
                        else:
                            File.append(l[0])
                    File_str=" , "
                    File_str=File_str.join(File)
                except:
                    File_str=""        

                finally:
                    result="Details:\n \n "+"Name: "+name+"\n \n Base Environment: "+ base+ "\n \n Description: "+des+ "\n \n Libraries: "+lib_str+ "\n \n Files: "+ File_str
                    configure.auth_token="0000"

                    return {'result': result}

        except Exception as e:
               return {'result' : str(e).replace("<"," ").replace(">", " ")}
    
    

    fileList = os.listdir(folderpath) if folderpath else []
    DATA_DIR = os.environ["DIP_HOME"]
    PYNBDIR = "config/ipython_notebooks/"
    pypath = os.path.join(DATA_DIR, PYNBDIR, project)
    pynbList = filter(lambda f: not f.startswith('.'), os.listdir(pypath)) if\
        os.path.exists(pypath) else []

    sto_db = sto_database(inputdataset)

    # Find Vantage Version
    vantage_version = ""
    is_vantage_cloud = False
    if inputdataset:
        # Execute query to find out the version and establish if it is Vantage Cloud or not
        executor = dataiku.core.sql.SQLExecutor2(dataset=inputdataset) 
        query_string = "SELECT InfoData FROM DBC.DBCInfoV where InfoKey = 'VERSION'"
        query_results = executor.query_to_df(query_string)
        for row in query_results.iterrows():
            vantage_version = row[1]["InfoData"]
            # This code should be made more robust
            logging.info("teradata_analytic_lib: the pm.versionInfo table returns", vantage_version)
            break
        # Find if Vantage Cloud based on vantage version
        if vantage_version.count(".") == 3:
            major_version = vantage_version[-2:]
            minor_version = vantage_version[0:2]
            vantage_version = major_version + '.'+ minor_version
            if int(minor_version) >= 20:
                is_vantage_cloud = True

    # Establish you have privileges to read the connection
    connectionErrorMessage = ""
    try:
        connectionName = inputdataset.get_location_info()['info']['connectionName']
        client = dataiku.api_client()
        if client.get_connection(name=connectionName).get_info():
            connectionErrorMessage = ""
    except:
        connectionErrorMessage = "Permissions error: Contact your Dataiku admin user to have 'Details Readable by' granted to 'Every Analyst' for the connection : " + connectionName

        
    return {'inputfolder':folderpath,
            'fileList':fileList,
            'nbList':pynbList,
            'connection': connection,
            'stoDatabase' : sto_db,
            'inputDataSets':inputDataSets ,
            'inputs': inputs,
            'isVantageCloudLake' : is_vantage_cloud,
            'vantageVersion' : vantage_version,
            'connectionErrorMessage' : connectionErrorMessage
            }

def do(payload, config, plugin_config, inputs):
    try:
      return do_execute(payload, config, plugin_config, inputs)
    except Exception as e:
      return {'error': str(e)}

