from fileinput import filename
import webbrowser
from behave import then, given
import os
import pickle
import pathlib
from features.steps.utility_functions import table_to_array
import json
import time
from behave.runner import Context
from soarsdk.objects import Container

"""
Module for misc functions and utilities 
"""


@then('wait for "{count}" seconds')
def wait(context: Context, count: str):
    """Waits for a period of time. Useful when working with an active playbook or a delayed result.

    Args:
        context (Context): Scenario context object
        count (str): Duration of seconds
    """
    time.sleep(int(count))


@then("debug")
@then("throw error")
def step_impl(context: Context):
    """Stops the execution of the test and prints the Container object to the console"""
    print(context.container.toJson())
    assert 1 == 2


@then("the browser is opened")
@then("open the browser")
def open_browser(context: Context) -> None:
    """
    Forces the container to open on the default web browser.
    """
    url = f"{context.phantom.base_url}mission/{context.container.id}/analyst/timeline"
    webbrowser.open_new_tab(url)


@then("the resources are deleted")
def delete_container(context: Context) -> None:
    """Deletes the container and artifacts from phantom"""
    context.phantom.delete_container(context.container)


@given('the existing container "{container_id}"')
def download_context_container(context: Context, container_id: int):
    """Downloads an existing container and stores it into the context. Useful when debugging existing containers"""
    context.container: Container = Container(id=container_id)
    context.phantom.update_container_values(context.container)


@then('ask the user to "{prompt}"')
def confirmation_prompt(context, prompt):
    """Pauses the behave runner and awaits user confirmation to continue. This step should only be used for debugging purposes
    and should not be merged into any finalized Feature files.
    """
    input(f"\n\n{prompt}\n\nPress enter to continue\n\n")
