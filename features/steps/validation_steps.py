from utility_functions import *
from exceptions import *
from behave import then, when
from behave.model import Row, Table
from typing import Generator, Union, Any
from behave.runner import Context
from soarsdk.objects import Container, Artifact, Action, Playbook
from assert_helpers import assert_container


@then('the playbook "{playbook_name}" has the status of "{status}"')
def assert_playbook_status(context: Context, playbook_name: str, status: str):
    """Validates the success of the playbook_run's status field.

    Raises:
        PlaybookNotRan: If the provided playbook_name is not found to have ran on the container.
        AssertionError: If the playbook's status field is failed
    """
    playbook: Playbook = context.container.get_playbook(name=playbook_name)
    if not playbook:
        raise PlaybookNotRan(
            f"Failed to find playbook {playbook_name} on the container"
        )
    try:
        assert playbook.status == status
    except:
        raise AssertionError(
            f"Playbook {playbook.name} status of {playbook.status} does not equal {status}"
        )


@then("the playbook actions are successful")
def assert_all_actions_successful(context: Context) -> None:
    """Blanket level validation that asserts that all actions are successful. This validation step is not recommended for common usage as it removes the verbosity and documentation of test cases

    Raises:
      AssertionError: If any action has a failure status attribute
    """
    playbooks = context.container.playbooks
    for playbook in playbooks:
        for action in playbook.actions:
            try:
                assert action.status == "success"
            except AssertionError:
                raise AssertionError(
                    f"The playbook {playbook.name}'s action {action.name} failed"
                )


@then(
    'the callback "{callback_name}" playbook "{child_playbook_name}" of "{playbook_name}" is "{status}"'
)
def assert_callback_status(
    context: Context,
    playbook_name: str,
    callback_name: str,
    child_playbook_name: str,
    status: str,
) -> None:
    """Verifies that the child playbook was successful.

    Raises:
        PlaybookNotRan: If the provided playbook_name is not found to have ran on the container.
        AssertionError: If the child playbook's status is not successful
    """

    playbook = context.container.get_playbook(name=playbook_name)
    if not playbook:
        raise PlaybookNotRan(f"No playbook {playbook_name} was found on the container.")

    callback_info = playbook.misc.get("callback").get(callback_name)

    try:
        assert callback_info.get("child_playbook_status") == status
    except AssertionError:
        child_playbook_status = callback_info.get("child_playbook_status")
        raise AssertionError(
            f'Child playbook {child_playbook_name} run status "{child_playbook_status}" does not match expected "{status}"'
        )


@then('the playbook "{playbook_name}" action "{action_name}" is "{status}"')
def assert_playbook_action_status(
    context: Context, playbook_name: str, action_name: str, status: str
):
    """Checks that a playbook's action has a given status
    Example: the playbook "playbook_name" action "action_name" is "success|failed"

    Raises:
        PlaybookNotRan: If the provided playbook is not found on the container
        LookupError: If the provided action is not found the given playbook
        AssertionError: If the action's status does not match the provided status value

    """
    playbook: Playbook = context.container.get_playbook(name=playbook_name)

    if not playbook:
        raise PlaybookNotRan(
            f"Playbook {playbook_name} not found in context.container. \n {[context.container.playbook_names]}"
        )

    action = playbook.get_action(action_name)

    if not action:
        raise LookupError(f"Action {action_name} not found in playbook {playbook}")

    try:
        assert action.status == status
    except AssertionError:
        raise AssertionError(
            f"Action {action_name} status of {status} does not match container action {action}"
        )


@then('the playbook "{playbook_name}" has not run')
def validate_playbook_not_ran(context: Context, playbook_name: str) -> None:
    """Checks that a playbook has not run
    Example: the playbook "demo_playbook" has not run

    Raises:
        AssertionError: If the playbook is found on the container
    """
    playbook = context.container.get_playbook(name=playbook_name)
    if playbook:
        raise AssertionError(f"Playbook {playbook_name} was ran")


@then('a "{color}" pin is created with the text "{message}"')
def validate_pin_created(context: Context, color: str, message: str) -> None:
    """Validates that a pin is created with a given color and text
    Example: Then a "red" pin is created with the text "Failure"

    Raises:
        AssertionError: If the Pin is not found with the corresponding message and color
    """
    pins: list = context.container.pins
    success: bool = False
    for pin in pins:
        if pin.data == message and pin.style == color:
            success = True
        if pin.message == message and pin.style == color:
            success = True

    if not success:
        raise AssertionError(
            f"{color} pin containing the message {message} not found in container. \n {pins}"
        )


