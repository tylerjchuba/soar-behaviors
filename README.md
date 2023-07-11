# Phantom Test Cases 
The repository that stores the testing library and test cases for Phantom (Splunk SOAR) playbooks. The new updated tool introduces two new libraries  - [soarsdk](https://github.com/tylerjchuba/soarsdk) and [Behave](https://behave.readthedocs.io/en/stable/). 


## Phantom Testing Guiding Philosophy
The goal of these new changes is to create better controls and consistencies when developing playbooks. A test case **should be able to describe what a playbook does** without the description or details of the playbook itself. This allows future engineers to better understand the intent of a playbook and allows for a more collaborative community. 

## Using the Gherkin language 
To make test cases as easy and readable as possible, we've implemented the Behave library with the Gherkin testing language. Essentially, this translates English statements into function calls within the library. For more information on Gherkin you can follow their reference sheet [here](https://cucumber.io/docs/gherkin/reference/), or to understand how Behave uses feature files you can read their guide [here](https://behave.readthedocs.io/en/stable/tutorial.html#feature-files). 

For more information on writing your own steps to use for this library, read this [tutorial](https://behave.readthedocs.io/en/stable/tutorial.html#python-step-implementations).



## Installation and Setup
The behave library requires [soarsdk](https://github.com/tylerjchuba/soarsdk) as an installation. 
~~~bash
# python3 environmental variable 
python3 -m pip install -r requirement.txt

~~~

## Configuring Connection & Authentication


## Running Behave Tests
1. Clone this Repo  
2. Open a terminal, and "cd soar-behaviors" 

Run a single test or a collection of similarly named tests. By default, the -i flag will include any Feature files that match the given string.
~~~bash
# Sign into Phantom before running tests
behave -i <feature_file_name>
behave -i <similar string>
~~~

The same functionality applies when you're trying to exclude tests from running. 

~~~bash
behave -e <playbook name to ignore>
~~~


## Testing Step Parsing 
When writing a FeatureFile, it's important to ensure that the steps written actually map to the implemented python step. To validate that the test case's steps are properly written out, use the command:
~~~bash
behave -i <file_name> -d 
~~~
This will allow to quickly see which steps are configured correctly before executing. 


# Writing a test case 
To get started, create or add onto an existing test case file within the *features* directory. Each scenario is categorized under the **playbook name** of which it runs and validates. 

To get started running a test case, each test case needs a container, artifacts, and playbooks. There are multiple ways to declare to each of the these data types. 


## Verbose Test Catalog
See the [all_steps.feature](features/all_steps.feature) file to view the currently supported steps within the library as well as descriptions on how to use them. 


## Simple Declarations 
If your use case is simple, it's easiest to declare them on one line. For example: 
~~~gherkin
Feature: Single line declarations 
Scenario: Simple test case scenario
    Given the container "test_container_name" under the label "alert" 
    Given the artifact "test123"

Scenario: Simple artifact with cef
    Given the container "test_container_name" under the label "alert" 
    Given the artifact "test123" with the cef "detectionSource:Crowdstrike"

Scenario: Simple artifact with tags 
    Given the container "test_container_name" under the label "alert" 
    Given the artifact "test123" with the tags "awesometags1, tag2, etc" 

~~~

## Table Declarations 
Sometimes a test case requires a significant amount of details that's difficult to list out on one line. In this case, it's easier to describe the object with a table. This library utilizes tables for a variety of different steps. Steps that utilize tables have the string "with the following". 

~~~gherkin
Feature: Table Declarations
Scenario: complex case
    Given the following container configuration  
        | label | name  | run_auto |
        | alert | test1 | False    |
    Given the artifact "test1" with the label "test1"
    Given the artifact "test1" has the following "cef" values
        | destinationAddress | 8.8.8.8   |
        | sourceAddress      | 127.0.0.1 |
    Given the artifact "test1" has the following "tags" values
        | tag1 |
        | tag2 |
        | tag3 |
~~~

## Utilizing comment blocks 
There are certain scenarios where an artifacts cef field is ridiculously massive and cannot fit into one of these tables, or it contains characters that cause the file not to work. **Use this step with preformatted data, data that contains newlines, or the '|' character.** To declare such a value, use the following format: 

~~~gherkin
    Given the artifact "test1" has the "emailBody" value below
    """
        This represents a large email with an abundance of strings that require
        parsing. This is a quick easy way to assign it an artifact's cef without
        the complications of trying to fit it into a table.
    """
~~~~


## Running playbooks
Playbooks are just as easy to describe. You may list them individually or as a table. We use the **When** keyword to run playbooks in a procedural order. This can be an easy way to chain multiple playbooks, interactions, and validations in order. 

~~~gherkin
    Feature: Running playbooks
    Scenario: Procedural Order
        Given the following container configuration
            | label | name  | run_auto |
            | alert | test1 | False    |
        Given the artifact "test1" with the label "test1"
        Given the artifact "test1" has the following "cef" values 
            | destinationAddress | 8.8.8.8   |
            | sourceAddress      | 127.0.0.1 |
        Given the artifact "test1" has the following "tags" values
            | tag1 |
            | tag2 |
            | tag3 |
        When the container and artifacts are created
        When the playbook "<repo_name>/<playbook_name>" is ran
        Then the playbook "playbook_name" is ran
~~~

### Handling Prompts 
Playbooks that require human interaction with prompts are handled differently than the conventional outline above. In the case where we know there are prompts to be handled ahead of time, we can declare the playbook and its configuration ahead of time.  

1. **Before** creating resources or running playbooks, specify the name of the playbook. Note you need to include the repository name.
2. Then specify the **name** of the prompt and its responses as they appear on the form. The prompts will be associated with **the most recent playbook** declared within the scenario. 
3. Run the playbook with either the "When the playbooks are ran" or "When the playbook "playbook_name"" steps. 

~~~gherkin
    Feature: Running Playbooks
    Scenario: Handling Prompt interactions 
        Given the container "Prompt Interactions" under the label "alert"
        Given the artifact "test1" with the label "test1"
        Given the artifact "test1" has the following "cef" values 
            | destinationAddress | 8.8.8.8   |
            | sourceAddress      | 127.0.0.1 |
        Given the playbook "<repo_name>/<playbook_name>" <-------------|
        Given the prompt "prompt_name" has the following responses <---|
            | I approve of this message | 
            | No                        | 
        When the container and artifacts are created
        When the playbooks are ran <------------------------------|
        When the playbook "repo_name>/<playbook_name>" is ran <---|

~~~

## Interactions 
The following steps are required for running a test case. You always have to create the container and artifacts before running playbooks, and to download the most recent container and run data. These steps are **critical** to perform before trying to run any assertions against its data. 

~~~gherkin
	Then the container and artifacts are created
	When the playbooks are run
	Then the results are collected 
~~~

## Writing Checks & Validations
**Test cases and playbook must have a form of validation that the intended action occurred**. This can be accomplished by the following: 
 - Checking for pin creation
 - Checking for container or artifact tags
 - Checking for new artifacts
 - Checking for a playbook's action results 

### Examples of validations 
~~~gherkin
    # Check a playbook's action
    Then the playbook "playbook_name" action "get data" is "success"

    # Check a pin for color and messaging 
    Then a "red" pin is created with the text "An unexpected error has occurred"

    # Check a container/artifact for a tag 
    Then the container "test_container" has the "tags" of "exampleTag, tag2"
    Then the artifact "artifact1" has the "tags" of "onlyOneTag""

~~~


## Note on keywords Given, Then, When, And
1. **Given**: is used to declare objects or configuration items. These describe existing resources before any playbooks are run. 
2. **When**: describes when action occurs. 
3. **Then**: Describes outcomes as a result of an action. Every validation step will start with "Then" 

You can substitute any of these keywords with **And** as long there is a previous step declared before it. From a code perspective, it will just infer the previous keyword. 



## Using Scenarios for Simpler test cases  
You can reduce the amount of scenarios needed for a given test case by **scenario outlines** from the Behave library. This allows a test case to repeat the same scenario multiple times just by changing variables. This is primarily useful for playbooks that categorize and tag either artifact or containers. Below is an example that was built for the demo playbook for conf23. The scenario outline runs for each table entry, substituting the variables provided into the steps.  

~~~gherkin
        Scenario Outline: Testing known blocked domains
            Given the container "Proxy block with a single domain" under the label "alert"
            Given the artifact "blocked domain" labeled "event"
              And the artifact "blocked domain" has the "cef" of "destinationDnsDomain:<domain>"
             Then the container and artifacts are created
             Then the playbook "triage_blocked_domains" is ran
              And the results are collected
             Then the artifact "blocked domain" has the "tags" of "<tags>"
              And the playbook "triage_blocked_domains" has the status of "success"
            
        Examples:
                  | domain            | tags      |
                  | blockeddomain.com | []        |
                  | .random.com       | [blocked] |

        @ignore_exception
        Scenario Outline: Non-blocked are commented on the container
            Given the container "Proxy block with a single domain" under the label "alert"
            Given the artifact "blocked domain" labeled "event"
              And the artifact "blocked domain" has the "cef" of "destinationDnsDomain:<domain>"
             Then the container and artifacts are created
             Then the playbook "triage_blocked_domains" is ran
              And the results are collected
             Then the artifact "blocked domain" has the "tags" of "<tags>"
              And "<domain> is currently not blocked" is commented

        Examples:
                  | domain      | tags |
                  | .google.com | []   |
                  | .splunk.com | []   |
~~~


## Troubleshooting
If you encounter an issue where you are failing your test case, there are a few ways to help identify the problem. 

1. Check your container/artifact configuration. Before running the interaction steps, add the following line to force Behave to print out the configuration before it's submitted to Phantom. 

~~~gherkin
   Feature: Table Declarations
    Scenario: complex case
        Given the following container configuration
            | label | name  | run_auto |
            | alert | test1 | False    |
        Given the artifact "test1" with the label "test1"
        Given the artifact "test1" has the following "cef" values 
            | destinationAddress | 8.8.8.8   |
            | sourceAddress      | 127.0.0.1 |
        Given the artifact "test1" has the following "tags" values
            | tag1 |
            | tag2 |
            | tag3 |
        And the playbook "playbook_name"
        Then throw error # <----- Prints the configuration of the test
~~~

1. Check the resources Behave has downloaded and updated. Throughout the lifecycle of the test case, the same container object is referenced and updated. Add the same statement after interactions to see the pure object that validations are checking against. Additionally, you can include the step **Then open the browser** that will open your default internet browser to the container its made. 
~~~gherkin
   Feature: Table Declarations
    Scenario: complex case
        Given the following container configuration
            | label | name  | run_auto |
            | alert | test1 | False    |
        Given the artifact "test1" with the label "test1"
        Given the artifact "test1" has the following "cef" values 
            | destinationAddress | 8.8.8.8   |
            | sourceAddress      | 127.0.0.1 |
        Given the playbook "example_playbook_name" 
        Then connect to "sandbox"
        Then the container and artifacts are created
        When the playbooks are run
        Then the results are collected 
        Then open the browser # <------ Shows you the test in a web browser 
        Then throw error # <----- Prints downloaded results 
~~~
        

## Data Type Standards
This section describes how various data types can be represented in a test file within the context of a table or a step declaration. 

### Dictionaries 
~~~gherkin 
# python dictionaries
# example_dictionary = {'key': 'value'}

# For single line declarations
Given the artifact "artifact_name" has the cef "key:value"   # <-- Preferred 
Given the artifact "artifact_name" has the cef "{'key':'value'}" #<--- Harder to read

# Declare keys within a dictionary 
Given the artifact "artifact_name" has the following "cef" values
    | testKey1 | testVal1 |
    | testKey2 | testVal2 | 
    | testKey3 | testVal3 |
~~~

### Lists
~~~gherkin
# python lists
# example_list = [1,2,3]

# For single line declarations 
Given the artifact "artifact_name" has the "tags" of "1,2,3" 
And the artifact "artifact_name" has the following "tags" values
    | tag1 |
    | tag2 | 
~~~



# Full Steps Catalog
Run the following command to see the full list of available steps pre-configured for this library. Steps are contained within the features/steps directory. 
~~~bash
behave --steps-catalog 
~~~


# Git Workflows & Procedures
## Standard
To being working on a test case, create a new branch based off of master that's named after the playbook that you're working on. 
~~~bash
git checkout -b <my_playbook_name>
~~~

Once completed with your changes, or you're wanting to share your code with others you need to push your local changes to this repository. You need to start by telling Git which files you would like to send upstream. You can do this using the **git add** command. Do this command for each file you want to include in your commit.  

~~~bash
git add features/<my_playbook_name>.feature
~~~

Once you've added all the relevant files, you need to commit your changes to the current branch. Include a message that indicates to others what you have changed.
~~~bash
git commit -m "Updated the test case with more examples" 
~~~

Finally, push the changes upstream using the **git push** command. It's import to use the **--set-upstream** parameter for the changes to actually reach the repository. 
~~~bash
git push --set-upstream origin <my_branch_name>
~~~

## How do I update my branch with Master? 
If there are new steps or changes added to the **master** branch of the repository, you can **rebase** your playbook's branch on master to automatically add the newest changes to your current branch. 
~~~bash
git rebase master
~~~
