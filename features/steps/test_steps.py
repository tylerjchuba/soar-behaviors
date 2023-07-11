import utility_functions as utils
from behave import *
import soarsdk


@given("the following table")
def step_impl(context):
    context.data = utils.table_to_dictionary(context.table)


@given('the variable "{var_name}" is assigned as "{var_value}"')
def step_impl(context, var_name, var_value):
    context.replacement_vars[var_name] = var_value


@given("the table")
def step_impl(context):
    context.container = soarsdk.Container(**utils.table_to_dictionary(context.table))


@then("the value is replaced")
def step_impl(context):
    assert context.container.name == "New Container"
    print(context.container)