@then('a "{color}" pin is created with the message "{message}" and data "{data}"')
def validate_full_pin(context: Context, color: str, message: str, data: str) -> None:
    """Validates that a pin is created with a given color, message and data
    Example: Then a "red" pin is created with the message "Failure" and data "System Error"

    Raises:
        AssertionError: If the Pin is not found with the corresponding message and color
    """

    for pin in context.container.pins:
        if pin.style == color and pin.message == message and pin.data == data:
            return

    raise AssertionError(
        f"{color} pin containing the message {message} and data {data} was not found. \n {context.container.pins}"
    )


@then('the action "{action_name}" is "{status}"')
def validate_action_status(context: Context, action_name: str, status: str) -> None:
    """Compare an action result to either success or failed. This is for any playbook within the container.
       Looks for at least once successful instance of the action running successfully in the event there are
       multiple events with the same name.
    Example: Then the "action run_query" is "success"

    Raises:
        ActionNotFound: Action not found in the run history of the container
        AssertionError: An action was found matching the name but without a matching status

    """
    if status not in ("success", "failed"):
        raise AssertionError(
            f'The action status "{status}" is invalid. Use either success or failed for the step configuration.'
        )

    matching_actions: list[Action] = context.container.get_action(name=action_name)

    if action_name not in context.container.action_names:
        raise ActionNotFound(action_name)

    for matching_action in matching_actions:
        if matching_action.name == action_name and matching_action.status == status:
            return

    raise AssertionError(
        f"No actions matching {action_name} matched the status of {status}"
    )


@then('the action "{action_name}" did not run')
def validate_action_absent(context: Context, action_name: str):
    """Ensure an action did not run.
    Example: Then the action run_query did not run
    """
    assert action_name not in context.container.action_names


@then('the artifact "{artifact_name}" has the "{key}" of "{value}"')
def validate_artifact_attribute(
    context: Context, artifact_name: str, key: str, value: str
):
    """Verifies that the given artifact has an attribute of a given value
    Example: Then the artifact "Foobar" has the "cef" of "testKey:testValue"
    Example: Then the artifact "Foobar" has the "tags" of "tag1, tag2, tag3"

    Params:
        context (Context): Scenario Context
        artifact_name (str): Name of the artifact
        key (str): artifact attribute

    Raises:
        ArtifactNotConfigured: Artifact could not be found on the container
    """

    artifact_attr: list[str] = ["label", "name", "cef", "tags"]
    artifact: Artifact = context.container.get_artifact(artifact_name)

    if not artifact:
        raise ArtifactNotConfigured(
            f"Artifact {artifact_name} not found in container artifacts: {context.container.artifacts}"
        )

    # Parse the provided value as a list
    if key == "tags":
        parsed_list: list = list_parse(value)
        print(f"{artifact.tags} | {parsed_list}")
        assert_equal_unordered_lists(parsed_list, artifact.tags)

    # Assert Keys and Values
    elif key == "cef":
        parsed_dictionary: dict = dict_parse(value)
        for expected_key, expected_value in parsed_dictionary.items():
            if not artifact.cef.get(expected_key):
                raise KeyError(
                    f"The cef key {expected_key} not found in the artifact's CEF. Available keys: {artifact.cef.keys()}"
                )
            if not expected_value == artifact.cef.get(expected_key):
                raise AssertionError(
                    f"The artifact CEF {expected_key} does not match expected. Actual: {artifact.cef[expected_key]} | Expected {expected_value} "
                )

    else:
        try:
            assert str(getattr(artifact, key)) == value
        except AssertionError:
            raise AssertionError(
                f"Artifact attribute {key} does not match expected value. Expected: {value} | Actual: {getattr(artifact, key)}"
            )


@then('the artifact "{artifact_name}" has the following "{sub_field}" values')
def validate_artifact_table(
    context: Context, artifact_name: str, sub_field: str
) -> None:
    """Asserts that a given artifact has provided values underneath [cef | tags] field.
    Example: Then the artifact "test_artifact" has the following "cef" values
        |   name    |   bob     |
        |   age     |   26      |

    Params:
        context (Context): Scenario Context
        artifact_name (str): Name of the artifact
        sub_field (str): Specify either CEF or Tags attributes
    Raises:
        ArtifactNotConfigured: If matching artifact cannot be found on the container
        AssertionError: If provided subfield doesn't match the values of the artifact
    """
    artifact_attr: list[str] = ["cef", "tags"]
    artifact: Artifact = context.container.get_artifact(artifact_name)

    if not artifact:
        raise ArtifactNotConfigured(
            f"Artifact {artifact_name} not found in container artifacts: {context.container.artifact_names}"
        )

    if sub_field == "cef":
        expected_values = table_to_dictionary(context)
        for key, value in expected_values.items():
            if not artifact.cef[key] == value:
                raise AssertionError(
                    f"Artifact {artifact.name} failed validations. Expected value: {value} | actual: {artifact.cef[key]}"
                )

    elif sub_field == "tags":
        assert_equal_unordered_lists(artifact.tags, table_to_list(context.table))


