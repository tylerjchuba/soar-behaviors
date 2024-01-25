from soarsdk.objects import Container
from soarsdk.objects import Playbook
from soarsdk.objects import Artifact
from soarsdk.objects import Note
from utility_functions import *
from exceptions import *
from behave import then, when
from behave.model import Row, Table


@when("the playbooks are run")
def run_all_playbooks(context: Context):
    """Runs through every playbook declared inside the FeatureFile; answering prompts as they appear
    Example: When the playbook are run

    Params:
        context (Context): scenario context object

    Raises:
        PlaybookNotRan: If the playbook failed to be ran

    """
    context.phantom.run_playbooks(context.container)
    if context.container.playbooks:
        for playbook in context.container.playbooks:
            try:
                assert playbook.id
            except:
                raise PlaybookNotRan(f"Playbook {playbook.name} failed to be run")


@then("the results are collected")
def step_impl(context):
    """Updates every object inside the container with the newest information. Use this after running a playbook to check the values of your test resources
    Example: Then the results are collected
    """
    context.phantom.update_container_values(context.container)


@when('the playbook "{playbook_name}" is ran')
def step_impl(context, playbook_name):
    """Run a given playbook after connecting to sandbox. Useful when multiple playbooks are required to run in different orders"""
    playbook: Playbook = context.container.get_playbook(name=playbook_name)
    if not playbook:
        playbook = Playbook(name=playbook_name)
        context.container.add_playbooks(playbook)

    if "ignore_exception" in context.scenario.tags:
        try:
            context.phantom.run_playbooks(context.container)
        except soarsdk.exceptions.PlaybookException:
            pass
    else:
        context.phantom.run_playbooks(context.container)


@when("the container and artifacts are created")
def step_impl(context):
    """Creates the Container & Artifact objects within Phantom. This starts making resources in Phantom to run playbook on.
    Declare any resources (containers/artifacts) before using this step.
    Example: Then the container and artifacts are created
    """
    if not context.container:
        raise ContainerNotConfigured()

    context.phantom.create_container(context.container)

    assert context.container.id
    for artifact in context.container.artifacts:
        assert artifact.id
        assert artifact.container


@then('the note "{note_title}" with the content of "{note_content}"')
def step_impl(context, note_title, note_content):
    """Creates a note on the initialized container"""
    if not context.container:
        raise ContainerNotConfigured()

    new_note: Note = Note(title=note_title, content=note_content)
    context.phantom.create_note(context.container, new_note)


@then("close the container")
@then("the container is closed")
def step_impl(context):
    if not context.container:
        raise ContainerNotConfigured()

    context.container.status = "closed"
    context.phantom.modify_container_values(context.container)
