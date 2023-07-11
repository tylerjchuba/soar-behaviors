from soarsdk.objects import Container
from soarsdk.client import PhantomClient
from behave.runner import Context
from behave.model import Scenario, Step
import steps.utility_functions as utils
import re

# Optional configuration step
# def after_scenario(context, scenario):
#     if scenario.status == "failed" and context.container.id:
#         context.execute_steps("""then open the browser""")


def before_all(context: Context):
    context.replacement_vars: dict = {}


def before_scenario(context: Context, scenario: Scenario) -> None:
    """Initializes replacement variables and establishes a connection"""
    context.phantom = None

    if not context.phantom:
        raise NotImplementedError(
            f"Authentication and connection details not implemented in the environment.py file"
        )


def before_step(context: Context, step: Step) -> None:
    if hasattr(context, "container"):
        utils.context_variable_replacement(context.container, context.replacement_vars)


def after_step(context: Context, step: Step) -> None:
    if hasattr(context, "container"):
        utils.context_variable_replacement(context.container, context.replacement_vars)
