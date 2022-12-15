# -*- coding: utf-8 -*-
import json
import os
from verifyTableColumns import *

# SERIES_SPEC
# (
#    TABLE_NAME ( [database-name . ] table name ) ,
#    ROW_AXIS ( { TIMECODE | SEQUENCE } ( field ) ) ,
#    SERIES_ID ( field-list ) ,
#    [ID_SEQUENCE ( instance-identifier-list-json-string )]
#       PAYLOAD (
#          FIELDS ( field-list ) ,
#          CONTENT ( { REAL | COMPLEX | AMPL_PHASE | AMPL_PHASE_RADIANS |
#            AMPL_PHASE_DEGREES | MULTIVAR_REAL | MULTIVAR_COMPLEX |  
#            MULTIVAR_ANYTYPE | MULTIVAR_AMPL_PHASE |
#            MULTIVAR_AMPL_PHASE_RADIANS | MULTIVAR_AMPL_PHASE_DEGREES } )
#       )
#    [, LAYER ( layer-name ) ]
#    [, INTERVAL ( { time-duration [ , time-zero ] |
#        { integer | float } [ ,
#         sequence-zero ] }
#     )]
# )
def gen_series_uaf(stmts, input_table_name, req_input, space_count, input_db_name=""):
    error = ""

    # START SERIES GROUP
    stmts.append("{}SERIES_SPEC (".format(" "*space_count))
    space_count += 1

    # TABLE_NAME
    stmts.append("{}TABLE_NAME ({}),".format(" "*space_count, verifyQualifiedTableName(input_db_name, input_table_name)))
    if not input_table_name:
        error += "Error {} has missing Table\n".format(verifyAttribute(req_input["uaf"].get("name")))
    is_row_sequence = req_input["uaf"].get("is_row_sequence", "SEQUENCE")

    # ROW_AXIS
    row_axis_name = req_input["uaf"].get("row_axis_name", "")
    if not row_axis_name:
        error += "Error {} has missing Row Axis\n".format(verifyAttribute(req_input["uaf"].get("name")))
    stmts.append("{}ROW_AXIS ({} ({})),".format(" "*space_count, verifyAttribute(is_row_sequence), verifyAttribute(row_axis_name)))

    # SERIES_ID
    id_name = req_input["uaf"].get("id_name", "")
    if not id_name:
        error += "Error {} has missing Series ID\n".format(verifyAttribute(req_input["uaf"].get("name")))
    id_name = id_name.split('\x00')
    stmts.append("{}SERIES_ID ( {} ),".format(" "*space_count,  verifyAttribute(",".join(id_name))))


    # OPTIONAL ID_SEQUENCE
    id_sequence = req_input["uaf"].get("id_sequence", "")
    if id_sequence:
        id_sequence = id_sequence.split('\x00')
        stmts.append("{} ID_SEQUENCE( {} ),".format(" "*space_count, verifyAttribute(",".join(id_sequence))))

    # START PAYLOAD GROUP
    stmts.append("{}PAYLOAD (".format(" "*space_count))
    space_count+=1

    # PAYLOAD FIELDS
    payload_fields = req_input["uaf"].get("payload_fields", "")
    if not payload_fields:
        error += "Error {} has missing Payload Fields\n".format(verifyAttribute(req_input["uaf"].get("name")))
    payload_fields = payload_fields.split('\x00')
    stmts.append("{}FIELDS ({}),".format(" "*space_count, verifyAttribute(",".join(payload_fields))))

    # PAYLOAD CONTENT
    payload_content = req_input["uaf"].get("payload_content", "")
    if not payload_content:
        error += "Error {} has missing Payload Content\n".format(verifyAttribute(req_input["uaf"].get("name")))
    stmts.append("{}CONTENT ({})".format(" "*space_count, verifyAttribute(payload_content)))

    # END PAYLOAD GROUP
    space_count-=1
    stmts.append("{}),".format(" "*space_count))

    # OPTIONAL LAYER
    layer = req_input["uaf"].get("layer", "")
    if layer:
        layer = layer.split('\x00')
        stmts.append("{}LAYER ({}),".format(" "*space_count, verifyAttribute(",".join(layer))))

    # OPTIONAL INTERVAL
    if req_input["uaf"].get("interval", "Off") == "On":
        # START INTERVAL GROUP
        stmts.append("{}INTERVAL (".format(" "*space_count))
        space_count+=1

        # TIME_DURATION
        time_duration = req_input["uaf"].get("time_duration", "")
        if not time_duration:
            error += "Error {} has missing Interval Time Duration\n".format(verifyAttribute(req_input["uaf"].get("name")))
        stmts[-1] += "{} {} ".format(" "*space_count, verifyAttribute(time_duration))

        # OPTIONAL TIME ZERO
        time_zero = req_input["uaf"].get("time_zero", "")
        if time_zero != "":
            stmts[-1] += " ,{} ".format( verifyAttribute(time_zero))

        # TIME TYPE
        time_type = req_input["uaf"].get("time_type", "")
        if time_type != "":
            stmts[-1] += " {} ".format( verifyAttribute(time_type))

        # OPTIONAL SEQ ZERO
        seq_zero = req_input["uaf"].get("seq_zero", "")
        if seq_zero:
            stmts[-1] += " ({}),".format(verifyAttribute(seq_zero))

        # strip the last comma
        stmts[-1] = stmts[-1].rstrip(",")

        # END INTERVAL GROUP
        space_count-=1
        stmts[-1] += "{}),".format(" "*space_count)

    # strip the last comma
    stmts[-1] = stmts[-1].rstrip(",")

    # END SERIES GROUP
    # OPTIONAL WHERE
    space_count -= 1
    where = req_input["uaf"].get("where", "")
    if where:
        stmts.append("{}) WHERE ({}),".format(" "*space_count, verifyAttribute(where)))
    else:
        stmts.append("{}),".format(" "*space_count))
    return error


