"""Tests for FormFactory class."""

from typing import Annotated, Literal

import dash_bootstrap_components as dbc
import pytest
from dash import html
from pydantic import BaseModel, Field

from dash_form_factory import FormFactory, InputField


# Models for parametrized create_component tests
class _SimpleModel(BaseModel):
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


class _NumericModel(BaseModel):
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


class _CheckboxModel(BaseModel):
    accept_terms: Annotated[
        bool,
        Field(
            False,
            title="Accept Terms",
            description="I accept the terms and conditions",
            json_schema_extra={"type": "checkbox"},
        ),
    ]


class _DatePickerModel(BaseModel):
    date_range: Annotated[
        list[str],
        Field(
            ["2024-01-01", "2024-12-31"],
            title="Date Range",
            description="Select a date range",
            json_schema_extra={"type": "date-picker"},
        ),
    ]


class _DropdownChecklistModel(BaseModel):
    options: Annotated[
        list[Literal["option_a", "option_b", "option_c"]],
        Field(
            [],
            title="Options",
            description="Select options",
            json_schema_extra={"type": "dropdown-checklist"},
        ),
    ]


class _SelectModel(BaseModel):
    color: Annotated[
        Literal["red", "green", "blue"],
        Field(
            "red",
            title="Color",
            description="Pick a color",
            json_schema_extra={"type": "select"},
        ),
    ]


class _SelectNoDefaultModel(BaseModel):
    color: Annotated[
        Literal["red", "green", "blue"],
        Field(
            title="Color",
            description="Pick a color",
            json_schema_extra={"type": "select"},
        ),
    ]


class TestFormFactoryInit:
    """Tests for FormFactory initialization."""

    def test_init_with_model_class(self, simple_model, make_factory):
        """FormFactory accepts a Pydantic model class."""
        factory = make_factory(simple_model, "name")

        assert factory.pymodel_class == simple_model
        assert factory.pymodel_instance is None
        assert factory.active is True

    def test_init_with_model_instance(self, simple_model, make_factory):
        """FormFactory accepts a Pydantic model instance."""
        instance = simple_model(name="Jane", email="jane@example.com")
        factory = make_factory(instance, "name")

        assert factory.pymodel_class == simple_model
        assert factory.pymodel_instance == instance

    def test_init_inactive(self, simple_model, make_factory):
        """FormFactory can be initialized as inactive."""
        factory = make_factory(simple_model, "name", active=False)

        assert factory.active is False

    def test_layout_is_deep_copied(self, simple_model):
        """FormFactory deep copies the layout."""
        layout = html.Div([InputField("name")])
        factory = FormFactory(simple_model, layout)

        assert factory.layout is not layout


class TestExtractFieldNames:
    """Tests for extract_field_names method."""

    def test_extract_single_field(self, simple_model, make_factory):
        """Extracts field name from single InputField."""
        factory = make_factory(simple_model, "name")

        assert factory.fields_website == ["name"]

    def test_extract_multiple_fields(self, simple_model, make_factory):
        """Extracts field names from multiple InputFields."""
        factory = make_factory(simple_model, "name", "email")

        assert factory.fields_website == ["name", "email"]

    def test_extract_nested_fields(self, simple_model):
        """Extracts field names from nested layout."""
        layout = dbc.Card(
            [
                dbc.CardBody(
                    [
                        dbc.Row([dbc.Col(InputField("name"))]),
                        dbc.Row([dbc.Col(InputField("email"))]),
                    ]
                )
            ]
        )
        factory = FormFactory(simple_model, layout)

        assert factory.fields_website == ["name", "email"]

    def test_extract_from_list(self, simple_model):
        """Extracts field names from list layout."""
        layout = [InputField("name"), InputField("email")]
        factory = FormFactory(simple_model, layout)

        assert factory.fields_website == ["name", "email"]

    def test_no_input_fields(self, simple_model):
        """Returns empty list when no InputFields present."""
        layout = html.Div([html.P("No fields here")])
        factory = FormFactory(simple_model, layout)

        assert factory.fields_website == []


