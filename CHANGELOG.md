# Teradata Plugin Changelog

## Versions 2.4.11, 2.4.12 (September 2023)

* Support for ONNX and Dataiku native model formats in BYOM recipes.
* Minor updates to some of the Analytic Functions definition JSON files.

## Versions 2.3.11, 2.3.12 (July 2023)

* Dataiku 12 is incompatible with preceding Dataiku releases. This plugin release begins support for both Dataiku 11 (or older) and 12 (and newer) releases. For as long as the plugin supports concurrently these 2 different Dataiku release families, the plugin will be using the efix version number to designate compatibility with the corresponding Dataiku release family. To this end: Releasing distinct versions for Dataiku 11 or older (v.2.3.11) and Dataiku 12 (v.2.3.12) platforms. Version 2.3.0 is otherwise identical to 2.3.11.

## Version 2.3.0 (May 2023)

* Support for the Unbounded Array Framework (UAF) time series functions.
* Bug fix: BYOM recipes did not by default run queries in TERA mode.
* Bug fix: If the user should have inadequate permissions to access a recipe, the plugin no longer produces a generic "External Code Failed" error; a permissions-related message is now issued upon accessing a recipe, instead.

## Version 2.2.1 (eFix - February 2023)

* Bug fix: An issue prevented non-admin users from running plugin recipes.

## Version 2.2.0 (December 2022)

* Support for 54 new Analytic Functions in Analytics Database 17.20.
* Bug fix: BYOM scoring recipe: Performance improvement by directly routing the scoring output to the database.

## Version 2.1.2 (eFix - October 2022)

* Bug fix: Analytic functions recipe: A naming mismatch caused errors when executing functions that use the "Number Of Splits" argument.
* Bug fix: BYOM scoring recipe: Now correctly uses the name of a Vantage table to reference the testing Dataset instead of the Dataiku Dataset name.
* Bug fix: BYOM model export recipe: Now correctly addresses the scenario where a user might choose a connection whose credentials mode is “per user”.

## Version 2.1.1 (eFix - October 2022)

* Bug fix: Analytic Functions recipe: Output Dataset is now fully qualified with database so that it can be different from the input Dataset database.
* Bug fix: Analytic Functions recipe: Execution of VAL functions now takes place on the input Dataset server.

## Version 2.1.0 (August 2022)

* Support for VAL functions.
* Merging of Analytic and VAL functions into single recipe.
* Code refactoring in the Analytic Functions recipes.
* Renaming of "SCRIPT Table Operator Analysis" recipe into "In-Vantage Scripting".
* Bug fixes.

## Version 2.0.0 (June 2022)

* Integration of all former plugins into the unified Teradata plugin.
* Code refactoring in the Analytic Functions recipes.
* Bug fixes.
* Interface update for the SCRIPT Table Operator Analysis recipe.
* Alignment with Dataiku plugin development guidelines.

## Version 1.0.0 / 0.2.3 (December 2021)

* Initial release of BYOM recipes bundled as the former Teradata BYOM plugin for Dataiku.

## Version 0.2.2 (July 2021)

* First officially supported release; features the Teradata Analytics Database Functions and SCRIPT Table Operator plugins.
