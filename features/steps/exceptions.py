class ContainerNotConfigured(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(
            "The container has not been declared. Use a container declaring step within the configuration_steps.py file"
        )


class ContainerMissingAttributes(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("The container must have both a name and a label")


class ActionFailed(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PlaybookNotRan(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PlaybooksNotConfigured(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("No playbooks have been configured.")


class ArtifactNotConfigured(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ActionNotFound(Exception):
    def __init__(self, action_name: str, *args: object) -> None:
        super().__init__(f"The action {action_name} was not found on the container.")