# MATRIX_SPEC(
#    TABLE_NAME( [ database-name . ] table name ),
#    ROW_AXIS ( { TIMECODE | SEQUENCE } ( field ) ) ,
#    COLUMN_AXIS ( { TIMECODE | SEQUENCE } ( field ) ) ,
#    MATRIX_ID ( field-list ) ,
#       [ID_SEQUENCE ( instance-identifier-list-json-string ) ,]
#    PAYLOAD (
#       FIELDS ( field-list ) ,
#       CONTENT ( { REAL | COMPLEX | AMPL_PHASE | AMPL_PHASE_RADIANS |
#           AMPL_PHASE_DEGREES | MULTIVAR_REAL | MULTIVAR_COMPLEX |
#           MULTIVAR_ANYTYPE   MULTIVAR_AMPL_PHASE |
#           MULTIVAR_AMPL_PHASE_RADIANS | MULTIVAR_AMPL_PHASE_DEGREES } )
#       ) ,
#    [LAYER ( layer-name ) ]
# )
def gen_matrix_uaf(stmts, input_table_name, req_input, space_count, input_db_name=""):
    error = ""
    # START MATRIX GROUP
    stmts.append("{}MATRIX_SPEC (".format(" "*space_count))
    space_count += 1

    # TABLE_NAME
    stmts.append("{}TABLE_NAME ({}),".format(" "*space_count, verifyQualifiedTableName(input_db_name, input_table_name)))
    if not input_table_name:
        error += "Error {} has missing Table\n".format(verifyAttribute(req_input["uaf"].get("name")))
    is_row_sequence = req_input["uaf"].get("is_row_sequence", "SEQUENCE")
    is_col_sequence = req_input["uaf"].get("is_col_sequence", "SEQUENCE")
    
    # COLUMN_AXIS
    column_axis_name = req_input["uaf"].get("column_axis_name", "")
    if not column_axis_name:
        error += "Error {} has missing Column Axis\n".format(verifyAttribute(req_input["uaf"].get("name")))
    stmts.append("{}COLUMN_AXIS ({} ({})),".format(" "*space_count, verifyAttribute(is_col_sequence), verifyAttribute(column_axis_name)))

    # ROW_AXIS
    row_axis_name = req_input["uaf"].get("row_axis_name", "")
    if not row_axis_name:
        error += "Error {} has missing Row Axis\n".format(verifyAttribute(req_input["uaf"].get("name")))
    stmts.append("{}ROW_AXIS ({} ({})),".format(" "*space_count, verifyAttribute(is_row_sequence), verifyAttribute(row_axis_name)))

    # MATRIX_ID
    id_name = req_input["uaf"].get("id_name", "")
    if not id_name:
        error += "Error {} has missing Matrix ID\n".format(verifyAttribute(req_input["uaf"].get("name")))
    id_name = id_name.split('\x00')
    stmts.append("{}MATRIX_ID ( {} ),".format(" "*space_count,  verifyAttribute(",".join(id_name))))

    # OPTIONAL ID_SEQUENCE
    id_sequence = req_input["uaf"].get("id_sequence", "")
    if id_sequence:
        id_sequence = id_sequence.split('\x00')
        stmts.append("{} ID_SEQUENCE( {} ),".format(" "*space_count, verifyAttribute(",".join(id_sequence))))

    # START PAYLOAD GROUP
    stmts.append("{}PAYLOAD (".format(" "*space_count))
    space_count+=1

    # PAYLOAD FIELDS
    payload_fields = req_input["uaf"].get("payload_fields", "")
    if not payload_fields:
        error += "Error {} has missing Payload Fields\n".format(verifyAttribute(req_input["uaf"].get("name")))
    payload_fields = payload_fields.split('\x00')
    stmts.append("{}FIELDS ({}),".format(" "*space_count, verifyAttribute(",".join(payload_fields))))

    # PAYLOAD CONTENT
    payload_content = req_input["uaf"].get("payload_content", "")
    if not payload_content:
        error += "Error {} has missing Payload Content\n".format(verifyAttribute(req_input["uaf"].get("name")))
    stmts.append("{}CONTENT ({})".format(" "*space_count, verifyAttribute(payload_content)))

    # END PAYLOAD GROUP
    space_count-=1
    stmts.append("{}),".format(" "*space_count))

    # OPTIONAL LAYER
    layer = req_input["uaf"].get("layer", "")
    if layer:
        layer = layer.split('\x00')
        stmts.append("{}LAYER ({}),".format(" "*space_count, verifyAttribute(",".join(layer))))

    # strip the last comma
    stmts[-1] = stmts[-1].rstrip(",")

    # END SERIES GROUP
    # OPTIONAL WHERE
    space_count -= 1
    where = req_input["uaf"].get("where", "")
    if where:
        stmts.append("{}) WHERE ({}),".format(" "*space_count, verifyAttribute(where)))
    else:
        stmts.append("{}),".format(" "*space_count))
    return error


