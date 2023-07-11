from behave import *
from utility_functions import *
from assert_helpers import *
from soarsdk.objects import Artifact
from soarsdk.objects import Container
from soarsdk.objects import Playbook
from soarsdk.objects import Action
import os
from exceptions import ContainerMissingAttributes
from exceptions import ContainerNotConfigured
from exceptions import ArtifactNotConfigured
from exceptions import PlaybooksNotConfigured
from exceptions import ActionNotFound


@given("the following container configuration")
def table_container_configuration(context: Context):
    """Configure a container by listing a table with all the variables defined in one step. You must have a a row header of 'name' and 'label' at minimum.
    Example: Given the following container configuration
             | name | label | run_auto |
             | Test | alert | False    |
    Params:
        context (Context): scenario context

    Raises:
        ContainerMissingAttributes: If the container isn't created with the minimal attributes
    """
    row_dict = table_to_array(context.table)[0]
    context.container = Container(**row_dict)
    try:
        assert context.container.name and context.container.label
    except AssertionError:
        raise ContainerMissingAttributes()
    context.container.tags.append("phantom-test-cases")


@given('the container "{container_name}" under the label "{label}"')
@given('the container "{container_name}" within the label "{label}"')
def container_step_configuration(context: Context, container_name: str, label: str):
    """Initialize a container object with a required name and label.
    Example: Given the container "Behave Test Example" within the label "example_label"

    Params:
        context (Context): scenario context
        container_name (str): desired name of the container
        label (str): desired label where the container should exist

    Raises:
        ContainerMissingAttributes: If the container isn't created with the minimal attributes
    """
    context.container = Container(
        name=container_name, label=label, tags=["phantom-test-cases"]
    )
    try:
        assert container_name and label
    except AssertionError:
        raise ContainerMissingAttributes()


@given('the container has the following "{attribute}" below')
def container_assign_attr_table(context: Context, attribute: str):
    """Assigns custom_fields or data attributes to a container utilizing a table configuration
    Example: the container has the following "custom_fields" below
        |   type    |   incident    |
        |   source  |   network     |

    Params:
        context (Context): scenario context
        attribute (str): Desired container attribute, see soarsdk.objects.Container

    Raises:
        ContainerNotConfigured: If the container has not be previously declared using a given step

    """
    assert_container(context.container)
    try:
        getattr(context.container, attribute)
    except:
        raise AttributeError(f"The container object does not have a {attribute} field")

    if attribute in ["data", "custom_fields"]:
        setattr(context.container, attribute, table_to_dictionary(context))
    if attribute == "tags":
        setattr(context.container, attribute, table_to_list(context.table))
    else:
        setattr(context, attribute, context.table)


@given('the artifact "{artifact_name}" has the "{key}" value below')
def assign_artifact_attr_text(context: Context, artifact_name: str, key: str):
    """Set an artifact value using a large body of text below the step. See all_steps.feature for exampleusage

    Args:
        context (Context): scenario context
        artifact_name (str): name of the artifact
        key (str): name of the artifact attribute to set

    Raises:
        ArtifactNotConfigured: Artifact must have been previously declared
    """
    artifact: Artifact = context.container.get_artifact(name=artifact_name)
    if not artifact:
        raise ArtifactNotConfigured(
            f"The artifact {artifact_name} has not been declared or was not found on the container"
        )
    if ":" in key:
        key1, key2 = key.split(":")[0]
        artifact.cef[key1][key2] = context.text
    else:
        artifact.cef[key] = context.text


@given('the artifact "{artifact_name}" with the "{attr}" of "{val}"')
@given('the artifact "{artifact_name}" has the "{attr}" of "{val}"')
def step_impl(context: Context, artifact_name, attr, val):
    """Adds a cef value to a given Artifact or declares a new artifact with that cef
    Example: the artifact "test1" has the "cef" of "foo:bar"
    """
    artifact = context.container.get_artifact(name=artifact_name)
    if not artifact:
        artifact = Artifact(name=artifact_name)
        context.container.add_artifact(artifact)
    if attr == "cef":
        artifact.cef = dict_parse(val)
    elif attr == "tags":
        artifact.tags = list_parse(val)
    else:
        # if not a primary attribute of artifact
        if attr not in artifact.cef:
            # assign it as a subdict of cef
            artifact.cef[attr] = {}
            artifact.cef[attr] = dict_parse(val)


@given('the artifact "{artifact_name}" with the label "{label}"')
@given('the artifact "{artifact_name}" labeled "{label}"')
def declare_artifact_with_cef(context: Context, artifact_name: str, label: str):
    """Initialize an artifact object within the previously defined container.
    Use this to declare the artifacts before attempting to define tags or cef for them with a table.
    Example: the artifact "test1" with the label "test1"

    Parameters:
        context (Context): scenario data
        artifact_name (str): name of the artifact
        label (str): label of the artifact

    Raises:
        ContainerNotConfigured: Container must initialized before artifacts are created
    """
    assert_container(context.container)
    artifact_cef: dict = {}

    if hasattr(context, "table"):
        if hasattr(context.table, "headings"):
            artifact_cef: dict = table_to_dictionary(context)

    artifact: Artifact = Artifact(name=artifact_name, label=label, cef=artifact_cef)
    context.container.add_artifact(artifact)


