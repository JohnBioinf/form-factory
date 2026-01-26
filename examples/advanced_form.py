"""Advanced example: Form with all supported field types.

This example demonstrates all field types supported by dash-form-factory:
- text: Text input
- email: Email input
- integer: Number input with step=1
- float: Number input with step="any"
- checkbox: Checkbox
- date-picker: Date range picker
- dropdown-checklist: Dropdown with checklist

Run with: uv run python examples/advanced_form.py
Then open: http://127.0.0.1:8050
"""

from typing import Annotated, List, Literal

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, callback, html
from pydantic import BaseModel, Field

from dash_form_factory import FormFactory, InputField


# Define model with all supported field types
class AdvancedForm(BaseModel):
    """Form model demonstrating all field types."""

    # Text field
    username: Annotated[
        str,
        Field(
            "",
            title="Username",
            description="Choose a unique username",
            json_schema_extra={"type": "text"},
        ),
    ]

    # Email field
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
            title="Age",
            description="Your age in years",
            json_schema_extra={"type": "integer"},
        ),
    ]

    # Float field
    salary: Annotated[
        float,
        Field(
            0.0,
            title="Expected Salary",
            description="Annual salary in thousands",
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
        List[str],
        Field(
            ["2024-01-01", "2024-12-31"],
            title="Availability Period",
            description="When are you available?",
            json_schema_extra={"type": "date-picker"},
        ),
    ]

    # Dropdown checklist field
    skills: Annotated[
        List[Literal["python", "javascript", "rust", "go"]],
        Field(
            [],
            title="Skills",
            description="Select your programming skills",
            json_schema_extra={"type": "dropdown-checklist"},
        ),
    ]


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
                # Dropdown checklist
                dbc.Row([dbc.Col(InputField("skills"))], className="mb-3"),
                # Checkbox
                dbc.Row([dbc.Col(InputField("newsletter"))], className="mb-3"),
                # Submit button
                dbc.Button("Submit", id="submit-btn", color="primary", className="w-100"),
            ]
        ),
    ],
    className="m-4",
    style={"max-width": "800px"},
)

# Process layout
factory = FormFactory(AdvancedForm, layout_template)
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
                        html.Li(f"Newsletter: {'Yes' if inputs['newsletter'] else 'No'}"),
                        html.Li(
                            f"Availability: {inputs['availability_start_date']} "
                            f"to {inputs['availability_end_date']}"
                        ),
                        html.Li(f"Skills: {', '.join(inputs['skills']) or 'None'}"),
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
