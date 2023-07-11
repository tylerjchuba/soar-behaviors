from email import header
import behave
import soarsdk
import json
from behave.model import Row, Table
from typing import Generator, Union, Any
from behave.runner import Context
from soarsdk.objects import Container, Artifact
import re


def row_as_dict(row: Row) -> dict:
    """Returns as a context.table.row as a dictionary.
    Assumes the first row (row[0]) is the key and the second is the value.
    """
    return {heading: row[heading] for heading in row.headings}


def dict_parse(raw_value: str) -> dict:
    """Converts the dictionary mapping "cefKey:cefValue" to a python dictionary object. Accepts raw dictionaries too
    This is the standard input for dictionary in the library in user defined values. Also supports declaration with curly brackets
    """
    parsed_dictionary: dict = {}
    if ":" in raw_value:
        items = raw_value.split(":")
        parsed_dictionary = {items[0]: items[1]}
    else:
        if "{" in raw_value and "}" in raw_value:
            return dict(json.loads(raw_value))
    for k, v in parsed_dictionary.items():
        if "[" in v and "]" in v:
            v = list_parse(v)
    return parsed_dictionary


def list_parse(user_in: str) -> list:
    """Converts a one line list into a python list"""
    output = user_in.strip("[]").split(",")
    for i, item in enumerate(output):
        # remove any leading whitespace from formatting
        changed_item = item.lstrip(" ")
        changed_item = changed_item.rstrip(" ")
        output[i] = changed_item

    return output


def artifact_with_cef(context: Context, cef_pair: str, artifact_name: str) -> None:
    """Assign a dictionary item to a given artifact's cef.
    Artifact must already be declared and assigned to the context.container
    """
    artifact: Artifact = context.container.get_artifact(artifact_name)

    try:
        assert artifact
    except AssertionError:
        raise AssertionError("Artifact failed to be found; check artifact_name")

    cef: dict = dict_parse(cef_pair)
    for k, v in cef.items():
        artifact.cef[k] = v


def table_to_dictionary(context: Context) -> dict:
    """Converts a context table into a python dictionary. Table must have headers (the first row are the headers).
    Only works with one row of actual values. Otherwise, use table_to_array()

    Returns:
        table_dict: dictionary representing table

    Examples:
        Given the following table
            | name   | Hank |
            | height | 72   |
            | age    | 30   |

        Given the following table
            | key    | value |
            | name   | Hank |
            | height | 72   |
            | age    | 30   |

        Both yield the following dictionary:
            {
                'name': 'Hank',
                'height': 72,
                'age': 30
            }


    """
    table_dict = {}
    headings = context.table.headings
    if len(headings) == 2:
        # Support for legacy tables, not recommended
        if "key" not in headings and "value" not in headings:
            # Assign the headings as row
            table_dict[headings[0]] = headings[1]
            # Assign the rows
            for row in context.table.rows:
                table_dict[row[0]] = row[1]
        else:
            # Skip assign the headings row as they are actually headings
            for row in context.table.rows:
                table_dict[row["key"]] = row["value"]
    else:
        return table_to_array(context.table)[0]

    # Process any configured variable replacements
    return context_variable_replacement(table_dict, context.replacement_vars)


def table_to_prompt(table: Table) -> dict:
    """Converts a context table into a properly created prompt for a playbook object"""
    prompt_dict: dict = {}
    headers = table.headings
    # assign headers as first entry -> headers aren't classified as rows for iteration
    prompt_dict[headers[0]] = [headers[1]]
    for row in table:
        prompt_id = row[0]
        prompt_response = row[1]
        if prompt_id in prompt_dict:
            prompt_dict[prompt_id].append(prompt_response)
        else:
            prompt_dict[prompt_id] = [prompt_response]
    return prompt_dict


def table_to_array(table: Table):
    """Converts a table to array (list of dictionaries) and maps any corresponding formatting to a python object"""
    table_array = []
    row_dict = {}

    for row in table.rows:
        for head in table.headings:
            v = row[head]
            # check for our syntax
            if ":" in v and "{" not in v:
                v = dict_parse(v)
            # raw string dictionary
            if "{" in v and "}" in v:
                v = dict(json.loads(v))
            # form list objects
            if "[" in v and "]" in v:
                v = list_parse(v)
            # remove whitespace from list objects
            if isinstance(v, list):
                for i, list_item in enumerate(v):
                    v[i] = list_item.lstrip(" ").rstrip(" ")
            row_dict[head] = v

        table_array.append(row_dict)
        row_dict = {}

    return table_array


def table_to_list(table: Table, columns=1, headers=False) -> list:
    """Converts a context table into a list

    Args:
        table ([behave.table]): table of the step's context
        columns (int, optional): [The amount of columns in the table]. Defaults to 1.

    Returns:
        list
    """
    table_list = []
    if not headers:
        table_list.append(table.headings[0])
    for row in table.rows:
        for i in range(0, columns):
            table_list.append(row[i])
    return table_list


def assert_equal_unordered_lists(expected_list: list, actual_list: list) -> bool:
    """Asserts and validates that the two lists contain the same values. The expected list is the
    MINIMUM values that should be found - does not account for varying lengths
    """
    differences: set = set(expected_list) - set(actual_list)
    if len(differences) != 0:
        raise AssertionError(
            f"The values expected in the list are not present inside the actual data. Missing values: {differences}"
        )


def json_key_finder(lookup_key: str, json_object: Union[dict, list]) -> Generator:
    """Recurse though a JSON object and return a generator representing all matches

    Parameters:
        lookup_key (str): The dictionary key value we're attempting to locate
        json_object (dict | list): JSON data structure potentially containing the desired key

    """
    if isinstance(json_object, dict):
        for key, value in json_object.items():
            if key == lookup_key:
                yield value
            else:
                yield from json_key_finder(lookup_key, value)
    elif isinstance(json_object, list):
        for item in json_object:
            yield from json_key_finder(lookup_key, item)


def context_variable_replacement(value: Any, replace_dict: dict) -> Any:
    """Identifies and replaces strings in nested data structures. Library format for variable replacement is
     ${variable_name}
    Args:
        value (Any): Recursive target to replace with
        replace_dict (dict): Context variables assigned with other steps
    Returns:
        Any: Initial object modified
    """
    variable_pattern: str = r"\${(.*)\}"
    if isinstance(value, str):
        regex_match: re.Match = re.findall(variable_pattern, value)
        for match in regex_match:
            if match in replace_dict:
                return re.sub(variable_pattern, str(replace_dict[match]), value)
    elif isinstance(value, dict):
        for key, val in value.items():
            value[key] = context_variable_replacement(val, replace_dict)
    elif isinstance(value, (list, tuple)):
        value = type(value)(
            context_variable_replacement(v, replace_dict) for v in value
        )
    elif isinstance(value, soarsdk.objects.PhantomObject):
        for k, v in value.__dict__.items():
            if v:
                v = context_variable_replacement(v, replace_dict)
    return value
