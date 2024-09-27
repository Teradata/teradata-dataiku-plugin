/**
 * Copyright Â© 2018 by Teradata.
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

  const app = angular.module('teradata_sto.module', []);

  app.controller('TeradataControllerScriptTO', function ($scope, $timeout) {
  

    /**
     * A wrapper function that delays execution so that
     * the Angular rendering cycle will have finished before
     * running the given function f.
     */
    const $delay = f => $timeout(f, 100);
    
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
    const FUNCTION_METADATA_PATH = '/plugins/AsterAnalytics/resource/data/';

    /**
     * Parameters to use for the dialog box.
     */
    const DIALOG_PARAMETERS = {
      modal: true,
      width: '33%',
      minHeight: 250,
      // close : function(){
      //     window.location.reload();
      // }
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

    let fileArraySize = 0;
    $scope.config.status="";

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
      // FILE_NAME: 'The name of the file to be installed',
      FILE_NAME: 'Specify the name of the input file to upload.',
      // FILE_ALIAS: 'The file alias to be used in the SQL statement',
      FILE_ALIAS: 'The Advanced SQL Engine Database needs an alias for the file, and a default alias is provided. You can change the default alias value, if desired, but ensure no two aliases are the same.',
      // FILE_LOCATION: 'The location of the file(s) to be installed, either the fully qualified path on the Teradata server, or a DSS Jupyter Notebook/Managed Folder',
      FILE_LOCATION: 'The location from where the file will be uploaded onto the Advanced SQL Engine Database.',
      // FILE_ADDRESS: 'The fully qualified file location on the Teradata Server',
      FILE_ADDRESS: 'The full path to the input file location on the Advanced SQL Engine Database server.',
      // FILE_FORMAT: 'Specifies whether a file is a TEXT or BINARY file',
      FILE_FORMAT: 'Specify whether the input is a TEXT or BINARY file.',
      // REPLACE_SCRIPT: 'Specifies whether a file will always be replaced',
      REPLACE_SCRIPT: 'Determines whether to replace an existing file on the Advanced SQL Engine Database or not. By default, if the box is checked and the file does not exist on the database, then the file will be installed.',
      SCRIPT_TYPE: 'Select your script language.',
      // SCRIPT_TYPE: 'Specify the script language. The plugin currently supports scripts written in R or Python.',
      OTHER_COMMAND: 'Enter the Unix command to execute your script',
      // SCRIPT_ARGUMENTS: 'The arguments for the script, place one argument per box. Click on the (+) button to add more arguments',
      SCRIPT_ARGUMENTS: 'Optional: Specify any additional input arguments, if needed by your script. Use one field per argument. Click on the [+] button to add fields. Click on the [-] button next to a field to delete it.',
      // ON: 'The ON Clause used as the input data for the script',
      ON: 'For the STO, the ON clause specifies the columns of a Advanced SQL Engine Database table that are streamed as input to your script. A default ON clause is provided, and it specifies using all columns of the recipe input dataset/table. To specify a different ON clause, click the "Customize the ON clause" button to edit the ON clause field.',
      // ON_CUSTOM: 'Determines whether the ON Clause should be modified',
      ON_CUSTOM: 'Enables customization of the default ON clause.',
      // HASH_BY: 'A HASH BY clause will cause the rows in the ON clause to be redistributed to AMPs based on the hash value of the column(s) specified',
      HASH_BY: 'The HASH BY clause groups table rows by the values of the specified column names, and distributes all rows of each group to a Advanced SQL Engine Database Access Module Processor (AMP; processing unit). Specify the column names you would like to hash their values by. If you specify a HASH BY clause, then you can also optionally order each group rows with the LOCAL ORDER BY clause.',
      // PARTITION_BY: 'A PARTITION BY clause will cause the STO to be executed against specific groups (partitions) based on the column(s) specified',
      PARTITION_BY: 'Specify column names for the partition task. Use one field per column. Click on the [+] button to add fields. Click on the [-] button next to a field to delete it.',
      // ORDER_BY: 'An ORDER BY clause specifies the order in which values in a group (partition) are sorted',
      ORDER_BY: '[Optional] Specify column names to use their data for row ordering in the partition groups. Use one field per column. Click on the [+] button to add fields. Click on the [-] button next to a field to delete it.',
      // LOCAL_ORDER_BY: 'A LOCAL ORDER BY clause  orders the rows qualified on each AMP',
      LOCAL_ORDER_BY: 'The LOCAL ORDER BY clause provides ordering of the input table rows in the groups created with the HASH BY clause. The LOCAL ORDER BY clause can be only specified when you have specified a HASH BY clause, too.',
      // RETURNS_NAME: 'Specifies the name of the column(s) to be returned by the STO',
      RETURNS_NAME: 'Specify a name for each output argument returned by your script.',
      // RETURNS_TYPE: 'Specifies the data type of the column(s) to be returned by the STO',
      RETURNS_TYPE:'Specify the data type of the column(s) to be returned',
      // SELECT_CUSTOM: 'Determines whether the SELECT (output) columns (data to be returned by the query) should be modified. Default is to SELECT all column(s) in the RETURNS clause',
      SELECT_CUSTOM: 'The default SELECT clause used by the plugin selects all output arguments of your script. Use this option determines whether to modify the default SELECT behavior.',
      // SELECT_COLUMNS: 'Specifies the contents of a user customized SELECT statement (data to be returned by the query)',
      SELECT_COLUMNS: 'Specify explicitly the contents of the SELECT clause.',
      ADDITIONAL_CLAUSES: 'Specifies any additional clauses to the output such as a HAVING or QUALIFY clause',
      // ADDITIONAL_CLAUSES: 'Specifies the SQL code for any additional clause to be used when invoking the STO. Examples of such clauses include DELIMITER, QUOTECHAR, etc. For more details, see Chapter 27 of the Teradata Guide "SQL Functions, Operators, Expression, and Predicates."'
      INPUTS: '[Optional] If you leave blank, then your script receives as input all columns in the recipe input dataset. If your script requires only specific columns from the recipe input dataset, then click on the [+] button to add fields and specify the column names needed by your script. Specify one column name per field in the order your script expects them. Click on the [-] button next to a field to delete it.',
      SEQUENCING_TYPE:'Select the order sequencing for the present column.',
      WHERE:'[Optional] Specify in SQL format any conditions that your input data must satisfy (note: This option corresponds to using the WHERE clause in SQL).',
      OUTPUT_COLUMN: 'Check the box to include this variable in the Dataiku output dataset.',
      OUTPUT_ALL: 'By default, all output variables of your script are included in the recipe Dataiku output dataset. To include only select variables, check the corresponding boxes next to the variables you want to include.',
      DATA_PARTITION_TYPE: 'If other than None, SCRIPT will partition the data sent to your script. In Vantage, instances of your script will execute with different data partitions as input until all partitions are exhausted. The column values option determines partitioning by means of different values in one or more columns (note: This option corresponds to using the PARTITION BY clause in SQL). The Database AMP hash option partitions data in a different way, where data are distributed to Database AMPs based on AMP hash values in one or more columns (note: This option corresponds to using the HASH BY clause in SQL).'
    }

    const fieldsContainer = document.getElementById("fieldsContainer");

    /** Regex for locating HTML entities. */
    const ENTITY_REGEX = /[\u00A0-\u9999<>\&]/gim

    /** Properly encodes an HTML entity. */
    function encodeRegex(i) {
      return '&#' + i.charCodeAt(0) + ';';
    }

    $.extend($scope, {

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

      getParamType: function (v) {
          if (Array.isArray(v)) {
              return 'array';
          } else if (typeof v==='object' && v!==null && !(v instanceof Date)) {
              return 'dictionary';
          }
          return 'string'
      },

      hasNoPartitionBy(){
        if($scope.config.function.partitionby == null || $scope.config.function.partitionby == ''){
          console.log('No Part by')
          $scope.config.function.orderby = '';
          return true
        } else {
          console.log(' Part by')
          return false
        }
      },

      hasNoHashBy(){
        if($scope.config.function.hashby == null || $scope.config.function.hashby == ''){
          console.log('No hash by')
          $scope.config.function.localorderby = '';
          return true
        } else {
          console.log('Hash by')
          return false
        }
      },

      openTabs: function(evt, tabName) {
        // Declare all variables
        var i, tabcontent, tablinks;
        console.log(evt); 
        // Get all elements with class="tabcontent" and hide them
        tabcontent = document.getElementsByClassName("plugintabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        tabcontent = document.getElementsByClassName("subtab");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
              }
  
      tabcontent = document.getElementsByClassName("subtabcontent");
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
      openSub: function(evt, tabName) {
      // Declare all variables
      var i, tabcontent, tablinks;
      console.log(evt); 
      // Get all elements with class="tabcontent" and hide them
      tabcontent = document.getElementsByClassName("plugintabcontent");
      for (i = 0; i < tabcontent.length; i++) {
          tabcontent[i].style.display = "none";
      }
      tabcontent = document.getElementsByClassName("subtab");
      for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "block";
      }
  
      tabcontent = document.getElementsByClassName("subtabcontent");
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
  
      openSubTabs: function(evt, tabName) {
      // Declare all variables
      var i, tabcontent, tablinks;
      console.log(evt); 
      // Get all elements with class="tabcontent" and hide them
      tabcontent = document.getElementsByClassName("plugintabcontent");
      for (i = 0; i < tabcontent.length; i++) {
          tabcontent[i].style.display = "none";
      }
      tabcontent = document.getElementsByClassName("subtabcontent");
      for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
      }
  
  
      // Get all elements with class="tablinks" and remove the class "active"
      tablinks = document.getElementsByClassName("subtablinks");
      
      for (i = 0; i < tablinks.length; i++) {
          tablinks[i].className = tablinks[i].className.replace(" active", "");
      }
        
      // Show the current tab, and add an "active" class to the button that opened the tab
      document.getElementById(tabName).style.display = "block";
      evt.currentTarget.className += " active";
  },
  

      
      

      addMoreFilesClick: function () {
        $scope.config.function.files.push({});
        fileArraySize = $scope.config.function.files.length;
      },

      addReturnClause: function() {
          $scope.config.function.return_clause.push({output:'false'});
      },

      getEnvName: function(index) {
          $scope.config.function.EnvName.push(index);
      },
      removeReturnClause: function(index) {
          if (index > -1) {
              $scope.config.function.return_clause.splice(index, 1);
          }
      },

      selectAllOutput: function() {
        if($scope.config.function.outputAll == true) {
          for (const clause of $scope.config.function.return_clause) {
              clause["output"] = false;
          }
        }
      },

      selectOneOutput: function() {
        var found = false;
        for (const clause of $scope.config.function.return_clause) 
        {
              if(clause["output"]==true) {
                found = true;
                break;
              }
        }
        if(found)
          $scope.config.function.outputAll = false
        else
          $scope.config.function.outputAll = true
      },

      addScriptArgument: function() {
          $scope.config.function.arguments.push({});
      },

      removeScriptArgument: function(index) {
          if (index > -1) {
              $scope.config.function.arguments.splice(index, 1);
          }
      },

      addScriptInput: function() {
          $scope.config.function.inputs.push({});
      },

      removeScriptInput: function(index) {
          if (index > -1) {
              $scope.config.function.inputs.splice(index, 1);
          }
      },

      addPartitionBy: function() {
          $scope.config.function.partitionbycolumns.push({"type" : "Ascending"});
      },

      removePartitionBy: function(index) {
          if (index > -1) {
              $scope.config.function.partitionbycolumns.splice(index, 1);
          }
      },


      addPartitionColumnBy: function() {
          $scope.config.function.partitionorderbycolumns.push({"type" : "Ascending"});
      },

      removePartitionColumnBy: function(index) {
          if (index > -1) {
              $scope.config.function.partitionorderbycolumns.splice(index, 1);
          }
      },


      onFilenameChange() {
          let filename = $scope.config.function.script_filename || '';
          $scope.config.function.script_alias = (filename.substring(0,filename.lastIndexOf('.')) ||
              filename).replace(/("| |')/g, "");
      },

      onAdditionalFilenameChange: function(index) {
          if (!$scope || index < 0 ||
                  !$scope.config ||
                  !$scope.config.function ||
                  !$scope.config.function.files ||
                  index >= $scope.config.function.files.length) {
              return;
          }
          let filename = $scope.config.function.files[index].filename || '';
          $scope.config.function.files[index].file_alias = (filename
              .substring(0,filename.lastIndexOf('.')) || filename).replace(/("| |')/g, "");
      },

      onFileLocationChange() {
          $scope.config.function.script_filename = '';
          $scope.config.function.script_alias = '';
          $scope.config.function.command_type = 'other'
      },

      getOriginalON() {
         
        $scope.config.function.sql_on_clause = [];

      },

      resetSelectToStar() {
        
       $scope.config.function.select_clause = '*';

     },

      onAdditionalFileLocationChange: function(index) {
          if (!$scope || index < 0 ||
                  !$scope.config ||
                  !$scope.config.function ||
                  !$scope.config.function.files ||
                  index >= $scope.config.function.files.length) {
              return;
          }
          $scope.config.function.files[index].filename = '';
          $scope.config.function.files[index].file_alias = '';
      },

      removeFile: function (index) {
        if (index > -1) {
          $scope.config.function.files.splice(index, 1);
        }
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

      /**
       * Checks if there is a version mismatch in function_version
       */
      checkVersionMismatch: function () {


        // })
      },

      /**
       * Gets the description of the given argument from the static JSON metadata.
       */
      getArgumentDescription: function (argument) {
        return ARGUMENT_TITLES[argument]
      },

      getPermittedValues: function (i) {

        try {

          return (functionMetadata
            && functionMetadata.argument_clauses[i]
            && functionMetadata.argument_clauses[i].permittedValues)
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
        tableNameAliases.push(tableNameAlias);
        functionMetadata.argument_clauses.map(argument => {
          if (argument.name.toUpperCase() === tableNameAlias) {
            if (KEYS.ALTERNATE_NAMES in argument) {
              argument.alternateNames.map(function (altname) { tableNameAliases.push(altname); })
            }
            console.log('tableNameAliases');
            console.log(tableNameAliases);
            // tableNameAliases.push(argument.name.toUpperCase());

          }
        })
        let potentialMatches = argumentsList
          .filter(arg => tableNameAliases.includes(arg.name.toUpperCase()));
        
        console.log('Find tablename');
        console.log(potentialMatches);
        console.log(argumentsList);
        if (potentialMatches.length) {
          console.log(potentialMatches);
          //console.log('We finally got here');
          return potentialMatches[0].value;
        }
        return ''

      },

      /**
       * Gets the function schema by joining and processing the metadata from the python backend 
       * and the static JSON file associated with the function.
       */
      getSchema: function (functionArgument, aliasedInputsList, unaliasedInputsList, argumentsList) {
        //console.log('Get Schema runs');
        aliasedInputsList = aliasedInputsList || []
        argumentsList = argumentsList || []
        console.log('getSchema');
        // console.log(functionMetadata)
        console.log(functionArgument);
        console.log(aliasedInputsList);
        console.log(unaliasedInputsList);
        console.log(argumentsList);
        const hasTargetTable = KEYS.TARGET_TABLE in functionArgument
        let targetTableName = ''
        var isAliasedInputsPopulated;
        var isInAliasedInputsList = false;
        var y = false;
        
        if (hasTargetTable) {
          
          const targetTableAlias = functionArgument.targetTable.toUpperCase();
          
          console.log('Table name');
          console.log(targetTableAlias);
          
          if (aliasedInputsList !== []) {
            isAliasedInputsPopulated = true;
            aliasedInputsList.map((input) => {
              if (input.name.toUpperCase() === targetTableAlias.toUpperCase()) {
                console.log('true');
                isInAliasedInputsList = true;
              }
            }
            )
          } else {
            isInAliasedInputsList = false;
          }
          
          const isAliased = isInAliasedInputsList;
          
          if (isAliased) {
            console.log('isAliased');
            let matchingInputs = aliasedInputsList.filter(input => targetTableAlias === input.name.toUpperCase());
            if (matchingInputs.length > 0) {
              
              targetTableName = matchingInputs[0].value;
            } else {
              
              targetTableName = $scope.findTableNameInArgumentsList(argumentsList, targetTableAlias);
            }


          } else {
            
            if (unaliasedInputsList.count && unaliasedInputsList.values && unaliasedInputsList.values.length) {
              console.log('Went to unaliased');

              targetTableName = unaliasedInputsList.values[0];
              
            }

            else {
              targetTableName = $scope.findTableNameInArgumentsList(argumentsList, targetTableAlias);
              console.log('Went to arguments');
              console.log(targetTableName);
            }


          }

        } else if (unaliasedInputsList.values && unaliasedInputsList.values.length > 0) {

          targetTableName = unaliasedInputsList.values[0]
          

        }

        if (!targetTableName || !$scope.inputschemas) {
          
          return [];
        }


        if (targetTableName && targetTableName in $scope.inputschemas) {
          
          return $scope.inputschemas[targetTableName];

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

        return $scope.config.function.arguments.filter(x => x.isRequired).length > 0

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
          && ($scope.config.function.arguments.filter(x => !x.isRequired).length > 0);

        return hasOptionalInputTable || hasOptionalArgument;

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
        $('.ng-invalid:not(form,.ng-hide,div,#selectize-selectized,option)').each((i, x) => {
          // invalids.push($(x).parent().prev().text());
          invalids.push($(x)[0].id);
          console.log($(x)[0]);
        }
      )
        
        if (invalids.length) {
          $scope.validationDialog(`Please amend the following fields: <ul>${invalids.map(x => `<li>${x}</li>`).join('')}</ul>`)
          // $scope.validationDialog(`Please amend the fields marked in red`)
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

        //console.log(functionVersion);
        //console.log($scope.config.function.function_version);
        // $scope.config.function.function_version = functionVersion;        
          
        console.log('Checking scope config');
        console.log($scope.config);
        runFunction();

        $scope.listenForResults(function () {
          //console.log('Got results');
          // //console.log(message);
          //console.log(functionVersion);
          //console.log($scope.config.function.function_version);
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

        $scope.callPythonDo({}).then(
          data=> {
            if(data['error'])
            {
              alert(data['error'])
            }
            $.extend($scope,data)
            $('#function_name').css('display', 'block');
            // moved to later as initialisation is too slow
            $scope.activateCosmeticImprovements();
          },
          () => {}
        ).then(
          () => { $scope.config.function.input_table = $scope.inputs.find(
                        (x => ('main' === x.role) && x.fullName) || {'fullName':''}).
                        fullName.split('.').pop();
                  if($scope.config.function.sql_on_clause == null || $scope.config.function.sql_on_clause == undefined){
                    $scope.getOriginalON()
                  }
                  if($scope.config.function.select_clause == null || $scope.config.function.select_clause == undefined){
                    $scope.resetSelectToStar()
                  }
                },
          () => {}
        );
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

      /**
       * Activates the multi-string input boxes.
       */
      activateMultiTagsInput: function () {
        try {

          $('input.teradata-tags').tagsInput({
            onChange: x => $(x).trigger('change'),
            defaultText: 'add param',
            delimiter: SEPARATOR
          });

        } catch (e) { }
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
        var title;
        try 
        {
          if($scope['isVantageCloudLake']==true) {
            doc_link = 'https://docs.teradata.com/r/Teradata-VantageCloud-Lake/Analyzing-Your-Data/Build-Scalable-Analytics-with-Open-Analytics-Framework/APPLY-Table-Operator';
            title ="Learn more about Vantage APPLY Table Operator";
          }
          else{
            doc_link = 'https://docs.teradata.com/r/SQL-Operators-and-User-Defined-Functions/July-2021/Table-Operators/SCRIPT';
            title = "Learn more about Teradata Vantage SCRIPT Table Operator";
          }

        }
        catch (e) {
          doc_link = 'https://docs.teradata.com';
          title = "Learn more about Teradata Vantage Table Operators";
        }
        
        
        $a
          .text(title)
          .css('color', 'orange')
          .attr('target', '_blank')
          .attr('href', doc_link);
        $a.parent().css('text-align', 'center');


        
        // $('#main-container > div > div:nth-child(1) > div > select')[0].value = '';
        $('.dss-page,#main-container').css('display', 'block');
        // $('select:first, select:first > option').css('text-transform', 'capitalize');
        $('form').attr('novalidate', 'novalidate');

      },

      /**
       * Applies the custom changes to the default Dataiku UI needed for the Aster plugin to work.
       */
      activateUi: function () {

        $delay(() => {
          console.log('I can actually run');
          $scope.initializeBootstrap();
          console.log('Starting activation of Tab activation')
          $scope.activateTabs();
          console.log('Starting activation of Multi tags input')
          $scope.activateMultiTagsInput();
          console.log('Starting activation validation')
          $scope.activateValidation();
          console.log('Initializing first tab')
          document.getElementById("defaultOpen").click();
          console.log('All is complete on activation')
          // Undefined
          // $scope.getOriginalON();
        });



      },

      cleanName: function (rawName) {
        return rawName.split('_').join(' ').toLowerCase()

      },

      formatConnectionSetting: function(key) {
          let formattedString = (key.match(/(.*[a-z])((?=[A-Z]).*)/) || []).slice(1)
            .join(" ") || key;
          return formattedString.charAt(0).toUpperCase() + formattedString.slice(1);
      },

      formatNameRuling: function(key) {
          let formattedString = key.match(/[A-Z]*[^A-Z]+/g).join(" ");
          return formattedString.charAt(0).toUpperCase() + formattedString.slice(1);
      },

      cleanKind: function (rawKind) {

        return rawKind ? `(${rawKind})` : ''

      },

      /**
       * Preprocess function metadata.
       */
      preprocessMetadata: function () {

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

          // Properly bind default arguments.
          let i = 0;
          $scope.config.function.arguments.forEach(argument => {

            // Index each argument for easy access.
            argument.i = i;

            try {

              if (functionMetadata.argument_clauses[i]
                && typeof functionMetadata.argument_clauses[i].defaultValue != 'undefined') {
                argument.value = functionMetadata.argument_clauses[i].defaultValue;
              }

            } catch (e) {

            }

            ++i;

          });

          // Re-arrange argument order.
          $scope.config.function.arguments = [
            ...$scope.config.function.arguments.filter(x => x.datatype === 'TABLE_NAME'),
            ...$scope.config.function.arguments.filter(x => x.datatype !== 'TABLE_NAME'),
          ]

        });

      },
      confirmDelete: function() {
        $('<div></div>').dialog({
          modal: true,
          width: 400,
          title: "Environment Update",
          open: function() {
            var markup = "You have requested to remove the user environment: "+$scope.config.environment_name ;
            $(this).html(markup);
          },
          buttons: {
            Confirm: function() {
              $(this).dialog("close");
              // Perform desired action on confirmation
              $scope.deleteEnvironment();
            },
            Cancel: function() {
              $(this).dialog("close");
              // Perform desired action on cancellation
            }
          }
        });
      },
      
      deleteEnvironment: function() {
      
            $scope.callPythonDo({
            'delete_env':true,
            'environment_name': $scope.config.environment_name
            }).then(
            data => {
                var message;
                if (data.result)
                message = "Env Removed"
                else
                message = "error"
                $('<div></div>').dialog({
                modal: true,
                width: 700,
                title: "Environment Update",
                open: function() {
                $(this).html(data.result);
                },
                buttons: {
                OK: function() {
                $( this ).dialog( "close" );
                }
                }
                });
                },
                () => { }
                ).then(
                () => {
                // Do nothing
                },
                () => {}
                );
            },
      
      createEnvironment: function() {
      

            $scope.callPythonDo({
            'create_env':true,
            'baseEnv': $scope.config.base_env,
            'envName': $scope.config.env_name,
            'des': $scope.config.des
            }).then(
            data => {
                var message;
                if (data.result)
                message = "Env Created"
                else
                message = "error"
                $('<div></div>').dialog({
                modal: true,
                width: 700,
                title: "Environment Update",
                open: function() {
                $(this).html(data.result);
                },
                buttons: {
                OK: function() {
                $( this ).dialog( "close" );
                }
                }
                });
                },
                () => { }
                ).then(
                () => {
                // Do nothing
                },
                () => {}
                );
            },

            
      userAuthentication: function() {
      
          $scope.callPythonDo({
          'tabs_auth':true,
          'ues_url': $scope.config.ues_url, 
          'pat_token': $scope.config.pat_token,
          'pvt_key': $scope.config.pvt_key,
          'exp_time':  $scope.config.exp_time
          }).then(
           data =>{
            var message;
                 if (data.result)
                 message = "authentication done"
                 else
                 message = "error"
                 $('<div></div>').dialog({
                 modal: true,
                 width: 700,
                 title: "Authentication Update",
                 open: function() {
                 $(this).html(data.result);
                 },
                 buttons: {
                 OK: function() {
                 $( this ).dialog( "close" );
                 }
                 }
                 });
                 },
                 () => { }
     
              ).then(
              () => {
              // Do nothing
              },
              () => {}
              );
            },


      installLibs: function() {
         
            $scope.callPythonDo({
            'install_libs':true,
            'envName': $scope.config.environment_name,
            'libs': $scope.config.lib,
            'req_lib': $scope.config.req_lib}).then(
             data => {
                 $scope.config.status = $scope.config.status +data.status
                 var message;
                 if (data.result)
                 message = "installing"
                 else
                 message = "error"
                 $('<div></div>').dialog({
                 modal: true,
                 width: 700,
                 title: "Environment Update",
                 open: function() {
                 $(this).html(data.result);
                 },
                 buttons: {
                 OK: function() {
                 $( this ).dialog( "close" );
                 }
                 }
                 });
                 },
                 () => { }
                 ).then(
                 () => {
                 // Do nothing
                 },
                 () => {}
                 );
             },

      updateLibs: function() {
         
            $scope.callPythonDo({
            'update_libs':true,
            'envName': $scope.config.environment_name,
            'libs': $scope.config.lib_name}).then(
             data => {
                 $scope.config.status = $scope.config.status+data.status

                 var message;
                 if (data.result)
                 message = "updating"
                 else
                 message = "error"
                 $('<div></div>').dialog({
                 modal: true,
                 width: 700,
                 title: "Environment Update",
                 open: function() {
                 $(this).html(data.result);
                 },
                 buttons: {
                 OK: function() {
                 $( this ).dialog( "close" );
                 }
                 }
                 });
                 },
                 () => { }
                 ).then(
                 () => {
                 // Do nothing
                 },
                 () => {}
                 );
             },
      confirmDelete: function() {
        $('<div></div>').dialog({
          modal: true,
          width: 400,
          title: "Environment Update",
          open: function() {
            var markup = "You have requested to remove the remote user environment: "+$scope.config.environment_name ;
            $(this).html(markup);
          },
          buttons: {
            Confirm: function() {
              $(this).dialog("close");
              // Perform desired action on confirmation
              $scope.deleteEnvironment();
            },
            Cancel: function() {
              $(this).dialog("close");
              // Perform desired action on cancellation
            }
          }
        });
      },

      confirmLibuninstall: function() {
        $('<div></div>').dialog({
          modal: true,
          width: 400,
          title: "Environment Update",
          open: function() {
            var markup = "You have requested to uninstall the library: "+ $scope.config.lib_name+ " from the remote user environment: "+$scope.config.environment_name ;
            $(this).html(markup);
          },
          buttons: {
            Confirm: function() {
              $(this).dialog("close");
              // Perform desired action on confirmation
              $scope.uninstallLibs();
            },
            Cancel: function() {
              $(this).dialog("close");
              // Perform desired action on cancellation
            }
          }
        });
      },

      uninstallLibs: function() {
         
            $scope.callPythonDo({
            'uninstall_libs':true,
            'envName': $scope.config.environment_name,
            'libs': $scope.config.lib_name }).then(
             data => {
                 $scope.config.status = $scope.config.status+data.status

                 var message;
                 if (data.result)
                 message = "uninstalling"
                 else
                 message = "error"
                 $('<div></div>').dialog({
                 modal: true,
                 width: 700,
                 title: "Environment Update",
                 open: function() {
                 $(this).html(data.result);
                 },
                 buttons: {
                 OK: function() {
                 $( this ).dialog( "close" );
                 }
                 }
                 });
                 },
                 () => { }
                 ).then(
                 () => {
                 // Do nothing
                 },
                 () => {}
                 );
             },

      confirmFileuninstall: function() {
        $('<div></div>').dialog({
          modal: true,
          width: 400,
          title: "Environment Update",
          open: function() {
            var markup = "You have requested to uninstall the file: "+ $scope.config.uninstall_file_name+ " from the remote user environment: "+$scope.config.environment_name ;
            $(this).html(markup);
          },
          buttons: {
            Confirm: function() {
              $(this).dialog("close");
              // Perform desired action on confirmation
              $scope.uninstallFiles();
            },
            Cancel: function() {
              $(this).dialog("close");
              // Perform desired action on cancellation
            }
          }
        });
      },
      uninstallFiles: function() {
         
            $scope.callPythonDo({
            'uninstall_file':true,
            'envName': $scope.config.environment_name,
            'file': $scope.config.uninstall_file_name}).then(
             data => {
                 var message;
                 if (data.result)
                 message = "uninstalling"
                 else
                 message = "error"
                 $('<div></div>').dialog({
                 modal: true,
                 width: 700,
                 title: "Environment Update",
                 open: function() {
                 $(this).html(data.result);
                 },
                 buttons: {
                 OK: function() {
                 $( this ).dialog( "close" );
                 }
                 }
                 });
                 },
                 () => { }
                 ).then(
                 () => {
                 // Do nothing
                 },
                 () => {}
                 );
             },
             
      installFiles: function() {
         
            $scope.callPythonDo({
            'install_file':true,
            'envName': $scope.config.environment_name,
            'file': $scope.config.install_file_name }).then(
             data => {
                 $scope.config.status = $scope.config.status+data.status

                 var message;
                 if (data.result)
                 message = "installing"
                 else
                 message = "error"
                 $('<div></div>').dialog({
                 modal: true,
                 width: 700,
                 title: "Environment Update",
                 open: function() {
                 $(this).html(data.result);
                 },
                 buttons: {
                 Ok: function() {
                 $( this ).dialog( "close" );
                 }
                 }
                 });
                 },
                 () => { }
                 ).then(
                 () => {
                 // Do nothing
                 },
                 () => {}
                 );
             },
      refreshEnv: function() {
         
            $scope.callPythonDo({
            'refresh':true,
            'envName': $scope.config.environment_name}).then(
             data => {
                 var message;
                 if (data.result)
                 message = "refreshing"
                 else
                 message = "error"
                 $('<div></div>').dialog({
                 modal: true,
                 width: 700,
                 title: "Environment Update",
                 open: function() {
                 $(this).html(data.result);
                 },
                 buttons: {
                 OK: function() {
                 $( this ).dialog( "close" );
                 }
                 }
                 });
                 },
                 () => { }
                 ).then(
                 () => {
                 // Do nothing
                 },
                 () => {}
                 );
             },
             
      checkStatus: function() {
         
            $scope.callPythonDo({
            'status':true,
            'envName': $scope.config.environment_name,
            'claim_id': $scope.config.claim_id,
            'all_status':$scope.config.status}).then(
             data => {
                 var message;
                 if (data.result)
                 message = "checking status"
                 else
                 message = "error"
                 $('<div></div>').dialog({
                 modal: true,
                 width: 800,
                 title: "Environment Update",
                 open: function() {
                 $(this).html(data.result);
                 },
                 buttons: {
                 OK: function() {
                 $( this ).dialog( "close" );
                 }
                 }
                 });
                 },
                 () => { }
                 ).then(
                 () => {
                 // Do nothing
                 },
                 () => {}
                 );
             },
             

      viewEnv: function() {
         
            $scope.callPythonDo({
            'view':true,
            'envName': $scope.config.environment_name
            }).then(
             data => {
                 var message;
                 if (data.result)
                 message = "User environment detials"
                 else
                 message = "error"
                 $('<div></div>').dialog({
                 modal: true,
                 width: 700,
                 title: "Environment Update",
                 open: function() {
                 $(this).html((data.result).replaceAll("\n", "<br>"));
                 },
                 buttons: {
                 OK: function() {
                 $( this ).dialog( "close" );
                 }
                 }
                 });
                 },
                 () => { }
                 ).then(
                 () => {
                 // Do nothing
                 },
                 () => {}
                 );
             },
             
		

      
      /**
       * Initializes this plugin.
       */
      initialize: function () {
        console.log('Start initialize()')
        $scope.config.function = $scope.config.function || {};
        $scope.config.function.script_location = $scope.config.function.script_location || "";
        $scope.config.function.files = $scope.config.function.files || [];
        $scope.config.function.arguments = $scope.config.function.arguments || [{'value':''}];
        $scope.config.function.return_clause = $scope.config.function.return_clause || [{'name':'','type':'', 'output' : false}];
        fileArraySize = $scope.config.function.files.length;
        $scope.config.function.inputs = $scope.config.function.inputs || [{'value':''}];
        $scope.config.function.where = $scope.config.function.where || '';
        $scope.config.function.partitionbycolumns = $scope.config.function.partitionbycolumns || [{'value':'','type':'Ascending'}];
        $scope.config.function.partitionorderbycolumns = $scope.config.function.partitionorderbycolumns || [{'value':'','type':'Descending'}];
        if ($scope.config.function.outputAll != undefined)
          $scope.config.function.outputAll = $scope.config.function.outputAll
        else
          $scope.config.function.outputAll = true
        
        $scope.communicateWithBackend();
        // if ($scope.config.function) {
        //   $scope.getFunctionMetadata($scope.config.function.name);
        // }

        // $scope.preprocessMetadata();
        $scope.activateUi();
        console.log('Initialize done')
      },

      /**
       * Initializes this plugin.
       */
      refresh: function (selectedFunction) {

        // $scope.getFunctionMetadata(selectedFunction);
        // $scope.preprocessMetadata();
        // //console.log($scope);
      }

    })
    var updateEnvNames = function() {
            // the parameter to callPythonDo() is passed to the do() method as the payload
            // the return value of the do() method comes back as the data parameter of the fist function()
            $scope.callPythonDo({'environment_name':true}).then(function(data) {
                // success
                $scope.names = data.names;
            }, function(data) {
                // failure
                $scope.names = ['N/A'];
             });
    };


    $scope.$watch('config.environment_name',updateEnvNames);
    $scope.$watch('config.function.environment',updateEnvNames);


    
    var updateFiles = function() {
            // the parameter to callPythonDo() is passed to the do() method as the payload
            // the return value of the do() method comes back as the data parameter of the fist function()
            $scope.callPythonDo({'file_name':true,
            'envName': $scope.config.environment_name}).then(function(data) {
                // success
                $scope.files = data.files;
            }, function(data) {
                // failure
                $scope.files = ['N/A'];
             });
    };

    $scope.$watch('config.uninstall_file_name',updateFiles);
    $scope.$watch('config.function.uninstall_file_name',updateFiles);


    
    var listLibs = function() {
            // the parameter to callPythonDo() is passed to the do() method as the payload
            // the return value of the do() method comes back as the data parameter of the fist function()
            $scope.callPythonDo({'lib_name':true,
            'envName': $scope.config.environment_name }).then(function(data) {
                // success
                $scope.libs = data.libs;
            }, function(data) {
                // failure
                $scope.libs = ['N/A'];
             });
    };

    $scope.$watch('config.lib_name',listLibs);

    
    var updateBaseEnv = function() {
            // the parameter to callPythonDo() is passed to the do() method as the payload
            // the return value of the do() method comes back as the data parameter of the fist function()
            $scope.callPythonDo({'base_env':true}).then(function(data) {
                // success
                $scope.choices = data.choices;
            }, function(data) {
                // failure
                $scope.choices = ['N/A'];
             });
    };
    $scope.$watch('config.base_env',updateBaseEnv);

    

    $scope.initialize();

});
  
    





})(window, document, angular, jQuery);