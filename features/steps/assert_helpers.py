import soarsdk
from soarsdk.objects import Artifact, Container
from exceptions import ContainerNotConfigured


"""
Module to store library related exceptions     
    
"""


def assert_artifact_in_container(artifact: Artifact, container: Container) -> None:
    """Validates that a provided artifact exists inside of the container @TODO

    Args:
        artifact (_type_): _description_
        container (_type_): _description_

    Raises:
        LookupError: _description_
    """
    try:
        assert isinstance(artifact, soarsdk.Artifact)
    except:
        raise LookupError(
            f"Artifact not found - check the artifact must be declared and the name must be the same string as the rest of the file. \n Available artifacts: {container.artifacts}"
        )


def assert_container(container: Container) -> None:
    """Validates a container exists with the minimum required attribute.

    Args:
        container (Container): Configured container

    Raises:
        ContainerNotConfigured: Exception to indicate a container needs to be created before process may proceed
    """
    try:
        assert container.name and container.label
    except AssertionError:
        raise ContainerNotConfigured(
            f"Container not configured. Declare a container with a name & label first using a Given step. See all_steps.feature for examples"
        )


def check_playbook_actions(playbooks, action_name, playbook_name=None):
    """Helper function to loop through playbook actions and compare results"""
    for playbook in playbooks:
        assert isinstance(playbook, soarsdk.Playbook)
        playbook_name = playbook_name if playbook_name else playbook.name

        if playbook.name in playbook_name:
            for action in playbook.actions:
                if action.name == action_name and action.status == "success":
                    return action.status
    return False