@given('the artifact "{artifact_name}" has the following "{sub_field}" values')
def assign_artifact_attr(context: Context, artifact_name: str, sub_field: str):
    """Configuration step to list all the values of either a cef/tags of an artifact before creation. The subfield provided isn't
    an existing artifact attribute, it will be assigned as a sub-dictionary key inside of the artifact's CEF.

    Example: Given the artifact "test1" has the follow "cef" values
        | key2    | val2     |

    Example: Given the artifact "test1" has the following "tags" values
        | tag1 |
        | tag2 |

    Example: Given the artifact "test1" has the following "emailDetails" values
        | fromAddress | example.com |
        | date        | 1/01/2020   |

    Parameters:
        context (Context): scenario data
        artifact_name (str): name of the artifact
        sub_field (str): attribute to assign the table values

    Raises:
        ContainerNotConfigured: Container must initialized before artifacts are created
        ArtifactNotConfigured: Artifact must already be declared using a given step


    """
    assert_container(context.container)
    artifact: Artifact = context.container.get_artifact(name=artifact_name)
    if not artifact:
        raise ArtifactNotConfigured(
            f"The artifact {artifact_name} has not been declared or was not found on the container"
        )

    if sub_field == "tags":
        artifact.tags = table_to_list(context.table)
    elif sub_field == "cef":
        artifact.cef = table_to_dictionary(context)
    else:
        artifact.cef[sub_field] = {}
        sub_d = table_to_dictionary(context)
        for k, v in sub_d.items():
            artifact.cef[sub_field][k] = v


@given("the following artifacts")
def bulk_artifacts_table(context: Context):
    """Provides the ability to declare artifacts and fields in one step. Discouraged as it can get messy.
    Example: Given the following artifacts
        | name  | label | cef     | tags |
        | test1 | test1 | foo:bar | [foo,bar] |

    Parameters:
        context (Context): scenario data

    Raises:
        ContainerNotConfigured: Container must initialized before artifacts are created
    """
    assert_container(context.container)
    table = table_to_array(context.table)

    for row in table:
        context.container.add_artifact(Artifact(**row))


@given('the playbook "{playbook_name}"')
def declare_playbook(context: Context, playbook_name: str):
    """Add a playbook to a declared container within the context
    Example: Given the playbook "playbook_name"

     Parameters:
        context (Context): scenario data
        playbook_name (str): playbook name

    Raises:
        ContainerNotConfigured: Container must initialized before artifacts are created
    """
    playbook: Playbook = Playbook(name=playbook_name)
    assert_container(context.container)
    context.container.playbooks.append(playbook)


@given('the prompt "{prompt_name}" has the following responses')
def configure_prompt(context: Context, prompt_name: str):
    """Adds a prompt response to the most recently declared playbook. The parameter prompt_name must utilize the name of the
    associated playbook.

    Parameters:
        context (Context): scenario data
        prompt_name (str): the name of the prompt from the playbook's VPE

    Raises:
        ContainerNotConfigured: Container must initialized before artifacts are created
        PlaybooksNotConfigured: A playbook must declared before the associated prompt response
    """
    assert_container(context.container)
    if not context.container.playbooks:
        raise PlaybooksNotConfigured
    playbook: Playbook = context.container.playbooks[-1]
    responses: list = table_to_list(context.table)
    playbook.prompts[prompt_name] = responses


@then('upload the file "{file_path}" to the container')
def upload_file_to_container(context: Context, file_path: str):
    """Uploads a file to the context container within Phantom. Check PhantomClient.upload_file() for more details
    Example: Then upload the file "./test.json" to the container

    Parameters:
        context (Context): scenario data
        file_path (str): location of the file to upload (recommended using the resources folder)

    Raises:
        FileNotFoundError: If the provided file & path cannot be located
        IOError: If the file cannot be read by the library
    """
    assert_container(context.container)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Requested file for upload {file_path} not found")

    try:
        file_data = open(file_path, "rb").read()
    except IOError as e:
        raise IOError(f"Failed to read the provided file: {e}")

    context.phantom.upload_file(context.container, file_path)


@then('assign the action output of "{data_path}" as "{variable_name}"')
def assign_data_output(context: Context, data_path: str, variable_name: str):
    """_summary_

    Parameters:
        context (Context): scenario data
        data_path (str): _description_
        variable_name (str): _description_

    Raises:
        KeyError: If the data_path cannot be parsed
        ActionNotFound: If the parsed action_name cannot be located on the container
    """
    action_name: str = data_path.split(".")[0]
    target_variable: str = data_path.split(".")[-1]

    if not action_name:
        raise KeyError(f"Failed to parse action_name from data_path {data_path}")

    action: Action = context.container.get_action(name=action_name)[0]
    if not action:
        raise ActionNotFound(
            f"Failed to find action {action_name} inside the container"
        )

    # Assign the target variable_name to the replacement_vars
    for result in json_key_finder(target_variable, action.result_data):
        context.replacement_vars[variable_name] = result
