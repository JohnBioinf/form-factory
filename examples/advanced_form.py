"""Advanced example: Form with all supported field types.

This example demonstrates all field types supported by dash-form-factory:
- text: Text input
- email: Email input
- integer: Number input with step=1
- float: Number input with step="any"
- checkbox: Checkbox
- date-picker: Date range picker
- select: Single-choice dropdown
- dropdown-checklist: Dropdown with checklist

Run with: uv run python examples/advanced_form.py
Then open: http://127.0.0.1:8050
"""

import re
from typing import Annotated, Any, Literal

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, callback, html
from pydantic import BaseModel, Field, model_validator

from dash_form_factory import FormFactory, InputField


# Define model with all supported field types
class AdvancedForm(BaseModel):
    """Form model demonstrating all field types."""

    # Text field
    username: Annotated[
        str,
        Field(
            "",
            min_length=1,
            title="Username",
            description="Choose a unique username",
            json_schema_extra={"type": "text"},
        ),
    ]

    # Email field — defaults to "" but validated as EmailStr when non-empty
    email: Annotated[
        str,
        Field(
            "",
            title="Email",
            description="Your email address",
            json_schema_extra={"type": "email"},
        ),
    ]

    # Integer field
    age: Annotated[
        int,
        Field(
            18,
            ge=18,
            le=70,
            title="Age",
            description="Must be between 18 and 70",
            json_schema_extra={"type": "integer"},
        ),
    ]

    # Float field
    salary: Annotated[
        float,
        Field(
            0.0,
            ge=0,
            title="Expected Salary",
            description="Annual salary in thousands (must be positive)",
            json_schema_extra={"type": "float"},
        ),
    ]

    # Checkbox field
    newsletter: Annotated[
        bool,
        Field(
            False,
            title="Subscribe to Newsletter",
            description="Receive weekly updates",
            json_schema_extra={"type": "checkbox"},
        ),
    ]

    # Date picker field
    availability: Annotated[
        list[str],
        Field(
            ["2024-01-01", "2024-12-31"],
            title="Availability Period",
            description="When are you available?",
            json_schema_extra={"type": "date-picker"},
        ),
    ]

    # Select field
    role: Annotated[
        Literal["developer", "designer", "manager", "other"],
        Field(
            "developer",
            title="Role",
            description="Your primary role",
            json_schema_extra={"type": "select"},
        ),
    ]

    @model_validator(mode="after")
    def validate_newsletter_requires_email(self) -> "AdvancedForm":
        """Newsletter subscription requires a valid email address."""
        if self.email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", self.email):
            raise ValueError("Please enter a valid email address")
        if self.newsletter and not self.email:
            raise ValueError("Email is required when subscribing to the newsletter")
        return self

    # Dropdown checklist field — options are grouped by first word when using
    # a custom checklist_formatter (see grouped_checklist_formatter below)
    skills: Annotated[
        list[
            Literal[
                "backend python",
                "backend java",
                "backend go",
                "frontend javascript",
                "frontend typescript",
                "frontend css",
                "devops docker",
                "devops kubernetes",
            ]
        ],
        Field(
            [],
            title="Skills",
            description="Select your skills by category",
            json_schema_extra={"type": "dropdown-checklist"},
        ),
    ]


def grouped_checklist_formatter(
    choices: tuple[str, ...], active: bool
) -> list[dict[str, Any]]:
    """Format checklist options with Hr dividers between prefix groups.

    Groups options by their first word and inserts a horizontal rule between
    groups. This is useful when choices follow a "category item" naming pattern.
    """
    options: list[dict[str, Any]] = []
    prefix: str | None = None
    for choice in choices:
        label = choice.replace("_", " ")
        if prefix is None or not label.startswith(prefix):
            prefix = label.split(" ")[0]
            if len(options) > 0:
                previous_label = options[-1]["label"]
                options[-1]["label"] = [html.Div(previous_label), html.Hr()]
        options.append({"label": label, "value": choice, "disabled": not active})
    return options


# Create layout with all field types
layout_template = dbc.Card(
    [
        dbc.CardHeader("Advanced Form Demo", className="text-center fs-4"),
        dbc.CardBody(
            [
                # Text and Email in a row
                dbc.Row(
                    [
                        dbc.Col(InputField("username"), md=6),
                        dbc.Col(InputField("email"), md=6),
                    ],
                    className="mb-3",
                ),
                # Numeric fields in a row
                dbc.Row(
                    [
                        dbc.Col(InputField("age"), md=6),
                        dbc.Col(InputField("salary"), md=6),
                    ],
                    className="mb-3",
                ),
                # Date picker
                dbc.Row([dbc.Col(InputField("availability"))], className="mb-3"),
                # Select
                dbc.Row([dbc.Col(InputField("role"))], className="mb-3"),
                # Dropdown checklist
                dbc.Row([dbc.Col(InputField("skills"))], className="mb-3"),
                # Checkbox
                dbc.Row([dbc.Col(InputField("newsletter"))], className="mb-3"),
                # Submit button
                dbc.Button(
                    "Submit", id="submit-btn", color="primary", className="w-100"
                ),
            ]
        ),
    ],
    className="m-4",
    style={"max-width": "800px"},
)

# Process layout
factory = FormFactory(
    AdvancedForm, layout_template, checklist_formatter=grouped_checklist_formatter
)
form_layout = factory.process_layout(factory.layout)

# Create app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(
    [
        html.H1("All Field Types Demo", className="text-center my-4"),
        html.Div(form_layout, className="d-flex justify-content-center"),
        html.Div(id="output", className="text-center mt-4 mx-4"),
    ]
)


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
def handle_submit(**inputs):
    """Handle form submission."""
    valid, output_dict = factory.validate_callback(inputs)

    if valid:
        # Build summary of submitted values
        summary = html.Div(
            [
                html.H5("Submitted Values:"),
                html.Ul(
                    [
                        html.Li(f"Username: {inputs['username']}"),
                        html.Li(f"Email: {inputs['email']}"),
                        html.Li(f"Age: {inputs['age']}"),
                        html.Li(f"Salary: ${inputs['salary']}k"),
                        html.Li(
                            f"Newsletter: {'Yes' if inputs['newsletter'] else 'No'}"
                        ),
                        html.Li(
                            f"Availability: {inputs['availability_start_date']} "
                            f"to {inputs['availability_end_date']}"
                        ),
                        html.Li(f"Role: {inputs['role']}"),
                        html.Li(
                            f"Skills: {', '.join(inputs['skills']) or 'None'}"
                        ),
                    ]
                ),
            ]
        )
        output_dict["output"] = dbc.Alert(summary, color="success")
    else:
        output_dict["output"] = dbc.Alert(
            "Please correct the errors above.", color="danger"
        )

    return output_dict


if __name__ == "__main__":
    app.run(debug=True)
