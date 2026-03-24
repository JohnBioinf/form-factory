"""Pytest fixtures for dash-form-factory tests."""

from typing import Annotated, Literal

import pytest
from pydantic import BaseModel, Field


@pytest.fixture
def simple_model():
    """Simple Pydantic model with text and email fields."""

    class SimpleConfig(BaseModel):
        name: Annotated[
            str,
            Field(
                "John Doe",
                title="Name",
                description="Your full name",
                json_schema_extra={"type": "text"},
            ),
        ]
        email: Annotated[
            str,
            Field(
                "john@example.com",
                title="Email",
                description="Your email address",
                json_schema_extra={"type": "email"},
            ),
        ]

    return SimpleConfig


@pytest.fixture
def numeric_model():
    """Pydantic model with numeric fields."""

    class NumericConfig(BaseModel):
        count: Annotated[
            int,
            Field(
                10,
                title="Count",
                description="Number of items",
                json_schema_extra={"type": "integer"},
            ),
        ]
        price: Annotated[
            float,
            Field(
                19.99,
                title="Price",
                description="Price in dollars",
                json_schema_extra={"type": "float"},
            ),
        ]

    return NumericConfig


@pytest.fixture
def checkbox_model():
    """Pydantic model with checkbox field."""

    class CheckboxConfig(BaseModel):
        accept_terms: Annotated[
            bool,
            Field(
                False,
                title="Accept Terms",
                description="I accept the terms and conditions",
                json_schema_extra={"type": "checkbox"},
            ),
        ]

    return CheckboxConfig


@pytest.fixture
def date_picker_model():
    """Pydantic model with date picker field."""

    class DateConfig(BaseModel):
        date_range: Annotated[
            list[str],
            Field(
                ["2024-01-01", "2024-12-31"],
                title="Date Range",
                description="Select a date range",
                json_schema_extra={"type": "date-picker"},
            ),
        ]

    return DateConfig


@pytest.fixture
def dropdown_checklist_model():
    """Pydantic model with dropdown checklist field."""

    class DropdownConfig(BaseModel):
        options: Annotated[
            list[Literal["option_a", "option_b", "option_c"]],
            Field(
                [],
                title="Options",
                description="Select options",
                json_schema_extra={"type": "dropdown-checklist"},
            ),
        ]

    return DropdownConfig


@pytest.fixture
def select_model():
    """Pydantic model with select field."""

    class SelectConfig(BaseModel):
        color: Annotated[
            Literal["red", "green", "blue"],
            Field(
                "red",
                title="Color",
                description="Pick a color",
                json_schema_extra={"type": "select"},
            ),
        ]

    return SelectConfig


@pytest.fixture
def make_factory():
    """Helper to create a FormFactory with a simple layout."""
    from dash import html

    from dash_form_factory import FormFactory, InputField

    def _make(model, *field_names, active=True):
        layout = html.Div([InputField(f) for f in field_names])
        return FormFactory(model, layout, active=active)

    return _make
