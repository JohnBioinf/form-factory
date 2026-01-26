"""Generate Dash Bootstrap forms from Pydantic v2 models.

dash-form-factory provides a factory pattern for creating Dash forms from
Pydantic models. Use InputField placeholders in your layout, then let
FormFactory replace them with actual form components.

Example:
    >>> from pydantic import BaseModel, Field
    >>> from typing import Annotated
    >>> import dash_bootstrap_components as dbc
    >>> from dash_form_factory import FormFactory, InputField
    >>>
    >>> class ContactForm(BaseModel):
    ...     name: Annotated[str, Field(
    ...         "",
    ...         title="Name",
    ...         description="Your name",
    ...         json_schema_extra={"type": "text"}
    ...     )]
    >>>
    >>> layout = dbc.Card([InputField("name")])
    >>> factory = FormFactory(ContactForm, layout)
    >>> form = factory.process_layout(factory.layout)
"""

from dash_form_factory.factory import FormFactory
from dash_form_factory.placeholder import InputField

__all__ = ["FormFactory", "InputField"]
__version__ = "0.1.0"
