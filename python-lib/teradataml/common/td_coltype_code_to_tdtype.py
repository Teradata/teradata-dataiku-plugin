# -*- coding: utf-8 -*-
#Dictionary mapping the 2 character type codes from
#HELP COLUMN to the Teradata types.
#TODO: Add to global constants class once added to pyTeradata.
HELP_COL_TYPE_TO_TDTYPE = {
"AT" : "TIME",
"BF" : "BYTE",
"BO" : "BLOB",
"BV" : "VARBYTE",
"CF" : "CHAR",
"CO" : "CLOB",
"CV" : "VARCHAR",
"D"  : "DECIMAL",
"DA" : "DATE",
"DH" : "INTERVAL DAY TO HOUR",
"DM" : "INTERVAL DAY TO MINUTE",
"DS" : "INTERVAL DAY TO SECOND",
"DY" : "INTERVAL DAY",
"F"  : "FLOAT",
"GF" : "GRAPHIC",
"GV" : "VARGRAPHIC",
"HM" : "INTERVAL HOUR TO MINUTE",
"HR" : "INTERVAL HOUR",
"HS" : "INTERVAL HOUR TO SECOND",
"I1" : "BYTEINT",
"I2" : "SMALLINT",
"I"  : "INTEGER",
"I8" : "BIGINT",
"JN" : "JSON",
"MI" : "INTERVAL MINUTE",
"MO" : "INTERVAL MONTH",
"MS" : "INTERVAL MINUTE TO SECOND",
"N"  : "NUMBER",
"PD" : "PERIOD(DATE)",
"PM" : "PERIOD(TIMESTAMP WITH TIME ZONE)",
"PS" : "PERIOD(TIMESTAMP)",
"PT" : "PERIOD(TIME)",
"PZ" : "PERIOD(TIME WITH TIME ZONE)",
"SC" : "INTERVAL SECOND",
"SZ" : "TIMESTAMP WITH TIME ZONE",
"TS" : "TIMESTAMP",
"TZ" : "TIME WITH TIME ZONE",
"XM" : "XML",
"YM" : "INTERVAL YEAR TO MONTH",
"YR" : "INTERVAL YEAR"
}