@then('the artifact "{artifact_name}" has the cef "{cef_key}" key')
def validate_artifact_cef(context: Context, artifact_name: str, cef_key: str):
    """Asserts that a given artifact has provided given attribute that is not null

    Params:
        context (Context): Scenario Context
        artifact_name (str): Name of the artifact
        cef_key (str): CEF key to match value

    Raises:
        ArtifactNotConfigured: If matching artifact cannot be found on the container
        KeyError: If the provided cef_key isn't found within the common event fields

    """
    artifact: Artifact = context.container.get_artifact(artifact_name)

    if not artifact:
        raise ArtifactNotConfigured(
            f"Artifact {artifact_name} not found in container artifacts: {context.container.artifact_names}"
        )

    if not artifact.cef.get(cef_key):
        raise KeyError(
            f"The cef {cef_key} was not found within the artifact {artifact_name}"
        )


@then('the artifact "{artifact_name}" does not have the cef "{cef_key}" key')
def step_impl(context: Context, artifact_name: str, cef_key: str):
    """Asserts that a given artifact has provided given cef _key
    Params:
        context (Context): Scenario Context
        artifact_name (str): Name of the artifact
        cef_key (str): CEF key to match value

    Raises:
        ArtifactNotConfigured: If matching artifact cannot be found on the container
        AssertionError: If the provided cef_key is found within the common event fields

    """
    artifact: Artifact = context.container.get_artifact(artifact_name)

    if not artifact:
        raise ArtifactNotConfigured(
            f"Artifact {artifact_name} not found in container artifacts: {context.container.artifact_names}"
        )

    if artifact.cef.get(cef_key):
        raise AssertionError(
            f"The cef {cef_key} was found within the artifact {artifact_name}"
        )


@then('the container has the "{attr}" of "{expected_value}"')
def step_impl(context: Context, attr: str, expected_value: str):
    """Asserts that the container has an attribute of a certain value
    Example: the container "test_container" has the "status" of "new"

    Params:
        context (Context): scenario context object
        attr (str): Container attribute (see soarsdk.objects.Container)
        expected_value (str): Comparison value for the request attribute

    Raises:
        AssertionError: The value of the attribute does not match the expected result
    """
    if attr == "tags":
        assert_equal_unordered_lists(context.container.tags, list_parse(expected_value))
    else:
        try:
            if attr == "data" or attr == "custom_fields":
                expected_value = dict_parse(expected_value)

            assert str(getattr(context.container, attr)) == str(expected_value)
        except AssertionError:
            raise AssertionError(
                f"The container attribute {attr} {expected_value} does not match {getattr(context.container, attr)}"
            )


@then('the container data has the following "{data_key}" values')
def validate_container_attributes_table(context: Context, data_key: str):
    """Asserts that the container's "data" attribute has the key value provided in a table format
    Example: the container data has the "foo" values
            | key | value |
            | bar | test  |
    Params:
        context (Context): scenario context
        data_key (str): Attribute to compare values

    Raises:
        KeyError: If the provided field isn't found in the container.data dictionary
        AssertionError: If any of the values for attribute do not match the provided table
    """
    try:
        # Check if the data key has a subkey as well
        if ":" in data_key:
            key, subkey = data_key.split(":")
            container_data_values = context.container["data"][key][subkey]
        else:
            container_data_values = context.container["data"][data_key]

        # Convert Container data values to string to match table data types
        for key in container_data_values:
            container_data_values[key] = str(container_data_values[key])

        # Convert the table input values to a dict
        expected_data = table_to_dictionary(context)

        # Compare expected and actual values
        assert container_data_values == expected_data
    except KeyError:
        raise KeyError(
            f"The container {context.container.name} does not have a data key of {data_key}"
        )
    except AssertionError:
        raise AssertionError(
            f"The container data attribute {data_key} does not match the containers values"
        )