# ART_SPEC (
#    TABLE_NAME ( [ database-name . ] table-name ) ,
#    [ ID_SEQUENCE ( instance-identifier-list-json-string ) , ]
#    [ PAYLOAD (
#       FIELDS ( field-list ) ,
#       CONTENT ( { REAL | COMPLEX | AMPL_PHASE | AMPL_PHASE_RADIANS |
#          AMPL_PHASE_DEGREES | MULTIVAR_REAL | MULTIVAR_COMPLEX | 
#          MULTIVAR_ANYTYPE | MULTIVAR_AMPL_PHASE | 
#          MULTIVAR_AMPL_PHASE_RADIANS | MULTIVAR_AMPL_PHASE_DEGREES } )
#     ) , ]
#    [LAYER ( layer-name ) ]
# )
def gen_art_uaf(stmts, input_table_name, req_input, space_count, input_db_name=""):
    error = ""
    # START ART GROUP
    stmts.append("{}ART_SPEC (".format(" "*space_count))
    space_count += 1

    # TABLE_NAME
    stmts.append("{}TABLE_NAME ({}),".format(" "*space_count, verifyQualifiedTableName(input_db_name, input_table_name)))
    if not input_table_name:
        error += "Error {} has missing Table\n".format(verifyAttribute(req_input["uaf"].get("name")))

    # OPTIONAL ID_SEQUENCE
    id_sequence = req_input["uaf"].get("id_sequence", "")
    if id_sequence:
        id_sequence = id_sequence.split('\x00')
        stmts.append("{} ID_SEQUENCE( {} ),".format(" "*space_count, verifyAttribute(",".join(id_sequence))))

    # if either payload fields or payload content exist then create payload group
    if req_input["uaf"].get("payload_fields", []) or req_input["uaf"].get("payload_content", ""):
        # START PAYLOAD GROUP
        stmts.append("{}PAYLOAD (".format(" "*space_count))
        space_count+=1

        # PAYLOAD FIELDS
        payload_fields = req_input["uaf"].get("payload_fields", "")
        payload_fields = payload_fields.split('\x00')
        stmts.append("{}FIELDS ({}),".format(" "*space_count, verifyAttribute(",".join(payload_fields))))

        # PAYLOAD CONTENT
        payload_content = req_input["uaf"].get("payload_content", "")
        stmts.append("{}CONTENT ({})".format(" "*space_count, verifyAttribute(payload_content)))

        # END PAYLOAD GROUP
        space_count-=1
        stmts.append("{}),".format(" "*space_count))

    # OPTIONAL LAYER
    layer = req_input["uaf"].get("layer", "")
    if layer:
        layer = layer.split('\x00')
        stmts.append("{}LAYER ({}),".format(" "*space_count, verifyAttribute(",".join(layer))))

    # strip the last comma
    stmts[-1] = stmts[-1].rstrip(",")

    # END SERIES GROUP
    # OPTIONAL WHERE
    space_count -= 1
    where = req_input["uaf"].get("where", "")
    if where:
        stmts.append("{}) WHERE ({}),".format(" "*space_count, verifyAttribute(where)))
    else:
        stmts.append("{}),".format(" "*space_count))
    return error