class TestCreateComponent:
    """Tests for create_component method."""

    @pytest.mark.parametrize(
        "model_class,field_name",
        [
            pytest.param(_SimpleModel, "name", id="text"),
            pytest.param(_SimpleModel, "email", id="email"),
            pytest.param(_NumericModel, "count", id="integer"),
            pytest.param(_NumericModel, "price", id="float"),
            pytest.param(_CheckboxModel, "accept_terms", id="checkbox"),
            pytest.param(_DatePickerModel, "date_range", id="date-picker"),
            pytest.param(_DropdownChecklistModel, "options", id="dropdown-checklist"),
            pytest.param(_SelectModel, "color", id="select"),
        ],
    )
    def test_creates_component_for_field_type(
        self, model_class, field_name, make_factory
    ):
        """Creates correct component for each supported field type."""
        factory = make_factory(model_class, field_name)
        components = factory.create_component(field_name)

        assert isinstance(components, list)

    def test_inactive_field_is_disabled(self, simple_model, make_factory):
        """Inactive factory creates disabled components."""
        factory = make_factory(simple_model, "name", active=False)
        components = factory.create_component("name")

        # Find the input component and check it's disabled
        input_component = None
        for comp in components:
            if hasattr(comp, "disabled"):
                input_component = comp
                break

        assert input_component is not None
        assert input_component.disabled is True

    def test_unknown_field_type_raises(self, make_factory):
        """Unknown field type raises ValueError."""

        class BadModel(BaseModel):
            bad_field: Annotated[
                str,
                Field("", json_schema_extra={"type": "unsupported_type"}),
            ]

        factory = make_factory(BadModel, "bad_field")

        with pytest.raises(ValueError, match="Unknown field_type"):
            factory.create_component("bad_field")

    def test_uses_instance_values(self, simple_model, make_factory):
        """FormFactory uses values from model instance."""
        instance = simple_model(name="Custom Name", email="custom@example.com")
        factory = make_factory(instance, "name")
        components = factory.create_component("name")

        # Find the input and check its value
        for comp in components:
            if hasattr(comp, "value") and comp.value is not None:
                assert comp.value == "Custom Name"
                break


class TestProcessLayout:
    """Tests for process_layout method."""

    def test_replaces_input_field(self, simple_model):
        """InputField is replaced with actual components."""
        layout = html.Div([InputField("name")])
        factory = FormFactory(simple_model, layout)
        processed = factory.process_layout(factory.layout)

        # The InputField should be replaced with a list of components
        assert not any(isinstance(c, InputField) for c in processed.children)

    def test_preserves_non_input_field_content(self, simple_model):
        """Non-InputField content is preserved."""
        layout = html.Div([html.H1("Title"), InputField("name")])
        factory = FormFactory(simple_model, layout)
        processed = factory.process_layout(factory.layout)

        # H1 should still be there
        assert any(isinstance(c, html.H1) for c in processed.children)

    def test_handles_nested_layout(self, simple_model):
        """Processes nested layouts correctly."""
        layout = dbc.Card(
            [
                dbc.CardHeader("Form"),
                dbc.CardBody([InputField("name")]),
            ]
        )
        factory = FormFactory(simple_model, layout)
        processed = factory.process_layout(factory.layout)

        # Should return processed layout without InputFields
        assert processed is not None


class TestProduceCallbackOutputs:
    """Tests for produce_callback_outputs method."""

    def test_outputs_for_text_field(self, simple_model, make_factory):
        """Produces correct outputs for text field."""
        factory = make_factory(simple_model, "name")
        outputs = factory.produce_callback_outputs()

        assert "name_valid" in outputs
        assert "name_invalid" in outputs
        assert "name_feedback_children" in outputs

    def test_outputs_for_checkbox_field(self, checkbox_model, make_factory):
        """Checkbox fields have limited outputs."""
        factory = make_factory(checkbox_model, "accept_terms")
        outputs = factory.produce_callback_outputs()

        # Checkboxes don't have valid/invalid outputs
        assert "accept_terms_valid" not in outputs
        assert "accept_terms_feedback_children" in outputs


