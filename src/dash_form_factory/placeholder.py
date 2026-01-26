"""Placeholder class for form fields."""


class InputField:
    """Placeholder class for form fields that will be replaced with actual components.

    Use InputField instances in your Dash layout to mark where form fields should
    be rendered. The FormFactory will replace these placeholders with actual
    Dash components based on the corresponding Pydantic model fields.

    Example:
        >>> from dash_form_factory import InputField
        >>> import dash_bootstrap_components as dbc
        >>>
        >>> layout = dbc.Card([
        ...     dbc.CardBody([
        ...         InputField("name"),
        ...         InputField("email"),
        ...     ])
        ... ])
    """

    def __init__(self, field_name: str) -> None:
        """Initialize with field name from Pydantic model.

        Args:
            field_name: The name of the field in the Pydantic model.
                       Must match exactly with a field defined in the model.
        """
        self.field_name = field_name