def gen_genseries_uaf(stmts, input_table_name, req_input, space_count, input_db_name=""):
    # START GENSERIES GROUP
    error = ""
    stmts.append("{}GENSERIES_SPEC (".format(" "*space_count))
    space_count += 1

    # instance_names
    instance_names = req_input["uaf"].get("instance_names", "")
    if instance_names:
        stmts.append("{} INSTANCE_NAMES( '{}' ),".format(" "*space_count, verifyAttribute(instance_names)))

    # data_type
    data_type = req_input["uaf"].get("data_type", "")
    if data_type:
        stmts.append("{} DT( {} ),".format(" "*space_count, verifyAttribute(data_type)))


    # START PAYLOAD GROUP
    stmts.append("{}GEN_PAYLOAD (".format(" "*space_count))
    space_count+=1

    # PAYLOAD start value
    payload_start_value = req_input["uaf"].get("payload_start_value", "")
    stmts.append("{},".format(verifyAttribute(payload_start_value)))

    # PAYLOAD offset value
    payload_offset_value = req_input["uaf"].get("payload_offset_value", "")
    stmts.append("{},".format(verifyAttribute(payload_offset_value)))

    # PAYLOAD offset value
    payload_num_entries = req_input["uaf"].get("payload_num_entries", "")
    stmts.append("{}".format(verifyAttribute(payload_num_entries)))

    # END PAYLOAD GROUP
    space_count-=1
    stmts.append("{})),".format(" "*space_count))

    # END GENSERIES GROUP
    # OPTIONAL WHERE
    space_count -= 1

    return error

