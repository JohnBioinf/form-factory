"""Basic example: Generate a simple contact form.

This example demonstrates the core workflow of dash-form-factory:
1. Define a Pydantic model with json_schema_extra for field types
2. Create a layout with InputField placeholders
3. Use FormFactory to process the layout into actual components
4. Wire up validation callbacks

Run with: uv run python examples/basic_form.py
Then open: http://127.0.0.1:8050
"""

import re
from typing import Annotated

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, callback, html
from pydantic import BaseModel, Field, field_validator

from dash_form_factory import FormFactory, InputField


# 1. Define your Pydantic model with json_schema_extra
class ContactForm(BaseModel):
    """A simple contact form model."""

    name: Annotated[
        str,
        Field(
            "",
            min_length=1,
            title="Full Name",
            description="Enter your full name",
            json_schema_extra={"type": "text"},
        ),
    ]
    email: Annotated[
        str,
        Field(
            "",
            min_length=1,
            title="Email Address",
            description="We'll never share your email",
            json_schema_extra={"type": "email"},
        ),
    ]

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Check email format."""
        if v and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Please enter a valid email address")
        return v


# 2. Create layout with InputField placeholders
layout_template = dbc.Card(
    [
        dbc.CardHeader("Contact Us", className="text-center fs-4"),
        dbc.CardBody(
            [
                dbc.Row([dbc.Col(InputField("name"))], className="mb-3"),
                dbc.Row([dbc.Col(InputField("email"))], className="mb-3"),
                dbc.Button("Submit", id="submit-btn", color="primary"),
            ]
        ),
    ],
    className="m-4",
    style={"max-width": "500px"},
)

# 3. Process layout with FormFactory
factory = FormFactory(ContactForm, layout_template)
form_layout = factory.process_layout(factory.layout)

# 4. Create Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(
    [
        html.H1("Contact Form Example", className="text-center my-4"),
        html.Div(form_layout, className="d-flex justify-content-center"),
        html.Div(id="output", className="text-center mt-4"),
    ]
)


# 5. Register validation callback
@callback(
    output={
        **factory.produce_callback_outputs(),
        "output": Output("output", "children"),
    },
    inputs={
        **factory.produce_callback_inputs(),
        "submit": Input("submit-btn", "n_clicks"),
    },
    prevent_initial_call=True,
)
def validate_form(**inputs):
    """Validate form and show result."""
    valid, output_dict = factory.validate_callback(inputs)

    if valid:
        output_dict["output"] = dbc.Alert(
            f"Form submitted! Name: {inputs['name']}, Email: {inputs['email']}",
            color="success",
        )
    else:
        output_dict["output"] = dbc.Alert(
            "Please fix the errors above.", color="danger"
        )

    return output_dict


if __name__ == "__main__":
    app.run(debug=True)