class TestProduceCallbackInputs:
    """Tests for produce_callback_inputs method."""

    def test_inputs_for_text_field(self, simple_model, make_factory):
        """Produces correct inputs for text field."""
        factory = make_factory(simple_model, "name")
        inputs = factory.produce_callback_inputs()

        assert "name" in inputs

    def test_inputs_with_use_state(self, simple_model, make_factory):
        """Produces State objects when use_state=True."""
        from dash import State

        factory = make_factory(simple_model, "name")
        inputs = factory.produce_callback_inputs(use_state=True)

        assert isinstance(inputs["name"], State)

    def test_inputs_for_date_picker(self, date_picker_model, make_factory):
        """Date picker produces start_date and end_date inputs."""
        factory = make_factory(date_picker_model, "date_range")
        inputs = factory.produce_callback_inputs()

        assert "date_range_start_date" in inputs
        assert "date_range_end_date" in inputs


class TestValidateCallback:
    """Tests for validate_callback method."""

    def test_valid_data_returns_true(self, simple_model, make_factory):
        """Valid form data returns (True, output_dict)."""
        factory = make_factory(simple_model, "name", "email")

        form_data = {"name": "John", "email": "john@example.com"}
        valid, output_dict = factory.validate_callback(form_data)

        assert valid is True
        assert output_dict["name_valid"] is True


class TestSelectField:
    """Tests for the select field type."""

    def test_creates_dbc_select(self, make_factory):
        """Select field creates a dbc.Select component."""
        factory = make_factory(_SelectModel, "color")
        components = factory.create_component("color")

        select_components = [c for c in components if isinstance(c, dbc.Select)]
        assert len(select_components) == 1

    def test_options_from_literal(self, make_factory):
        """Options are built from Literal values with underscore-to-space labels."""
        factory = make_factory(_SelectModel, "color")
        components = factory.create_component("color")

        select = [c for c in components if isinstance(c, dbc.Select)][0]
        assert select.options == [
            {"label": "red", "value": "red"},
            {"label": "green", "value": "green"},
            {"label": "blue", "value": "blue"},
        ]

    def test_uses_default_value(self, make_factory):
        """Select uses the field's default value."""
        factory = make_factory(_SelectModel, "color")
        components = factory.create_component("color")

        select = [c for c in components if isinstance(c, dbc.Select)][0]
        assert select.value == "red"

    def test_fallback_to_first_literal(self, make_factory):
        """Select without default uses first Literal value."""
        factory = make_factory(_SelectNoDefaultModel, "color")
        components = factory.create_component("color")

        select = [c for c in components if isinstance(c, dbc.Select)][0]
        assert select.value == "red"

    def test_has_valid_invalid_outputs(self, make_factory):
        """Select field gets valid/invalid callback outputs."""
        factory = make_factory(_SelectModel, "color")
        outputs = factory.produce_callback_outputs()

        assert "color_valid" in outputs
        assert "color_invalid" in outputs
        assert "color_feedback_children" in outputs

    def test_uses_form_feedback(self, make_factory):
        """Select field uses dbc.FormFeedback for validation display."""
        factory = make_factory(_SelectModel, "color")
        components = factory.create_component("color")

        feedback = [c for c in components if isinstance(c, dbc.FormFeedback)]
        assert len(feedback) == 1

    def test_disabled_when_inactive(self, make_factory):
        """Select is disabled with gray background when inactive."""
        factory = make_factory(_SelectModel, "color", active=False)
        components = factory.create_component("color")

        select = [c for c in components if isinstance(c, dbc.Select)][0]
        assert select.disabled is True
        assert select.style == {"background-color": "#e9ecef"}

    def test_validate_callback(self, make_factory):
        """Select validation sets valid/invalid correctly."""
        factory = make_factory(_SelectModel, "color")
        valid, output_dict = factory.validate_callback({"color": "red"})

        assert valid is True
        assert output_dict["color_valid"] is True


class TestDropdownChecklistFeedback:
    """Regression tests for dropdown-checklist feedback bug fix."""

    def test_uses_form_text_not_form_feedback(self, make_factory):
        """Dropdown-checklist uses FormText (not FormFeedback) for feedback."""
        factory = make_factory(_DropdownChecklistModel, "options")
        components = factory.create_component("options")

        # Should NOT have FormFeedback (it can't work with DropdownMenu)
        feedback = [c for c in components if isinstance(c, dbc.FormFeedback)]
        assert len(feedback) == 0

        # Should have FormText with text-danger for error display
        form_texts = [c for c in components if isinstance(c, dbc.FormText)]
        danger_texts = [
            t for t in form_texts if getattr(t, "className", None) == "text-danger"
        ]
        assert len(danger_texts) == 1