@then('there are at least "{quantity}" artifacts labeled "{artifact_label}"')
def validate_minimum_labeled_artifacts(
    context: Context, quantity: str, artifact_label: str
):
    """Validates that there are at least a minimum quantity of artifacts sharing the same label
    Example: Then there are at least "3" artifacts labeled as "event"
    Params:
        context (Context): scenario context
        quantity (str): desired minimum quantity
        artifact_label (str): artifact_label_match

    Raises:
        AssertionError: If the count of matching artifacts is lower than the requested amount

    """
    if not context.container:
        raise ContainerNotConfigured()

    artifact_labels = [artifact.label for artifact in context.container.artifacts]
    matching_count: int = artifact_labels(artifact_label)

    if not context.container.artifact_names.count(artifact_label) >= int(quantity):
        raise AssertionError(
            f"{quantity} labeled artifacts must be labeled as {artifact_label}, but only found {matching_count}"
        )


@then('the action "{action_name}" has the "{field}" below')
def validate_action_field(context: Context, action_name: str, field: str):
    """Validates an attribute of an action using a larger body of text

    Params:
        context (Context): scenario context
        action_name (str): Name of the action to validate
        field (str): Field of the action to validate

    Raises:
        ActionNotFound: If the requested action_name is not present on the container
        AttributeError: The the requested action field isn't a valid attribute
        AssertionError: If the value of the context.text field doesn't match the value

    """
    assert_container(context.container)
    action: Action = context.container.get_action(action_name)[0]

    if not action:
        raise ActionNotFound(f"The action {action_name} was not found. Check spelling")

    try:
        assert getattr(action, field)
    except:
        raise AttributeError(f"The field {field} is not a valid attribute on an action")
    try:
        assert str(getattr(action, field)) == context.text
    except:
        raise AssertionError(f"{getattr(action, field)} != {context.text}")


@then('the action "{action_name}" has the "{field}" of "{value}"')
def validate_action_attr(context: Context, action_name: str, field: str, value: str):
    """Validates an attribute of an action

    Parameters:
        context (Context): scenario context
        action_name (str): Name of the action to validate
        field (str): Attribute of the Action to check. See soarsdk.objects.Action
        value (str): Comparison or expected value

    Raises:
        AttributionError: If an invalid attribute of an action is provided
        AssertionError: If an the action's value and expected value do not match
    """
    assert_container(context.container)
    action: Action = context.container.get_action(action_name)[0]

    if not action:
        raise ActionNotFound(f"The action {action_name} was not found. Check spelling")

    if not hasattr(action, field):
        raise AttributeError(
            f"The field {field} is not a valid attribute on an action object"
        )

    assert str(getattr(action, field)) == value


@then("delete the container")
@then("the container is deleted")
def delete_container(context: Context):
    """Deletes the container within phantom & any associated artifacts"""
    context.phantom.delete_container(context.container)


@then('"{comment}" is commented')
@then('the comment "{comment}" is added')
def validate_comment(context: Context, comment: str):
    """Checks if a comment is added to the container

    Parameters:
        context (Context): scenario context
        comment (str): Name of  note to search for

    Raises:
        AssertionError: If the comment isn't found on the container
    """
    if not comment in context.container.comments:
        raise AssertionError(f"Comment {comment} not in {context.container.comments} ")


@then('the note "{note_title}" is created')
def validate_note(context: Context, note_title: str):
    """Validates that a note matching the provided name was added to the container

    Parameters:
        context (Context): scenario context
        note_title (str): Name of  note to search for

    Raises:
        AssertionError: If the note isn't found in the current notes
    """
    note_titles: list[str] = [note.title for note in context.container.notes]
    if not note_title in note_titles:
        raise AssertionError(
            f"Failed to find note {note_title}. Available notes: {note_titles}"
        )


@then('there are "{notes_quantity}" total notes')
def step_impl(context: Context, notes_quantity: str):
    """Validates that a note matching the provided name was added to the container

    Parameters:
        context (Context): scenario context
        note_quantity (str): Expected quantity of notes

    Raises:
        AssertionError: If the total number of notes does not match"""
    assert context.container.id
    assert len(context.container.notes) == int(notes_quantity)


@then('a container is created under the label "{container_label}"')
def step_impl(context: Context, container_label: str):
    """Switches the context container to the resulting container. Finds a "create" container action under the existing
    context.container actions

    Parameters:
        context (Context): scenario context
        container_label (str): Label where the created container was created

    Raises:
        Exception: The step was unable to process or find the resulting container_id
    """
    assert_container(context.container)

    resulting_container_id: int = None

    for playbook in context.container.playbooks:
        for action in playbook.actions:
            if action.action == "create container" and action.status == "success":
                resulting_container_id = (
                    action.result_data[0].get("summary").get("container_id")
                )
                break

    if not resulting_container_id:
        raise Exception(
            f"Unexpected error has ocurred. Unable to find resulting container from source container {context.container.id}"
        )

    context.container = Container(id=resulting_container_id)
    context.phantom.update_container_values(context.container)
    assert context.container.label == container_label
