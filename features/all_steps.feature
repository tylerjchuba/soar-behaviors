Feature: Example Steps to use when configuring a test cases
        Scenario: Container Configurations
            # Declare a container with just name and label 
            Given the container "container_name" under the label "container_label"
            Given the container "container_name" within the label "container_label"
            # Declare more attributes of container using a tabel
            Given the following container configuration
                  | name           | label           | status           |
                  | container_name | container_label | container_status |
            Given the container "container_name" has the following "custom_fields"
                  | key1 | value2 |
                  | key2 | value2 |
            Given the container "container_name" has the following "data"
                  | key1 | value2 |
                  | key2 | value2 |
            # Dictionary data/custom_fields
            Given the container has the following "data" below
                  | key1 | value2 |
                  | key2 | value2 |
            # List values for tags
            Given the container has the following "tags" below
                  | red   |
                  | green |
            
            

        Scenario: Declaring & Configuring Artifacts
            # Declare an artifact with CEF values in one step 
            Given the artifact "artifact_name" with the "label" of "artifact_label"
                  | cef_key1 | cef_value1 |
                  | cef_key2 | cef_value2 |
            Given the artifact "artifact_name" labeled "artifact_label"
                  | cef_key1 | cef_value1 |
                  | cef_key2 | cef_value2 |
            # Then use the following steps to configure other details about the artifact 
            Given the artifact "artifact_name" with the "tags" of "['test', 'example_tag']"
            Given the artifact "artifact_name" with the "cef" of "exampleKey:exampleValue"
            Given the artifact "artifact_name" has the following "tags" values
                  | test1 |
                  | tes1  |
            Given the artifact "artifact_name" has the following "cef" values
                  | key1 | value1 |
                  | key2 | value2 |

            Given the artifact "artifact_name" has the "emailBody" below
                """
              At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum
              deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, 
              similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. 
              Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis
              est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, 
                """
            
            # Assign values to an artifact.cef.sub-dictionary 
            Given the artifact "test1" has the following "emailDetails" values
                  | fromAddress | example.com |
                  | date        | 1/01/2020   |


        Scenario: Declaring Playbooks
            Given the playbook "playbook_name"
            Given with the playbook "playbook_name"


        Scenario: Interacting with Prompts / Approvals
            # Prompts must be declared and used referencing the name of the prompt
            Given the prompt "prompt_name" has the following responses:
                  | The first answer to the questions  |
                  | The second answer to the questions |
     

        Scenario: Creating Declared & Configured Resources
             # MANDATORY: The objects must be created before anything can be ran or validated
             Then the container and artifacts are created


        Scenario: Running playbooks
             # Use this step when multiple playbooks are declared using the "Given the playbook "playbook_name" step"
             When the playbooks are run
             When the playbook "playbook_name" is ran

        Scenario: Declare and run a single playbook
             # Use this step when you only need to run a single playbook. The container/Artifacts must be created
             Then run the playbook "<repo_name>/<playbook_name>"


        Scenario: Collecting Results / Refreshing Objects
            # This step is optional if running a playbook. After a playbook is ran, the most recent container data is
            # downloaded to the container context
             Then the results are collected

        Scenario: Uploading files
             # Files must be stored inside the repository under the "resources" folder 
             Then upload the file "resources/file_name" to the container

        Scenario: Validating Containers + Miscellanous objects
             # Validate the color and message of the pin 
             Then a "color" pin is created with the text "text top of the pin"
             # Validate the color, message, and data of a pin 
             Then a "color" pin is created with the message "message" and data "data"
             # Check that a container attribute has an expected value
             Then the container has the "container_field" of "value"
             # Check that the container.data[key] has the provided list of keys and values
             Then the container data has the "data_key" values
                  | example_key  | example_value |
                  | example_key2 | example_value |
             # Validate note quantity 
             Then there are "2" total notes
             # Validate a specific note
             Then the note "note_title" is created
             Then "comment_string" is commented
             Then the comment "comment_string" is added

        Scenario: Switching Container context
            # Use this step if your process creates a second container that needs checks ran against it. 
             Then a container is created under the label "container_label"
    

        Scenario: Validating Artifacts
             # Checking various attributes of a given artifact 
             Then the artifact "artifact_name" has the "label" of "artifact_label"
             Then the artifact "artifact_name" has the "cef" of "key:Value"
             Then the artifact "artifact_name" has the "tags" of "[exampleTag]"
             # Check for the existence (not value) of a given cef key 
             Then the artifact "artifact_name" has the following "cef_key" values
             # Validate that the artifact has a specific nonempty cef key
             Then the artifact "artifact_name" has the cef "cef_key_name" key
             # Check that an artifact's CEF does not have a given key  
             Then the artifact "artifact_name" does not have the cef "cef_key"
             # Check that a quantity of labeled artifacts exist. Useful when multiple artifacts are created
             Then there are at least "quantity" artifacts labeled "artifact_label"


        Scenario: Validating Playbooks
             # Check the status of the playbook using either "success" or "failed"
             Then the playbook "playbook_name" has the status of "status"
             # Validate that all actions on the playbook are successful. Not encouraged for usage, please specify actions 
             Then the playbook actions are successful
             # Check the status of a named child playbook. Not a common step that should be used 
             Then the callback "callback_name" playbook "child_playbook_name" of "parent_playbook_name" is "playbook_status"
             # Validate the status of a specific playbook's action 
             Then the playbook "playbook_name" action "action_name" is "action_status"
             # Validate that a playbook is not executed
             Then the playbook "playbook_not_supposed_to_be_ran_name" has not run
             # Validate by action name, only allowed when a single playbook is executed during the run of scenario
             Then the action "action_name" is "status"
            # Validate that a given action was not ran 
             Then the action "action_name" did not run
            # Validate that an action has a value
             Then the action "action_name" has the "field" below
                """
        Example body of text
                """
             Then the action "action_name" has the "field" of "value"

        Scenario: Miscellanous Steps
            # Use this step to force the browser to open and see the code objects inside the terminal 
             Then debug
             Then open the browser
            # Open the browser without failing the running test case
             Then the browser is opened
             Then open the browser
            # Deletes the container as the lasts step as to not spam Splunk SOAR 
             Then delete the container
             Then the resources are deleted
             # Wait for a set period of time 
             Then wait for "quanitity_of_seconds" seconds
