/**
 * Copyright © 2019 by Teradata.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
 * associated documentation files (the "Software"), to deal in the Software without restriction,
 * including without limitation the rights to use, copy, modify, merge, publish, distribute,
 * sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or
 * substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
 * NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 * DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

(function (window, document, angular, $) {

  if (typeof window === 'undefined' || !window) {
    throw new Error('DOM Window not present!')
  } else if (typeof document === 'undefined' || !document) {
    throw new Error('DOM Document not present!')
  } else if (typeof angular === 'undefined' || !angular) {
    throw new Error('Angular library not present!')
  } else if (typeof $ === 'undefined' || !$) {
    throw new Error('jQuery library not present!')
  }

  const app = angular.module('teradata_sqle.module', []);

  app.controller('TeradataVantageController', function ($scope, $timeout) {

    // SAROOP_DONE: Declare flag set it false
    var isBackendDictReady = false;

    /**
     * A wrapper function that delays execution so that
     * the Angular rendering cycle will have finished before
     * running the given function f.
     */
    const $delay = f => $timeout(f, 100);
    
    const $twicedelay = g =>$timeout(g,200);

    /**
     * Default separator for list-like objects.
     */
    const SEPARATOR = String.fromCharCode(0);

    /**
     * A private variable containing the function metadata.
     */
    let functionMetadata;

    /**
     * A private variable containing the function metadata.
     */
    let functionVersion = '';
    let functionType = '';

    /**
     * A private variable containing the function to run the given recipe.
     */
    let runFunction;

    /**
     * Dialog container.
     */
    const $dialog = $('#dialog');

    /**
     * Validation dialog container.
     */
    const $validationDialog = $('#dialog-validation');

    /**
     * Function metadata path - this path contains the JSON metadata of each function.
     */
    const FUNCTION_METADATA_PATH = '/plugins/Teradata/resource/data/';

    /**
     * Parameters to use for the dialog box.
     */
    const DIALOG_PARAMETERS = {
      modal: true,
      width: '33%',
      minHeight: 250,
    }

    /**
     * Parameters to use for the dialog box CSS.
     */
    const DIALOG_CSS_PARAMETERS = {
      'max-height': '70vh',
      overflow: 'auto'
    }

    /**
     * Number of milliseconds per listen interval.
     */
    const LISTEN_INTERVAL = 50;

    /**
     * Object keys that are repeatedly used in this script.
     */
    const KEYS = {
      LONG_DESCRIPTION: 'long_description',
      ALTERNATE_NAMES: 'alternateNames',
      TARGET_TABLE: 'targetTable',
      INPUT_TABLE: 'INPUTTABLE',
      INPUT_TABLE_ALTERNATIVE: 'INPUT_TABLE'
    }

    const ARGUMENT_TITLES = {
      // HASH_BY: 'A HASH BY clause will cause the rows in the ON clause to be redistributed to AMPs based on the hash value of the column(s) specified',
      HASH_BY: 'The HASH BY clause groups table rows by the values of the specified column names, and distributes all rows of each group to a Analytics Database Access Module Processor (AMP; processing unit). Specify the column names you would like to hash their values by. If you specify a HASH BY clause, then you can also optionally order each group rows with the LOCAL ORDER BY clause.',
      // PARTITION_BY: 'A PARTITION BY clause will cause the STO to be executed against specific groups (partitions) based on the column(s) specified',
      PARTITION_BY: 'Specify column names for the partition task. Use one field per column. Click on the [+] button to add fields. Click on the [-] button next to a field to delete it.',
      // ORDER_BY: 'An ORDER BY clause specifies the order in which values in a group (partition) are sorted',
      ORDER_BY: '[Optional] Specify column names to use their data for row ordering in the partition groups. Use one field per column. Click on the [+] button to add fields. Click on the [-] button next to a field to delete it.',
      // LOCAL_ORDER_BY: 'A LOCAL ORDER BY clause  orders the rows qualified on each AMP',
      LOCAL_ORDER_BY: 'The LOCAL ORDER BY clause provides ordering of the input table rows in the groups created with the HASH BY clause. The LOCAL ORDER BY clause can be only specified when you have specified a HASH BY clause, too.',
      // RETURNS_NAME: 'Specifies the name of the column(s) to be returned by the STO',
      RETURNS_NAME: 'Specify a name for each output argument returned by your recipe.',
      // RETURNS_TYPE: 'Specifies the data type of the column(s) to be returned by the STO',
      RETURNS_TYPE:'Check the box to include this variable in the Dataiku output dataset.',
      // SELECT_CUSTOM: 'Determines whether the SELECT (output) columns (data to be returned by the query) should be modified. Default is to SELECT all column(s) in the RETURNS clause',
      SELECT_CUSTOM: 'The default SELECT clause used by the plugin selects all output arguments of your recipe. Use this option determines whether to modify the default SELECT behavior.',
      // SELECT_COLUMNS: 'Specifies the contents of a user customized SELECT statement (data to be returned by the query)',
      SELECT_COLUMNS: 'Specify explicitly the contents of the SELECT clause.',
      INPUTS: '[Optional] If you leave blank, then your recipe receives as input all columns in the recipe input dataset. If your recipe requires only specific columns from the recipe input dataset, then click on the [+] button to add fields and specify the column names needed by your recipe. Specify one column name per field in the order your recipe expects them. Click on the [-] button next to a field to delete it.',
      SEQUENCING_TYPE:'Select the order sequencing for the present column.',
      WHERE:'[Optional] Specify in SQL format any conditions that your input data must satisfy (note: This option corresponds to using the WHERE clause in SQL).',
      OUTPUT_COLUMN: 'Check the box to include this variable in the Dataiku output dataset.',
      OUTPUT_ALL: 'By default, all output variables of your recipe are included in the recipe Dataiku output dataset. To include only select variables, check the corresponding boxes next to the variables you want to include.',
      DATA_PARTITION_TYPE: 'If other than None, the recipe will execute with different data partitions. The column values option determines partitioning by means of different values in one or more columns (note: This option corresponds to using the PARTITION BY clause in SQL). The Hash option partitions data in a different way, where data are distributed to Database AMPs based on AMP hash values in one or more columns (note: This option corresponds to using the HASH BY clause in SQL).'
   
    }


    /** Regex for locating HTML entities. */
    const ENTITY_REGEX = /[\u00A0-\u9999<>\&]/gim

    /** Properly encodes an HTML entity. */
    function encodeRegex(i) {
      return '&#' + i.charCodeAt(0) + ';';
    }
    var debug = false;
    function console_log(msg){
      if (debug)
        console.log(msg);
    }

    $.extend($scope, {
      getToolTip: function(key) { return ARGUMENT_TITLES[key];},
      /**
       * Shows a dialog.
       * 
       * This is for displaying Aster-side errors.
       */
      dialog: function (title, content, elem) {

        // [HACK] Sometimes, the title is "error" because of timing issues.
        // So we force it to succeed if the content is "Job succeeded".
        if (content === 'Job succeeded.') {
          title = 'Success'
        }

        $dialog.find('pre').text(content);
        $(elem).click(() => $('.ui-dialog-content').dialog('close'));
        $dialog.find('.other').empty().append(elem);

        $dialog
          .attr('title', title)
          .dialog(DIALOG_PARAMETERS);

        $dialog.css(DIALOG_CSS_PARAMETERS);

      },

      /**
       * Shows a dialog.
       * 
       * This is for displaying frontend validation errors.
       */
      validationDialog: function (html) {

        $validationDialog.find('div').html(html);
        $validationDialog.dialog(DIALOG_PARAMETERS);
        $validationDialog.css(DIALOG_CSS_PARAMETERS);

      },

      /**
       * Gets the static JSON metadata of the given function.
       */
      getFunctionMetadata: function (selectedFunction, shouldSetDefaults) {
        console_log("Getting function metadata.")

        if (typeof selectedFunction === 'undefined') {
          return;
        }

        // this code is if you only want the backend to be loaded by the UI
        if(isBackendDictReady == false)
          return;

        // Get JSON from dictionary
        var numChoices = $scope.choices.length;
        var data = undefined;
        var i = 0;
        var choice = undefined;
        for(i=0; i<numChoices; ++i) {
          // Find the choice for the selectedFunction 
          choice = $scope.choices[i]
          if(selectedFunction  == choice["function_alias_name"]) {
              // Check if it has original_json
              if("json_contents" in choice) {
                  // If it does have original_json, just use that for the data
                  data = choice["json_contents"]
                  break 
              }
              break
          }
        }

        // If JSON contents are not available then call python to load the JSON contents
        if(data == undefined) {
          var json_path = choice["json_file_path"]
          $scope.callPythonDo({"load_json":json_path}).then(
                    data => {
                          var result = data['result'];
                          // Update the dictionary
                          for(let key in result) {
                              if(key == "name" || key == "function_alias_name")
                                continue;
                              $scope.choices[i][key] = result[key]
                              if($scope.config.function[key] == undefined)
                                $scope.config.function[key] = result[key]
                          }
                          
                          data = $scope.choices[i]["json_contents"]
                          $scope.updateUiBasedOnJsonContents(data, selectedFunction, shouldSetDefaults)
                          // SKS: activate the UI (copied from original code path)
                          $scope.preprocessMetadata(false);
                          // Update current function name in UI
                          $("#current_function_name").val($scope.config.function.name);
                          $scope.activateUi();
                        },
                  () => { }
                  ).then(
                    () => { 
                            // Do nothing
                          },
                    () => {}
                  );
          return
        }

        if(data == undefined) {
          $('<div></div>').dialog({
                  modal: true,
                  width: 400,
                  height: 220,
                  title: "Error",
                  open: function() {
                    var markup = "<b style='color:red;'> Could not find " + selectedFunction + ". Your plugin may need to be updated to a later version.</b>";
                    $(this).html(markup);
                  },
                  buttons: {
                    Ok: function() {
                      $( this ).dialog( "close" );
                    }
                  }   
              }).css("font-size", "12px"); 
            return;
        }

        // JSON contents were available so load 
        $scope.updateUiBasedOnJsonContents(data, selectedFunction, shouldSetDefaults)

      },

  updateUiBasedOnJsonContents: function (data, selectedFunction, shouldSetDefaults) {
        
        // strip json vulnerability protection prefix
        data = data.replace(")]}',\n", '');
        data = data.replace(/: Infinity/g, ': "Infinity"');
        data = data.replace(/: -Infinity/g, ': "-Infinity"');             
        // WARNING DANGEROUS STRING REPLACEMENT
        data = data.replace(/NaN(?!.*")/g,'"NaN"')  
        // data = data.replace(/^\t|\s*\-NaN/g, '"-NaN"');
        // console_log(JSON.stringify({ "x" : NaN }, undefined, 2));
        // data = data.replace(/^\t|\s*NaN/g, '"NaN"');             
        data = JSON.parse(data, function censor(key, value) {
              value == Infinity ? "Infinity" : value;
              value == NaN ? "NaN" : value;
              return value
        });
        // data = JSON.parse(data, function censor(key, value) {
        //   return value == NaN ? "NaN" : value;
        // });
        console_log(data)

        functionMetadata = data;
        
        functionVersion = functionMetadata.function_version;
        // PARTITION BY BLANK
        $scope.config.function.partitionAttributes = $scope.config.function.partitionAttributes || [''];
        $scope.config.function.orderByColumn = $scope.config.function.orderByColumn || [''];
        // $scope.config.function.orderByColumnDirection = $scope.config.function.orderByColumnDirection || []
        
        // Store the function type
        if(data.function_type == undefined) {
          $scope.config.function_type = "sql"
        }
        else {
          $scope.config.function_type = data.function_type
          
        }


        $scope.preprocessDescriptions();
        $scope.preprocessMetadata(shouldSetDefaults);
        $scope.activateTabs();
        $scope.activateMultiTagsInput();
        $scope.activateTooltips();

      },

      /**
       * Preprocesses the descriptions so that the special characters are correctly rendered.
       */
      preprocessDescriptions: function () {

        if (!functionMetadata || !functionMetadata.argument_clauses)
          return;

        functionMetadata.argument_clauses.forEach(
          x => {
            try {

              x.description = x.description
                ? x.description.replace(ENTITY_REGEX, encodeRegex)
                : ''

            } catch (e) { }
          }
        )

      },

      /**
       * Gets the function description from the static JSON metadata.
       */
      getFunctionDescription: function () {
        return (functionMetadata && KEYS.LONG_DESCRIPTION in functionMetadata) ?
          functionMetadata.long_description :
          '';

      },

      multiColumnNamesCheck: function(item){
        var result = (item.datatype == 'COLUMN_NAMES' || item.datatype == 'COLUMNS') && item.allowsLists;
        // if (result && (item.value == null || item.value == "")){
        //   item.value = [""];
        // }
        // console_log('Multi check');
        // console_log(item.name);
        // console_log(result);
        return result;
      },

      resetSelectToStar() {
        
        $scope.config.function.select_clause = '*';
 
      },

      /**
       * Checks if there is a version mismatch in function_version
       */
      // checkVersionMismatch: function () {
    	//   if (!$scope.config.function) {
      //       return false;
      //       }
      //   var previousVersion = $scope.config.function.function_version ? $scope.config.function.function_version : '';
      //   console_log($scope.config.function.function_version ? $scope.config.function.function_version : '');
      //   // console_log(functionVersion);
      //   if (($scope.config.function.function_version ? $scope.config.function.function_version : '') === functionVersion || ($scope.config.function.function_version ? $scope.config.function.function_version : '') === '') {
      //     console_log('False');
      //     return false;
      //   } else {
      //     console_log('True')
      //     console.warn('Function version mismatch');
      //     console.warn('Previous Version:', previousVersion)
      //     console.warn('Installed Version:', functionVersion)
      //     return true;
      //   }
      // },
      addPartitionByColumn_TEST: function(partitionArray) {
        // console_log('Partition array type');
        // console_log(typeof partitionArray);
        // console_log(partitionArray);
        if(typeof partitionArray == undefined || typeof partitionArray == 'string'){
          // console_log('Originally undefined/string');          
          partitionArray = [];
          // console_log(partitionArray)
          partitionArray.push('');
          // console_log(partitionArray)
          
        } else {          
          partitionArray.push('');
          // console_log('Added to partition array');
          // console_log(partitionArray);
          
        
        }
    },
    

    addColumnArgument: function(item) {
      console_log('Adding value to array');
      console_log(item.name);
      console_log(item.value);
      item.value.push("");
    },

    removeColumnArgument: function(item, index) {
      if (index > -1) {
          item.value.splice(index, 1);
      }
  },

  addAdditionalSQLClause: function() {    
    if($scope.config.function.additionalSQLClause == null){
      $scope.config.function.additionalSQLClause = [""];
    } else{ 
      $scope.config.function.additionalSQLClause.push("");
    }
    
  },

  removeAdditionalSQLClause: function(index) {
    if (index > -1) {
      $scope.config.function.additionalSQLClause.splice(index, 1);
    }
},
  
    initializeColumnArray: function(columnArray){
      columnArray = columnArray || [''];
      return columnArray;
    },

    initializeColumnArrayOptional: function(columnArray){
      // MOdified this too
      columnArray = columnArray || [''];
      return columnArray;
    },
    
    removePartitionByColumn_TEST: function(partitionArray,index) {
      if (index > -1) {
        // console_log('Removed from partition array')
        // console_log(partitionArray)
        partitionArray.splice(index, 1);
      }
    },

    addPartitionByColumn: function() {
      // console_log('Added one column')
      $scope.config.function.partitionAttributes.push('');
  },
  removePartitionByColumn: function(index) {
    if (index > -1) {
        $scope.config.function.partitionAttributes.splice(index, 1);
    }
  },

  addOrderByColumn: function() {
    // console_log('Added one column')
    $scope.config.function.orderByColumn.push('');
    $scope.config.function.orderByColumnDirection.push('');
  },
  removeOrderByColumn: function(index) {
    if (index > -1) {
      $scope.config.function.orderByColumn.splice(index, 1);
      $scope.config.function.orderByColumnDirection.splice(index, 1);
    }
  },

  addOrderByColumn_WITHDIR: function(orderArray, orderDirArray) {
    // console_log('Partition array type');
    // console_log(typeof orderArray);
    // console_log(orderArray);
    if(typeof orderArray == undefined || typeof orderArray == 'string'){
      // console_log('Originally undefined/string');          
      orderArray = [];
      // console_log(orderArray)
      orderArray.push('');
      // console_log(orderArray)
      
    } else {          
      orderArray.push('');
      // console_log('Added to partition array');
      // console_log(partitionArray);         
    }
    // DIRECTION
    if(typeof orderDirArray == undefined || typeof orderDirArray == 'string'){               
      orderDirArray = [];        
      orderDirArray.push('');
      
      
    } else {          
      orderDirArray.push('');
      // console_log('Added to partition array');
      // console_log(partitionArray);         
    }
},
removeOrderByColumn_WITHDIR: function(orderArray, orderDirArray, index) {
  if (index > -1) {
    // console_log('Removed from partition array')
    // console_log(orderArray)
    orderArray.splice(index, 1);
    orderDirArray.splice(index, 1);
  }
},
      validityChanger: function () {
        $('div.ng-invalid').removeClass('ng-invalid')
        $('div.invalid').addClass('ng-invalid')
        return true;
      },

      /**
       * Checks if function is a driver function
       */
      checkIfDriverFunction: function () {
        // Move check above with IF statement and IF FALSE, set recipe output = ""
          return functionMetadata && functionMetadata.output_tables &&
              functionMetadata.output_tables.filter(arg => arg.isOutputTable).length;
      },

      /**
       * Checks if argument has Native JSON
       */
      hasNativeJSON: function (functionName) {          
        if (functionName == null || functionName == "") {
          return false;
        }
        // console_log('functionName');
        // console_log(functionName);
        var filteredChoices = $scope.choices.filter(choice => choice.name == functionName);      
        // console_log(filteredChoices);        
        if(filteredChoices[0].hasNativeJSON == false){
          $scope.config.function.useCoprocessor = true;
        }
        return filteredChoices[0].hasNativeJSON;
    },

    useNativeOrNot: function(inNative){
      // console_log('useNativeOrNot')
      // console_log($scope.config.function.useCoprocessor)
      // console_log(inNative)
      // if()
      return true;

    },

    refreshTeraTabs: function(){
      
      // $delay(() => {$scope.activateMultiTagsInput();
      $scope.activateMultiTagsInput();
     //this line is to watch the result in console , you can remove it later	
      console_log("Refreshed");
    // }) 
    },


      /**
       * Gets the description of the given argument from the static JSON metadata.
       */
      getArgumentDescription: function (i) {

        try {

          return (functionMetadata && functionMetadata.argument_clauses[i])
            ? functionMetadata.argument_clauses[i].description
            : null;

        } catch (e) {

          return null

        }

      },
         

      // SKS: Version Dialog
      showVersionDialog: function() {
           $('<div></div>').dialog({
                modal: true,
                width: 700,
                title: "Version Information",
                open: function() {
                  var markup = $scope.versionInfo;
                  $(this).html(markup);
                },
                buttons: {
                  Ok: function() {
                    $( this ).dialog( "close" );
                  }
                }   
            });  //end confirm dialog
      },

       // SKS: JSON Dialog
      showJSONDialog: function() {
           $('<div></div>').dialog({
                modal: true,
                width: 600,
                height: 400,
                title: "Open-ended Input JSON",
                open: function() {
                  var markup = JSON.stringify($scope.config, undefined, 4);
                  markup = '<pre>' + markup + '</pre>' 
                  $(this).html(markup);
                },
                buttons: {
                  Ok: function() {
                    $( this ).dialog( "close" );
                  }
                }   
            });  //end confirm dialog
      },

      // SKS: Query Dialog
      showQueryDialog: function() {
          $scope.callPythonDo({"query":true}).then(
                    data => {
                            $('<div></div>').dialog({
                                modal: true,
                                width: 600,
                                height: 400,
                                title: "SQL Query",
                                open: function() {
                                  var markup = data['result'];
                                  markup = markup.replaceAll("{", '<i class="keyword2">&#123;')
                                  markup = markup.replaceAll("}", '&#125;</i>')
                                  markup = markup.replaceAll(/\bCREATE TABLE\b/g, '<b class="keyword1">CREATE TABLE</b>');
                                  markup = markup.replaceAll(/\bSELECT\b/g, '<b class="keyword1">SELECT</b>');
                                  markup = markup.replaceAll(/\bFROM\b/g, '<b class="keyword1">FROM</b>');
                                  markup = markup.replaceAll(/\bPARTITION BY\b/g, '<b class="keyword2">PARTITION BY</b>');
                                  markup = markup.replaceAll(/\bHASH BY\b/g, '<b class="keyword2">HASH BY</b>');
                                  markup = markup.replaceAll(/\bLOCAL ORDER BY\b/g, '<b class="keyword2">LOCAL ORDER BY</b>');
                                  markup = markup.replaceAll(/\bORDER BY\b/g, '<b class="keyword2">ORDER BY</b>');
                                  markup = markup.replaceAll(/\bDIMENSION\b/g, '<b class="keyword1">DIMENSION</b>');
                                  markup = markup.replaceAll(/\bWHERE\b/g, '<b class="keyword1">WHERE</b>');
                                  markup = markup.replaceAll(/\bHAVING\b/g, '<b class="keyword1">HAVING</b>');
                                  markup = markup.replaceAll(/\bQUALIFY\b/g, '<b class="keyword1">QUALIFY</b>');
                                  markup = markup.replaceAll(/\bGROUP BY\b/g, '<b class="keyword1">GROUP BY</b>');
                                  markup = markup.replaceAll(/\bSAMPLE\b/g, '<b class="keyword1">SAMPLE</b>');
                                  markup = markup.replaceAll(/\bWITH DATA\b/g, '<b class="keyword1">WITH DATA</b>');
                                  markup = markup.replaceAll(/\bUSING\b/g, '<b class="keyword1">USING</b>');
                                  markup = markup.replaceAll(/\bON\b/g, '<b class="keyword2">ON</b>');
                                  markup = markup.replaceAll(/\bAS\b/g, '<b class="keyword2">AS</b>');
                                  markup = markup.replaceAll(/\bCALL\b/g, '<b class="keyword1">CALL</b>');
                                  markup = markup.replaceAll('\n', '<br>');
                                  $(this).html(markup);
                                },
                                buttons: {
                                  Ok: function() {
                                    $( this ).dialog( "close" );
                                  }
                                }   
                            }).css("font-size", "12px"); 

                        },
                  () => { }
                  ).then(
                    () => { 
                            // Do nothing
                          },
                    () => {}
                  );

         

           
      },



      // SKS: Explanation Dialog
      showExplainDialog: function() {
          $scope.callPythonDo({"explain":true}).then(
                    data => {
                            $('<div></div>').dialog({
                                modal: true,
                                width: 600,
                                height: 400,
                                title: "Explanation of SQL",
                                open: function() {
                                  var markup = data['result'];
                                  markup = markup.replaceAll('\n', '<br>');
                                  $(this).html(markup);
                                },
                                buttons: {
                                  Ok: function() {
                                    $( this ).dialog( "close" );
                                  }
                                }   
                            }).css("font-size", "12px"); 

                        },
                  () => { }
                  ).then(
                    () => { 
                            // Do nothing
                          },
                    () => {}
                  );

         

           
      },

      getArgumentWithName: function (name) {
          return (functionMetadata && functionMetadata.argument_clauses) ?
                  functionMetadata.argument_clauses.find(argument => (argument.
                          name.toUpperCase() === name.toUpperCase()) ||
                          (argument.alternateNames && argument.alternateNames.
                                  findIndex(x=> x.toUpperCase() === name.toUpperCase() ) != -1)) :
                      null;
      },

      // SKS : Added way to get upper and lower bounds
      getLowerBoundValuesWithName: function (item) {
          let name = item.name;
          let argument = $scope.getArgumentWithName(name);
          if (argument) {
            if (argument.lowerBound.toString().toLowerCase().indexOf("infinity") != -1)
              return "-1000000";
            return argument.lowerBound.toString();
          }
          return "-1000000";
      },
      getUpperBoundValuesWithName: function (item) {
          let name = item.name;
          let argument = $scope.getArgumentWithName(name);
          if (argument) {
            if (argument.upperBound.toString().toLowerCase().indexOf("infinity") != -1)
              return "1000000";
            return argument.upperBound.toString();
          }
          return "1000000";
      },
      getStepRangeValuesWithName: function (item) {
          let name = item.name;
          let argument = $scope.getArgumentWithName(name);
          if (argument) {
            if (argument.lowerBound.toString().toLowerCase().indexOf("infinity") != -1)
              return "0.01";
            if (argument.upperBound.toString().toLowerCase().indexOf("infinity") != -1)
              return "0.01";
            return ((argument.upperBound-argument.lowerBound)/100.0).toString();
          }
          // Set the step size to have 100 intervals
          return "0.01";
      },

      // SKS: Added Default Value
      getDefaultValueWithName: function (item) {
        let name = item.name;
          let argument = $scope.getArgumentWithName(name);
          if (argument && argument.defaultValue !== undefined)
            return argument.defaultValue;
          else
            return "";
      },


      getPermittedValuesWithName: function (item) {
    	  let name = item.name;
          let argument = $scope.getArgumentWithName(name);
          let permittedvalues = argument && argument.permittedValues && argument.permittedValues.length ?
        		  argument.permittedValues : null;
          //if (permittedvalues && item.allowsLists && (typeof item.value === 'string')) {
        	//  item.value = item.value.split(',');
          //}
          return permittedvalues;
      },


      validateColumnName: function (item, value, schema) {
        for(var i in schema) {
            if(schema[i].name == value) {
              return value;
            }
        }
        // Column Name not found
        return ""
      },

      getArgumentDescriptionWithName: function (name) {
          let argument = $scope.getArgumentWithName(name);

          // SKS: Add Upper/Lower Bound to description
          if (argument && ['DOUBLE','INTEGER', 'LONG', 'DOUBLE PRECISION'].indexOf(argument.datatype) >= 0 && argument.lowerBound != undefined && argument.upperBound != undefined) {
            return argument.description + "</br>" + "<p style='color:red;'> Lower bound="+argument.lowerBound+ "</br>Upper Bound="+argument.upperBound +"</p>"
          }

          return argument ? argument.description : null;
      },

      getArgumentFormattedName: function (name) {
          let argument = $scope.getArgumentWithName(name);
          return argument ? argument.name.replace(/([A-Z]+)/g, " $1")
                  .replace(/([A-Z][a-z])/g, " $1").split('_').join(' ')
                  : name;
      },

      getPermittedValues: function (i) {

        try {
          return (functionMetadata
            && functionMetadata.argument_clauses[i]
            && functionMetadata.argument_clauses[i].permittedValues
            && functionMetadata.argument_clauses[i].permittedValues.length)
            ? functionMetadata.argument_clauses[i].permittedValues
            : null;

        } catch (error) {

          return null;

        }


      },

      /**
       * Gets the schema of the unaliased inputs from the static JSON metadata.
       */
      getSchemaOfUnaliasedInputs: function (unaliasedInputsList) {

        if (!unaliasedInputsList
          || !unaliasedInputsList.values
          || !unaliasedInputsList.values.length)
          return [];

        const targetTableName = unaliasedInputsList.values[0];

        return $scope.inputschemas
          && targetTableName
          && targetTableName in $scope.inputschemas
          ? $scope.inputschemas[targetTableName]
          : []

      },

      findTableNameInArgumentsList: function (argumentsList, tableNameAlias) {
        //Get alternate names
        var tableNameAliases = [];
        // tableNameAliases.push(tableNameAlias);
        
        tableNameAliases = tableNameAlias;
        if (!functionMetadata) {
          return [''];
        }
        functionMetadata.argument_clauses.map(argument => {
          if (argument.name.toUpperCase() === tableNameAlias) {
            if (KEYS.ALTERNATE_NAMES in argument) {
              argument.alternateNames.map(function (altname) { tableNameAliases.push(altname); })
            }
          }
        })
        let potentialMatches = argumentsList
          .filter(arg => tableNameAliases.includes(arg.name.toUpperCase()));
        if (potentialMatches.length) {
          if (tableNameAlias.length > 1) {
            return potentialMatches.map(function (match) {
              return match.value
            });
          } else {
            return [potentialMatches[0].value];
          }
        }
        return ['']

      },

      // Opens tabs
      openTabs: function(evt, tabName) {
        // Declare all variables
        var i, tabcontent, tablinks;
        // console_log(evt); 
        // Get all elements with class="tabcontent" and hide them
        tabcontent = document.getElementsByClassName("plugintabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
    
        // Get all elements with class="tablinks" and remove the class "active"
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
    
        // Show the current tab, and add an "active" class to the button that opened the tab
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.className += " active";
    },
    
    initTab:function(){
      $delay(() => {console_log('InitTab Happens');
      document.getElementById("defaultOpen").click();
      });
    },
      /**
       * Gets the function schema by joining and processing the metadata from the python backend 
       * and the static JSON file associated with the function.
       */
      getSchema: function (functionArgument, aliasedInputsList, unaliasedInputsList, argumentsList) {
        console_log('Get Schema runs');
        aliasedInputsList = aliasedInputsList || []
        argumentsList = argumentsList || []
        // console_log('getSchema');
        // console_log(functionMetadata)
        // console_log(functionArgument);
        // console_log(aliasedInputsList);
        // console_log(unaliasedInputsList);
        // console_log(argumentsList);
        const hasTargetTable = KEYS.TARGET_TABLE in functionArgument
        let targetTableName = ''
        var isAliasedInputsPopulated;
        var isInAliasedInputsList = false;
        // Alternate name variables
        var isInAlternateNames = false;
        var alternateNameIndex = 0;
        var alternateNameOriginalName = '';
        var y = false;
        if (hasTargetTable) {
          var targetTableAlias;
          if (typeof functionArgument.targetTable === 'string') {
            targetTableAlias = [(functionArgument.targetTable || '').toUpperCase()];
            console_log('Table name');
            console_log(targetTableAlias);
          } else {
            targetTableAlias = functionArgument.targetTable.map(function (table_name) {

              return (table_name || '').toUpperCase();
            })
            console_log('Table name');
            console_log(targetTableAlias);
          }

          // if (KEYS.ALTERNATE_NAMES in func)
          // var tableAliasList = 

          // const isAliased = KEYS.INPUT_TABLE !== targetTableAlias;
          
          if (aliasedInputsList !== []) {
            isAliasedInputsPopulated = true;
            console_log('Into Alias Inputs');
            aliasedInputsList.map((input) => {
              // if (input.name.toUpperCase() === targetTableAlias.toUpperCase()) {
              if (targetTableAlias.includes(input.name.toUpperCase())) {
                console_log('Alias inputs true');
                isInAliasedInputsList = true;
              }
              // Test code
              console_log('Alternate names');
              console_log(input.alternateNames);    
              console_log(input.name)
              console_log(input)
              if(input.alternateNames != [] && input.alternateNames != undefined){        
                console_log("Got in");        
                console_log(input.alternateNames)
                for (var altNameIndex=0;altNameIndex<input.alternateNames.length;altNameIndex++ ){
                  console_log('Table Alternate name\n');
                  console_log(input.alternateNames[altNameIndex].toUpperCase());
                  console_log(targetTableAlias)
                  if(targetTableAlias.includes(input.alternateNames[altNameIndex].toUpperCase())){
                    console_log('includes alternate')
                    isInAliasedInputsList = true;
                    isInAlternateNames = true;
                    alternateNameIndex = altNameIndex;
                    alternateNameOriginalName = input.name.toUpperCase();
                  }
                }
              }
            }
            )
          } else {
            isInAliasedInputsList = false;
            console_log('Not in alias input anymore');
          }
          // const isAliased = aliasedInputsList.includes(targetTableAlias);
          const isAliased = isInAliasedInputsList;
          //console_log(KEYS.INPUT_TABLE);
          //console_log(targetTableAlias);
          // console_log('Aliased Inputs List Check');
          // console_log(aliasedInputsList);
          if (isAliased) {
            console_log('isAliased');
            // let matchingInputs = aliasedInputsList.filter(input => targetTableAlias === input.name.toUpperCase());
            let matchingInputs = aliasedInputsList.filter(input => targetTableAlias.includes(input.name.toUpperCase()));
            if (matchingInputs.length > 0) {
              //console_log('Matching inputs > 0');
              // targetTableName = matchingInputs[0].value;
              // matchingInputs[targetTableAlias.length - 1].value
              if(isInAlternateNames){
                  let matchingInputsAlt = aliasedInputsList.filter(input => input.alternateNames.some(r=> targetTableAlias.includes(r.toUpperCase())));
                  console_log(matchingInputsAlt)
                  if (matchingInputsAlt.length > 0) {               
                    // targetTableNameAlt = matchingInputsAlt.map(function(input) {
                    //   return input.value
                    // });
                    console_log("matching");
                    console_log(matchingInputs);
                    console_log(matchingInputsAlt)
                    matchingInputs = matchingInputs.concat(matchingInputsAlt);
                   }
              }
              targetTableName = matchingInputs.map(function(input) {
                return input.value
              });
            } else if (matchingInputs == 0 && isInAlternateNames){ //Alternate names additional code
              // console_log('Is in alternates and matching was 0')
              let matchingInputs = aliasedInputsList.filter(input => input.alternateNames.some(r=> targetTableAlias.includes(r.toUpperCase())));
              // console_log(matchingInputs)
              if (matchingInputs.length > 0) {               
                targetTableName = matchingInputs.map(function(input) {
                  return input.value
                });
              }
            } else {
              //console_log('Matching inputs < 0');
              // console_log('Does Matching <= 0 happen?')
              targetTableName = $scope.findTableNameInArgumentsList(argumentsList, targetTableAlias);
            }


          } else {
            //console_log('isNotAliased');
            //console_log(unaliasedInputsList);
            if (unaliasedInputsList.count && unaliasedInputsList.values && unaliasedInputsList.values.length) {
              // console_log('Went to unaliased');

              targetTableName = [unaliasedInputsList.values[0]];
              //console_log(targetTableName);
            }

            else {
              targetTableName = $scope.findTableNameInArgumentsList(argumentsList, targetTableAlias);
              // console_log('Went to arguments');
              // console_log(targetTableName);
            }


          }

        } else if (unaliasedInputsList.values && unaliasedInputsList.values.length > 0) {

          targetTableName = [unaliasedInputsList.values[0]];
          //console_log('This else if');
          //console_log(targetTableName);

        }

        if (!targetTableName || !$scope.inputschemas) {
          //console_log('This happened');
          //console_log(targetTableName);
          //console_log($scope);
          return [];
        }


        if (targetTableName) {
          //console_log('Schemas');
          //console_log($scope.inputschemas[targetTableName]);
          var forReturnInputSchemas = [];
          for (var i = 0; i < targetTableName.length; i++) {
            if (targetTableName[i] in $scope.inputschemas) {
              var currentInputSchemas = $scope.inputschemas[targetTableName[i]]
              currentInputSchemas = currentInputSchemas.map(function (eachInput) {
                return $.extend(eachInput, { "tableName": targetTableName[i] });
              })
              // console_log('Current');
              // console_log(currentInputSchemas);
              forReturnInputSchemas.push.apply(forReturnInputSchemas, currentInputSchemas)
            }
          }
          // console_log('Schema');
          // console_log(forReturnInputSchemas)
          return forReturnInputSchemas;

        }

        return $scope.schemas;

      },

      /**
       * Checks whether or not we should show the partition order fields.
       * 
       * NOTE: Temporary code to not show partition 
       * and order by fields when there are no unaliased input dataset
       */
      shouldShowPartitionOrderFields: function (unaliasedInputsList) {
        return unaliasedInputsList && unaliasedInputsList.count > 0;
      },

      /**
       * Checks whether or not the given argument is an output table or not.
       */
      isArgumentOutputTable: function (functionArgument) {
        return functionArgument.isOutputTable
      },

      /**
       * Checks whether or not required arguments are present in the function metadata.
       */
      hasRequiredArguments: function () {

        if (!$scope.config.function.arguments || !$scope.config.function.arguments.length)
          return false
        
        const hasRequiredArgument = $scope.config.function.arguments.filter(x => x.isRequired).length > 0
        const hasRequiredOutputTable = $scope.config.function.output_tables.filter(x => x.isRequired).length > 0
        return hasRequiredArgument || hasRequiredOutputTable

      },

      /**
       * Checks whether or not optional arguments are present in the function metadata.
       */
      hasOptionalArguments: function () {

        const hasOptionalInputTable = $scope.config.function.required_input
          && $scope.config.function.required_input.length
          && ($scope.config.function.required_input.filter(x => !x.isRequired).length > 0);

        const hasOptionalArgument = $scope.config.function.arguments
          && $scope.config.function.arguments.length
          && ($scope.config.function.arguments.filter(x => !x.isRequired).length > 0)
          && ($scope.config.function.useCoprocessor || ($scope.config.function.arguments.filter(x => x.inNative && !x.isRequired).length > 0));
          // console_log('hasOptionalArguments');
          // console_log($scope.config.function.useCoprocessor);
          // console_log(($scope.config.function.arguments.filter(x => x.inNative).length > 0));
          const hasOptionalOutputTable = $scope.config.function.output_tables
          && $scope.config.function.output_tables.length
          && ($scope.config.function.output_tables.filter(x => !x.isRequired).length > 0);
        // console_log(hasOptionalInputTable);
        // console_log(hasOptionalArgument);
        // console_log(hasOptionalOutputTable);
        return hasOptionalInputTable || hasOptionalArgument || hasOptionalOutputTable;

      },

      /**
       * Checks whether or not optional arguments are present in the partnerfunction metadata.
       */
      hasOptionalArguments_Partner: function () {

        const hasOptionalInputTable = $scope.config.function.partnerFunction.required_input
          && $scope.config.function.partnerFunction.required_input.length
          && ($scope.config.function.partnerFunction.required_input.filter(x => !x.isRequired).length > 0);

        const hasOptionalArgument = $scope.config.function.partnerFunction.arguments
          && $scope.config.function.partnerFunction.arguments.length
          && ($scope.config.function.partnerFunction.arguments.filter(x => !x.isRequired).length > 0)
          && ($scope.config.function.partnerFunction.useCoprocessor || ($scope.config.function.partnerFunction.arguments.filter(x => x.inNative && !x.isRequired).length > 0));
          // console_log('hasOptionalArguments');
          // console_log($scope.config.function.useCoprocessor);
          // console_log(($scope.config.function.arguments.filter(x => x.inNative).length > 0));
          const hasOptionalOutputTable = $scope.config.function.partnerFunction.output_tables
          && $scope.config.function.partnerFunction.output_tables.length
          && ($scope.config.function.partnerFunction.output_tables.filter(x => !x.isRequired).length > 0);
        // console_log(hasOptionalInputTable);
        // console_log(hasOptionalArgument);
        // console_log(hasOptionalOutputTable);
        return hasOptionalInputTable || hasOptionalArgument || hasOptionalOutputTable;

      },

      /**
       * A function that listens for job results.
       * It accepts a callback function f that is executed after the results are received.
       * The presence or absence of the job results are listened to 
       * by using a simple setInterval (which checks for results every 50ms).
       * 
       * NOTE: This is a hack-ish implementation because we donot know how to listen to the job results properly.
       * If Dataiku publishes a proper DOM event then we should listen to that event instead.
       * But, currently, that event is not being published.
       */
      listenForResults: function (f) {
        const listener = setInterval(() => {
          const $jobResult = $('.recipe-editor-job-result')
          if ($jobResult.length && f()) {
            clearInterval(listener);
            $jobResult.remove();
          }
        }, LISTEN_INTERVAL)
      },

      /**
       * Function that validates all the input controls of the recipe.
       * 
       * Returns true if valid. If not, it shows an error dialog then returns false.
       */
      validate: function () {

        const invalids = []
        $('.ng-invalid:not(form,.ng-hide,div,ng-disabled)').each((i, x) => invalids.push($(x).parent().prev().text()))

        if (invalids.length) {
          $scope.validationDialog(`Please amend the following fields: <ul>${invalids.map(x => `<li>${x}</li>`).join('')}</ul>`)
          return false
        }

        return true

      },

      /**
       * Function to execute the "proper" run workflow of an Aster recipe.
       * 
       * Firstly, the inputs are validated.
       * If the inputs are valid, it proceeds to the run phase 
       * which runs the original runFunction of the recipe (which we hijacked earlier).
       * It then listens for any results by using the listenForResults function.
       * Once the results are back, it displays it in a jQuery UI dialog box.
       */
      runThenListen: function () {

        if (!$scope.validate()) return;

        //console_log(functionVersion);
        //console_log($scope.config.function.function_version);
        $scope.config.function.function_version = functionVersion;
        runFunction();

        $scope.listenForResults(function () {
          //console_log('Got results');
          // //console_log(message);
          //console_log(functionVersion);
          //console_log($scope.config.function.function_version);
          const $results = $('.alert:not(.ng-hide):not(.messenger-message)')

          if ($results.length === 0) return false;

          try {

            const title = $results.get(0).classList[1].split('-')[1]

            if (!title || title === 'info')
              return false

            const result = $results.find('h4').text()

            const $jobLinkClone = $results.find('a').last().clone(true, true)

            $results.remove()
            $scope.dialog(title, result, $jobLinkClone)

            return true

          } catch (e) { }

          return false

        })

      },

      /**
       * Resolves a code-conflict issue between jQuery and Bootstrap.
       */
      initializeBootstrap: function () {
        if ($.fn.button && $.fn.button.noConflict)
          $.fn.bootstrapBtn = $.fn.button.noConflict()
      },

      /**
       * Communicates with Python backend 
       * and acquires necessary data to display in the recipe UI.
       */
      communicateWithBackend: function () {

        // SAROOP_DONE: Set flag to false (before backend is called)
        isBackendDictReady = false;
        var startTime = new Date();
        $scope.callPythonDo({}).then(
          data => {
                    var endTime = new Date();
                    var numSeconds = Math.round((endTime - startTime)/1000);
                    if (numSeconds > 6){
                      $('<div></div>').dialog({
                                modal: true,
                                width: 400,
                                height: 150,
                                title: "Warning",
                                open: function() {
                                  var markup = "<b style='color:red;'> Response is slow, check Database connection</b>";
                                  $(this).html(markup);
                                },
                                buttons: {
                                  Ok: function() {
                                    $( this ).dialog( "close" );
                                  }
                                }   
                            }).css("font-size", "12px"); 
                    }

                    // SKS: Extend scope from python dictionary results
                    $.extend($scope, data)
                    
                    $('#filter_sqle').click(function() {
                        $scope.updateAvailableFunctions();
                    });
                    

                    $('#filter_valib').click(function() {
                        $scope.updateAvailableFunctions();
                    });

                    $scope.updateAvailableFunctions();
                  
                    $( "#current_function_name" ).change(function() {
                      // Update the hidden Menu which triggers the change in the model
                      $("#main_function_name").val($("#current_function_name").val())
                      $("#main_function_name").trigger('change')
                    });

                    // SKS: Set flag to True (after backend returns result)
                    isBackendDictReady = true;
                    
                    // SKS: and getFunctionMetadata Call function again
                    $scope.getFunctionMetadata($scope.config.function.name, !$scope.config.function);
                    // SKS: activate the UI (copied from original code path)
                    $scope.preprocessMetadata(true);
                    // Update current function name in UI
                    $("#current_function_name").val($scope.config.function.name);
                  },
          () => { }
        ).then(
          () => { 
                  if($scope.config.function.select_clause == null || $scope.config.function.select_clause == undefined){
                    $scope.resetSelectToStar()
                  }
                },
          () => {}
        );

      },

      updateAvailableFunctions: function() {
        var function_options = { };
        var numChoices = $scope.choices.length;
        for(var i=0; i<numChoices; ++i) {
          var choice = $scope.choices[i];
          var function_name = choice["function_alias_name"];
          function_options[function_name] = choice["keyword"];
        }

        $("#available_functions").empty();
        $.each(function_options, function(function_name, keyword)
        {
            
            if((keyword == "VALIB" && $("#filter_valib").is(':checked')) ||
                (keyword == "SQLE"  && $("#filter_sqle").is(':checked'))) 
            {

                $("<option/>", {
                  value: function_name,
                  text: function_name
                  }).appendTo("#available_functions");
            }
        });

      },          

                    

      /**
       * Activates the tabbing functionality of this recipe.
       */
      activateTabs: function () {
        try {
          $('#tabs').tabs('destroy')
        } catch (e) { }
        $('#tabs').tabs();
      },

      /**
       * Activates the informative tooltips of each input control.
       * Hijacks each tagsInput element so that it properly displays tooltips as well.
       */
      activateTooltips: function () {

        $('#main-container').tooltip();

        $delay(() => {

          $('.tagsinput').each((i, x) => {

            const original = $(x).prev().attr('data-original-title') || ''

            const title = original ?
              (original + '<br><br><b>(Press ENTER to add to list)</b>') :
              '<b>(Press ENTER to add to list)</b>'
            $(x).data({
              toggle: 'tooltip',
              container: 'body',
              placement: 'right',
              html: true,
              title: title,
              'original-title': title
            })
              .tooltip()

          });

        });

      },
      testPrint: function(element){
        $delay(() => {
        console_log('Testprint')
        // $('input.flexdatalist').trigger('change');
        // $('input.flexdatalist').trigger('input');
        // console_log(element.value);
        // console_log('==================================');
        // console_log(element);
        // console_log('==================================');
        // $scope.config.test_model = element;
        // console_log($scope.config.test_model);
        // alert($scope.config.test_model)

        // if XGBoost_Predict and if 
        });
      },
      changeInputModelTable: function(element){
        $delay(() => {
          if($scope.config.function.name == 'XGBoost_Predict'){
            if (element.name == 'Model'){
              // initialize
              $scope.config.function.required_input[1].orderByColumn = [''];
              $scope.config.function.required_input[1].orderByColumnDirection = [''];
  
              //Get list of column names
              var tableName = $scope.inputschemas[element.value];
  
              var listColumn = [];
              tableName.forEach(column => {
                listColumn.push(column.name);
              });
              // alert(listColumn);
  
              //if column name tree_id exist in the list
              var columnDefault = ['class_num', 'iter', 'tree_id'];
              columnDefault.forEach(column => {
                if (listColumn.includes(column)){
                  $scope.config.function.required_input[1].orderByColumn.unshift(column);
                  $scope.config.function.required_input[1].orderByColumnDirection.unshift('ASC');
                };
              });
            };
          };
        });
      },
      /**
       * Activates the multi-string input boxes.
       */
      activateMultiTagsInput: function () {
    	  $delay(() => {
        try {
            $('.flexdatalist').flexdatalist({
            minLength: 1,
            onChange: x => $(x).trigger('change')
            });
            
            $('input.flexdatalist').on('change:flexdatalist', function(event, set, options) {
              // console_log('The thing changed')
              // console_log(set.value);
              // console_log(set.text);
              // console_log(set);
              // console_log(event);
              // console_log(options);
              $(event.currentTarget).trigger('change');
              $(event.currentTarget).trigger('input');
              var ipt = event.currentTarget;
              // console_log(ipt);
              // console_log(event.target);
              // $(event.target).trigger('change');
              // $(event.target).trigger('input');
              // $scope.testPrint(event.currentTarget);
              // console_log($scope.config.test_model);
          });


            $('input.teradata-tags').tagsInput({
              interactive: true,
              unique: false,
              onChange: x => $(x).trigger('change'),
              onAddTag: function(tagName) {
                // Remove Double Quotes from List (aka Tags)
                if(tagName.includes('"')) {
                  $(this).removeTag(tagName);
                }
              },
              defaultText: 'add param',
              delimiter: SEPARATOR
            });

            // Do not allow quotes on inputs
            $("input").keypress(function(e){
                var c = String.fromCharCode(e.which);
                if(c == '"') {
                  return false;
                }
                return true;
            });

          } catch (e) {console.error('activateMultiTagsInput: ' + e); }
    	  });
      },

      /** 
       * Hijacks the current click handler of the recipe
       * and replaces it with the runThenListen function.
       * 
       * Stores the original recipe run function in the runFunction variable.
       */
      activateValidation: function () {

        const $runButton = $('.btn-run-main')
        runFunction = $._data($runButton.get(0), 'events').click[0].handler.bind($runButton.get(0));
        $runButton
          .off('click')
          .on('click', e => $scope.runThenListen());

      },

      /**
       * Hijacks the current UI and applies a few cosmetic improvements.
       */
      activateCosmeticImprovements: function () {

        const $a = $('.mainPane > div:first > div:first > div.recipe-settings-section2 > a');

        var doc_link;
        try 
        {
          if($scope.config.function.name.includes('VAL'))
            doc_link = 'https://docs.teradata.com/r/Vantage-Analytics-Library-User-Guide/January-2022';
          else
            doc_link = 'https://docs.teradata.com/r/Teradata-VantageTM-Advanced-SQL-Engine-Analytic-Functions/June-2022';
        } 
        catch (e) {
          doc_link = 'https://docs.teradata.com';
        }
        

        $a
          .text('Learn more about Teradata Vantage Analytic Functions')
          .css('color', 'orange')
          .attr('target', '_blank')
          .attr('href', doc_link);
        $a.html($a.html().replace(/\n/g,'<br/>'));
        $a.parent().css('text-align', 'center');
        $('#main-container > div > div:nth-child(1) > div > select')[0].value = '';
        $('.dss-page,#main-container').css('display', 'block');
        $('select:first, select:first > option').css('text-transform', 'capitalize');
        $('form').attr('novalidate', 'novalidate');

      },

      /**
       * Applies the custom changes to the default Dataiku UI needed for the Aster plugin to work.
       */
      activateUi: function () {

        $delay(() => {

          $scope.initializeBootstrap();

          $scope.activateCosmeticImprovements();
          $scope.activateTabs();
          $scope.activateMultiTagsInput();
          $scope.activateValidation();
                    
          
          
          $scope.reloader = true;
          
        });

      },

      cleanName: function (rawName) {

        return rawName.split('_').join(' ').toLowerCase()

      },

      cleanKind: function (rawKind) {
        if(rawKind==='PartitionByNone')
          return '';
        return rawKind ? `(${rawKind})` : ''

      },

      /**
       * Preprocess function metadata.
       */
      preprocessMetadata: function (shouldBindDefaults) {

        if (
          !functionMetadata
          || !$scope.config
          || !$scope.config.function
          || !$scope.config.function.arguments
          || !$scope.config.function.arguments.length) return;

        $delay(() => {

          // Re-arrange functions alphabetically.
          if ($scope.choices) {
            $scope.choices = $scope.choices.sort((a, b) => a.name.localeCompare(b.name))
          }

          let i = 0;
          $scope.config.function.arguments.forEach(argument => {

            // SKS: Added Default Value
            try 
            {
              argument.defaultValue = $scope.getDefaultValueWithName(argument);
            } 
            catch (e) {
              alert("Default Value was not updated");
            }

            // Index each argument for easy access.
            argument.i = i;
            let permittedValues = $scope.getPermittedValuesWithName(argument);
            if (permittedValues && argument.allowsLists) {
            	let curvalue = argument.value;
            	if (typeof curvalue === 'string') {
            		argument.value = argument.value.split(',');
            	}
            }
            
            // if (result && (item.value == null || item.value == "")){
            //     item.value = [""];
            //   }
            console_log('Checking COLUMN NAMES');
            console_log(argument.name);
            console_log(argument.datatype == "COLUMN_NAMES");
            console_log(argument.allowsLists);

            // SKS: The following line causes an exception for MovingAverage
            // SKS: Caught exception: TypeError: Cannot read property 'constructor' of null
            // SKS: Workaround, added a try-catch to avoid causing bug (this results in initTab not being called)
            try 
            {
              console_log(!(argument.value.constructor === Array));
            }
            catch (e) {
              console_log("call to argument.value.constructor..avoided an exception");
            }

            if((argument.datatype == "COLUMN_NAMES" || argument.datatype == "COLUMNS") && argument.allowsLists && argument.isRequired && !(argument.value.constructor === Array)){
              argument.value = [""];
              console_log(argument.value);
            } else if ((argument.datatype == "COLUMN_NAMES" || argument.datatype == "COLUMNS") && argument.allowsLists && !argument.isRequired && !(argument.value.constructor === Array)){
              argument.value = [""];
              console_log(argument.value);
            }
            if((argument.datatype == "STRING") && argument.allowsLists && $scope.getPermittedValuesWithName(argument) && argument.isRequired && !(argument.value.constructor === Array)){
              argument.value = [""];
              console_log(argument.value);
            } 

           /* try {

              if (functionMetadata.argument_clauses[i]
                && typeof functionMetadata.argument_clauses[i].defaultValue != 'undefined') {
                argument.value = functionMetadata.argument_clauses[i].defaultValue;
              }

            } catch (e) {

            }*/
            ++i;
          });

          // Re-arrange argument order.
          $scope.config.function.arguments = [
            ...$scope.config.function.arguments.filter(x => x.datatype === 'TABLE_NAME'),
            ...$scope.config.function.arguments.filter(x => x.datatype !== 'TABLE_NAME'),
          ]
          $scope.initTab();
        });

      },

      /**
       * Initializes this plugin.
       */
      initialize: function () {
        // alert("Initialize")
        $scope.communicateWithBackend();
        if ($scope.config.function) {
          $scope.getFunctionMetadata($scope.config.function.name, !$scope.config.function);
        }
        
        $scope.preprocessMetadata(false);
        $scope.activateUi();


        // $scope.config.function.partitionAttributes = $scope.config.function.partitionAttributes || [];
        // $scope.config.function.orderByColumn = $scope.config.function.orderByColumn || [];

      },
      
      shouldRender: function () {
    	  return functionMetadata ? true : false;
      },

      /**
       * Initializes this plugin.
       */
      refresh: function (selectedFunction) {
        $scope.getFunctionMetadata(selectedFunction, true);
        $scope.preprocessMetadata(true);
        // document.getElementById("defaultOpen").click();
      }

    })

    $scope.reloader = false;
    $scope.initialLoading = true;
    $scope.initialize();

  });
})(window, document, angular, jQuery);

