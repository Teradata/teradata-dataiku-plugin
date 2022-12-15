# Teradata Plugin Changelog

## Version 2.2.0 (December 2022)

Current version

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

* First officially supported release; features the Teradata Advanced SQL Engine Functions and SCRIPT Table Operator plugins.