def gen_uaf_query(outputTable, config_json, outputDB = ""):
    stmts = []
    error = ""
    start_group_line = []
    space_count = 0
    stmts.append("{}EXECUTE FUNCTION INTO ART ({})".format(" "*space_count, verifyQualifiedTableName(outputDB, outputTable)))
    space_count += 1
    #print("SKS", config_json["function"])
    
    # Some functions do not have function_alias_name, in which case use name
    function_name = config_json["function"].get("function_alias_name")
    if function_name == None:
        function_name = config_json["function"].get("name")

    stmts.append("{}{}".format(" "*space_count, verifyAttribute(function_name)))
    stmts.append("{}(".format(" "*space_count))
    space_count += 1

    for req_input in config_json["function"]["required_input"]:
        input_table_name = req_input.get("value", "")
        input_db_name = ""
        # Translate to full table name
        if ("inputtables" in config_json["function"]) and (input_table_name in config_json["function"]["inputschemas"]):
            input_db_name = config_json["function"]["inputschemas"][input_table_name]
        # Translate to full table name
        if ("inputtables" in config_json["function"]) and (input_table_name in config_json["function"]["inputtables"]):
            input_table_name = config_json["function"]["inputtables"][input_table_name]
        if "GENSERIES" in req_input["uafType"]:
            error += gen_genseries_uaf(stmts, input_table_name, req_input, space_count, input_db_name)
        elif "SERIES" in req_input["uafType"]:
            error += gen_series_uaf(stmts, input_table_name, req_input, space_count, input_db_name)
            is_row_sequence = req_input["uaf"].get("is_row_sequence", "SEQUENCE")
        elif "MATRIX" in req_input["uafType"]:
            error += gen_matrix_uaf(stmts, input_table_name, req_input, space_count, input_db_name)
        elif "ART" in req_input["uafType"]:
            error += gen_art_uaf(stmts, input_table_name, req_input, space_count, input_db_name)
        else:
            error += "Error {} has Unknown uafType\n".format(verifyAttribute(req_input["uaf"].get("name")))


    stmts.append("{}FUNC_PARAMS (".format(" "*space_count))
    space_count += 1
    start_group_line.append(len(stmts))

    inputFormat = ""
    outputFormat = ""
    
    for argument_clause in config_json["function"]["arguments"]:

        name = argument_clause["name"]

        dataype = argument_clause["datatype"]

        if dataype == 'GROUPSTART':
            if '.' in name:
                name = name.split('.')[1]
            if function_name == "TD_PLOT" and (name == "PLOTS" or name == "SERIES"):
                # Square bracket included too
                stmts.append("{}{} [(".format(" "*space_count, verifyAttribute(name)))
            else:
                if function_name == 'TD_RESAMPLE' and name == 'TIMECODE' and is_row_sequence=='SEQUENCE':
                    name = 'SEQUENCE'
                stmts.append("{}{} (".format(" "*space_count, verifyAttribute(name)))
            start_group_line.append(len(stmts))
            space_count += 1
            continue
        
        if '.' in name:
            name = name.split('.')[1]

        if dataype == 'GROUPEND':
            # strip the last comma
            stmts[-1] = stmts[-1].rstrip(",")

            space_count -= 1
            start = start_group_line.pop()
            if start == len(stmts):
                # nothing was added inside the group so remove the group start on prior line
                stmts.pop()
            else:
                if function_name == "TD_PLOT" and (name == "PLOTS" or name == "SERIES"):
                    # Square bracket included too
                    stmts.append("{})],".format(" "*space_count))
                else:
                    stmts.append("{}),".format(" "*space_count))
            continue

        if not "value" in argument_clause:
            continue

        value = argument_clause["value"]
        
        # is there a default value? If so and value == default value then continiue

        if name == "InputFormat":
            inputFormat = value
            continue
        if name == "OutputFormat":
            outputFormat = value
            continue

        if "defaultValue" in argument_clause and value == argument_clause["defaultValue"]:
            continue
        if dataype == "BOOLEAN" or dataype == "BOOL":
            if value == "True" or value == True:
                value = 1
            else:
                value = 0

        stmts.append("{}{} (".format(" "*space_count, verifyAttribute(name)))
        add_quotes = dataype == "STRING" and argument_clause.get("Type", "") != "enumeration"
        if argument_clause.get("allowsLists", False):
            split_list = value.split('\x00') # May need to be \x00
            if len(split_list)>0:
                if add_quotes:
                    stmts[-1] += "'{}'".format(verifyAttribute(split_list[0]))
                else:
                    stmts[-1] += "{}".format(verifyAttribute(split_list[0]))
            for index in range(1, len(split_list)):
                if add_quotes:
                    stmts[-1] += ",'{}'".format(verifyAttribute(split_list[index]))
                else:
                    stmts[-1] += ",{}".format(verifyAttribute(split_list[index]))
        else:
            if add_quotes:
                stmts[-1] += "'{}'".format(verifyAttribute(value))
            else:
                value = str(value)
                stmts[-1] += "{}".format(verifyAttribute(value))
        stmts[-1] += "),"


    # strip the last comma
    stmts[-1] = stmts[-1].rstrip(",")


    space_count -= 1
    start = start_group_line.pop()
    if start == len(stmts):
        # nothing was added inside the group so remove the group start on prior line
        stmts.pop()
        # strip the last comma
        stmts[-1] = stmts[-1].rstrip(",")
    else:
        stmts.append("{})".format(" "*space_count))


    if inputFormat and outputFormat:
        stmts.append(",INPUT_FMT({})".format(verifyAttribute(inputFormat)))
        stmts.append(",OUTPUT_FMT({}),".format(verifyAttribute(outputFormat)))
    elif inputFormat:
        stmts.append(",INPUT_FMT({}),".format(verifyAttribute(inputFormat)))
    elif outputFormat:
        stmts.append(",OUTPUT_FMT({}),".format(verifyAttribute(outputFormat)))
    stmts[-1] = stmts[-1].rstrip(",")


    space_count -= 1
    stmts.append("{});".format(" "*space_count))

    # Join into one string
    stmts = "\n".join(stmts)

    return stmts, error
    


