# Teradata Vantage SQL Engine Functions Plugin

For proper monitoring of deployed ML models, a considerate data scientist/ML engineer want to check new data looks like training data.

## Scope of the plugin

The Teradata Vantage SQL Engine Functions Plugin allows end users to leverage Vantage analytics within their DSS data science workflows. This plugin provides support for a majority of the Advanced SQL Engine analytics functions in 16.20.


## Installation and requirements

Please see our [official plugin page](https://www.teradata.com/TBD/) for installation.

To install the Teradata Vantage SQL Engine Functions plugin for Dataiku DSS, perform the following:

1. In DSS Settings page (accessible through the Admin Tools button), select the [Plugins] tab, then select the [ADVANCED] option.
2. Click on [Choose File] and browse to the location of the present plugin zip file in your local filesystem.
3. If a previous installation of present plugin exists, check "Is update".
4. Click on [UPLOAD] button.
5. When the upload succeeds, click on [Reload] button, or do a hard refresh (Ctrl + F5) on all open Dataiku browsers for the change to take effect.

Documentation for the present plugin exists in the folder "resource/documentation" of the plugin zip file.


## Changelog

**Version 2.0-2 (2021-04)**

* Bug fix: The functions visual interface was distorted in DSS v.8.0.x.
* Bug fix: An older version of the functions JSON file caused the Pack and Unpack functions to invoke the nonexistent argument “Columns” instead of “Column”. Fix was made inline in existing JSON file.

**Version 2.0-1 (2021-04)**

* Initial release

You can log feature requests or issues on our [dedicated Github repository](https://github.com/TBD/issues).


## System Requirements

The following component versions are required for the Teradata Vantage Plugin:

1. Dataiku Data Science Studio version 8.0.2 - TBD
2. Teradata Vantage 2.0
3. Teradata JDBC Driver 16.20 (minimum), Teradata JDBC Driver 17.00 (recommended)


## Limitations

1. For analytic functions that:
   - take in output table names as arguments, and
   - where the select query produces only a message table indicating the name of the output model/metrics table, it is the responsibility of the user to specify output table names that are different from those of the existing tables.
   Some analytic functions provide an option to delete an already existing output table prior to executing an algorithm, but others do not. In the former case, the Advanced SQL Engine throws an "Already exists" exception.

2. The plugin only supports Vantage Advanced SQL Engine Database datasets as input and output.

3. Due to the mode the plugin creates output tables, the function output is checked for duplicate rows. If any duplicate rows are found, then they are removed from the output table. This behavior is not adjustable in the present version of the plugin.

4. Functions with any OUTPUT TABLE type arguments will require the user to add an output dataset for the SELECT statement results of the query and any additional output tables. Please refer to the Vantage Advanced SQL Engine Analytic Functions documentation page at docs.teradata.com to learn about the output tables of each function.

5. The following Advanced SQL Engine functions are not supported:
   - DecisionForestPredict
   - DecisionTreePredict
   - GLMPredict
   - NaiveBayesPredict
   - NaiveBayesTextClassifierPredict
   - SVMSparsePredict


## References

For additional information on the Teradata Vantage Advanced SQL Engine analytic functions, search for the following on docs.teradata.com:

1. "Advanced SQL Engine Analytic Functions Overview".
2. "Teradata Vantage Advanced SQL Engine Analytic Functions".
3. "Teradata Vantage User Guide".


# License

The Teradata Vantage SQL Engine Functions Plugin is:

   Copyright © 2021 by Teradata.
   Licensed under the [TBD](LICENSE).





