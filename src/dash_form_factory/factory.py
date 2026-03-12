"""Factory class to generate Dash forms from Pydantic models."""

from copy import deepcopy
from typing import Any, get_args

import dash_bootstrap_components as dbc  # type: ignore[import-untyped]
from dash import Input, Output, State, dcc, html
from pydantic_core import ValidationError

from dash_form_factory.placeholder import InputField


class FormFactory:
    """Factory class to generate a Dash form from a Pydantic model.

    FormFactory takes a Pydantic model and a layout containing InputField
    placeholders, then generates actual Dash form components with validation.

    Supported field types (via json_schema_extra):
        - "text": Text input (dbc.Input)
        - "email": Email input (dbc.Input with type="email")
        - "integer": Number input with step=1 (dbc.Input)
        - "float": Number input with step="any" (dbc.Input)
        - "checkbox": Checkbox (dbc.Checkbox)
        - "date-picker": Date range picker (dcc.DatePickerRange)
        - "dropdown-checklist": Dropdown with checklist (dbc.DropdownMenu)

    Example:
        >>> from pydantic import BaseModel, Field
        >>> from typing import Annotated
        >>> import dash_bootstrap_components as dbc
        >>>
        >>> class MyModel(BaseModel):
        ...     name: Annotated[str, Field(
        ...         "",
        ...         title="Name",
        ...         description="Your name",
        ...         json_schema_extra={"type": "text"}
        ...     )]
        >>>
        >>> layout = dbc.Card([InputField("name")])
        >>> factory = FormFactory(MyModel, layout)
        >>> form = factory.process_layout(factory.layout)
    """

    def __init__(self, pymodel: type[Any], layout: Any, active: bool = True) -> None:
        """Initialize FormFactory.

        Args:
            pymodel: Pydantic model class or instance to use for field definitions
            layout: Optional. For generate_form(): OrderedDict layout.
                   For process_layout(): Can be any Dash component tree.
            active: Whether form fields are active (editable) or disabled
        """
        # Store both the instance (for values) and the class (for schema)
        if isinstance(pymodel, type):
            # pymodel is a class
            self.pymodel_class = pymodel
            self.pymodel_instance = None
        else:
            # pymodel is an instance
            self.pymodel_class = type(pymodel)
            self.pymodel_instance = pymodel

        # Keep self.pymodel for backward compatibility
        self.pymodel = pymodel

        self.layout = deepcopy(layout)
        self.active = active
        self.type_to_component = {
            "email": dbc.Input,
            "text": dbc.Input,
            "float": dbc.Input,
            "integer": dbc.Input,
            "dropdown-checklist": dbc.DropdownMenu,
            "date-picker": dcc.DatePickerRange,
            "checkbox": dbc.Checkbox,
        }
        self.fields_website = self.extract_field_names(layout)

        self.fieldtypes_not_to_validate = [
            "checkbox",
            "dropdown-checklist",
            "date-picker",
        ]
        # Always preserve IDs for callbacks, regardless of active state
        # Disabled state and styling are handled in create_component()
        self.id_format = "{field_name}"
        self.feedback_id_format = "{field_name}_feedback"
        self.start_date_id_format = "{field_name}_start_date"
        self.end_date_id_format = "{field_name}_end_date"

    def create_component(self, field_name: Any) -> Any:
        """Create the Dash component for a field.

        Args:
            field_name: Name of the field in the Pydantic model

        Returns:
            A list of Dash components representing the form field
        """
        if not isinstance(field_name, str):
            return field_name
        field = self.pymodel_class.model_fields[field_name]

        field_type = field.json_schema_extra["type"]
        try:
            component_class = self.type_to_component[field_type]
        except KeyError:
            raise ValueError(f"Unknown field_type: {field_type}")

        props: dict[str, Any] = {}

        id_feedback = self.feedback_id_format.format(field_name=field_name)
        id_field = self.id_format.format(field_name=field_name)
        # Get value from instance if available, otherwise use default
        if self.pymodel_instance is not None:
            try:
                value = getattr(self.pymodel_instance, field_name)
            except AttributeError:
                value = field.default
        else:
            value = field.default

        if field_type in ["text", "email"]:
            props["type"] = "text" if field_type == "text" else "email"
            props["id"] = id_field
            props["value"] = value
            props["html_size"] = len(value) + 5
            props["style"] = {"width": "auto"}
            if not self.active:
                props["disabled"] = True
                props["style"].update({"background-color": "#e9ecef"})
        elif field_type in ["float", "integer"]:
            props["type"] = "number"
            props["step"] = 1 if field_type == "integer" else "any"
            props["required"] = True
            props["id"] = id_field
            props["value"] = value
            props["html_size"] = len(str(value)) + 5
            props["style"] = {"width": "auto"}
            if not self.active:
                props["disabled"] = True
                props["style"].update({"background-color": "#e9ecef"})
        elif field_type == "dropdown-checklist":
            props["label"] = field.title
            choices = get_args(get_args(field.annotation)[0])
            options: list[dict[str, Any]] = []
            prefix = "foobar"
            for choice in choices:
                label = choice.replace("_", " ")
                if not label.startswith(prefix):
                    prefix = label.split(" ")[0]
                    if len(options) > 0:
                        previous_label = options[-1]["label"]
                        options[-1]["label"] = [html.Div(previous_label), html.Hr()]
                options.append(
                    {"label": label, "value": choice, "disabled": not self.active}
                )
            checklist_props = {
                "options": options,
                "value": value,
                "id": id_field,
                "inline": False,
                "style": {"max-height": "300px", "overflow-y": "auto"},
                "className": "ms-2",
            }
            props["children"] = [dbc.Checklist(**checklist_props)]
        elif field_type == "date-picker":
            props["id"] = id_field
            props["start_date"] = value[0]
            props["end_date"] = value[1]
            props["initial_visible_month"] = value[1]
            if not self.active:
                props["disabled"] = True
        elif field_type == "checkbox":
            props["id"] = id_field
            props["value"] = value
            props["label"] = field.title
            if not self.active:
                props["disabled"] = True
        else:
            raise ValueError(f"Unknown field type {field_type}")

        if field_type == "checkbox":
            content = [
                component_class(**props),
                dbc.FormText(field.description),
                html.Br(),
                dbc.FormText(
                    "",
                    id=id_feedback,
                    className="text-danger",
                ),
            ]
        elif field_type == "date-picker":
            content = [
                dbc.Label(field.title),
                html.Br(),
                component_class(**props),
                html.Br(),
                dbc.FormText(field.description),
                dbc.FormText(id=id_feedback, className="text-danger"),
            ]
        else:
            content = [
                dbc.Label(field.title),
                component_class(**props),
                dbc.FormText(field.description),
                dbc.FormFeedback(id=id_feedback),
            ]
        return content

    def extract_field_names(self, layout: Any) -> list[str]:
        """Extract all field names from InputField instances in a layout tree.

        Args:
            layout: A Dash component tree that may contain InputField placeholders

        Returns:
            List of field names found in the layout
        """
        field_names: list[str] = []

        # If it's an InputField, extract the field name
        if isinstance(layout, InputField):
            field_names.append(layout.field_name)

        # If it's a Dash component with children, recursively extract from children
        elif hasattr(layout, "children"):
            field_names.extend(self.extract_field_names(layout.children))

        # If it's a list, recursively extract from each item
        elif isinstance(layout, list):
            for item in layout:
                field_names.extend(self.extract_field_names(item))

        # If it's a dict, recursively extract from each value
        elif isinstance(layout, dict):
            for value in layout.values():
                field_names.extend(self.extract_field_names(value))

        return field_names

    def process_layout(self, layout: Any) -> Any:
        """Recursively process a Dash layout tree, replacing InputField instances.

        Args:
            layout: A Dash component tree that may contain InputField placeholders

        Returns:
            The processed layout with InputField instances replaced by actual
            form components
        """
        # If it's an InputField, replace with the actual component
        if isinstance(layout, InputField):
            return self.create_component(layout.field_name)

        # If it's a Dash component with children, recursively process children
        if hasattr(layout, "children"):
            processed_children = self.process_layout(layout.children)
            # Create a new instance with processed children
            layout.children = processed_children
            return layout

        # If it's a list, recursively process each item
        if isinstance(layout, list):
            return [self.process_layout(item) for item in layout]

        # If it's a dict, recursively process each value
        if isinstance(layout, dict):
            return {key: self.process_layout(value) for key, value in layout.items()}

        # Otherwise return as-is (strings, numbers, None, etc.)
        return layout

    def generate_form(self) -> list[Any]:
        """Generate the form layout from an OrderedDict layout.

        This method expects self.layout to be an OrderedDict where keys are
        group names and values are lists of field name lists (for rows/columns).

        Returns:
            List of Dash Card components representing the form
        """
        form_layout: list[Any] = []
        for group_name, row in self.layout.items():
            card_layout = []
            for field_names in row:
                col = [
                    dbc.Col(
                        self.create_component(field_name),
                    )
                    for field_name in field_names
                ]
                card_layout.append(
                    dbc.Row(
                        col,
                        class_name="m-2",
                    )
                )

            form_layout.append(
                dbc.Card(
                    [
                        dbc.CardHeader(group_name, class_name="w-100 text-center fs-4"),
                        dbc.CardBody(card_layout),
                    ],
                    class_name="my-2 d-flex justify-content-center align-items-center",
                )
            )

        return form_layout

    def produce_callback_outputs(self) -> dict[str, Output]:
        """Produce the callback outputs for form validation.

        Returns:
            Dictionary of Dash Output objects keyed by descriptive names.
            Use with the ** operator in callback decorators.
        """
        output_dict: dict[str, Output] = {}
        for field_name in self.fields_website:
            field_type = self.pymodel_class.model_fields[field_name].json_schema_extra[
                "type"
            ]
            id_feedback = self.feedback_id_format.format(field_name=field_name)
            if field_type not in self.fieldtypes_not_to_validate:
                output_dict[f"{field_name}_valid"] = Output(field_name, "valid")
                output_dict[f"{field_name}_invalid"] = Output(field_name, "invalid")
                output_dict[f"{id_feedback}_type"] = Output(id_feedback, "type")
            output_dict[f"{id_feedback}_children"] = Output(id_feedback, "children")

        return output_dict

    def produce_callback_inputs(
        self, use_state: bool = False
    ) -> dict[str, Input | State]:
        """Produce the callback inputs for form handling.

        Args:
            use_state: If True, use State instead of Input (won't trigger callback)

        Returns:
            Dictionary of Dash Input/State objects keyed by field names.
            Use with the ** operator in callback decorators.
        """
        input_dict: dict[str, Input | State] = {}
        callback_context: type[Input] | type[State]
        if use_state:
            callback_context = State
        else:
            callback_context = Input

        for field_name in self.fields_website:
            field_type = self.pymodel_class.model_fields[field_name].json_schema_extra[
                "type"
            ]
            id_field = self.id_format.format(field_name=field_name)
            if field_type == "date-picker":
                id_start_date = self.start_date_id_format.format(field_name=field_name)
                id_end_date = self.end_date_id_format.format(field_name=field_name)
                input_dict[id_start_date] = callback_context(field_name, "start_date")
                input_dict[id_end_date] = callback_context(field_name, "end_date")
            else:
                input_dict[id_field] = callback_context(field_name, "value")

        return input_dict

    def validate_callback(
        self, form_data: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """Validate the form data against the Pydantic model.

        Args:
            form_data: Dictionary of form field values from the callback

        Returns:
            Tuple of (is_valid, output_dict) where output_dict contains
            validation state for each field
        """
        exceptions: dict[str, str] = {}
        try:
            self.set_model(form_data)
        except ValidationError as e:
            for error in e.errors():
                msg = error["msg"].replace("Value error, ", "")
                locs = error["loc"]
                if len(locs) == 0:
                    # This should be a model validator that manually passed the location
                    locs = error["ctx"]["loc_tuple"]

                for loc in locs:
                    exceptions[str(loc)] = msg

        valid = len(exceptions) == 0

        output_dict: dict[str, Any] = {}
        for field_name in self.fields_website:
            field_type = self.pymodel_class.model_fields[field_name].json_schema_extra[
                "type"
            ]
            id_feedback = self.feedback_id_format.format(field_name=field_name)
            if field_name in exceptions:
                msg = exceptions.pop(field_name)
                if field_type not in self.fieldtypes_not_to_validate:
                    output_dict[f"{field_name}_valid"] = False
                    output_dict[f"{field_name}_invalid"] = True
                    output_dict[f"{id_feedback}_type"] = "invalid"
                output_dict[f"{id_feedback}_children"] = msg
            else:
                if field_type not in self.fieldtypes_not_to_validate:
                    output_dict[f"{field_name}_valid"] = True
                    output_dict[f"{field_name}_invalid"] = False
                    output_dict[f"{id_feedback}_type"] = "valid"
                output_dict[f"{id_feedback}_children"] = ""

        if len(exceptions) > 0:
            raise ValueError(f"Unhandled form validation errors: {exceptions}")

        return valid, output_dict

    def set_model(self, form_data: dict[str, Any]) -> None:
        """Set the model from the form data.

        Args:
            form_data: Dictionary of form field values
        """
        model_dict: dict[str, Any] = {}
        for field_name in self.pymodel_class.model_fields:
            field_type = self.pymodel_class.model_fields[field_name].json_schema_extra[
                "type"
            ]
            if field_type == "date-picker":
                id_start_date = self.start_date_id_format.format(field_name=field_name)
                id_end_date = self.end_date_id_format.format(field_name=field_name)
                model_dict[field_name] = [
                    form_data[id_start_date],
                    form_data[id_end_date],
                ]
            else:
                try:
                    model_dict[field_name] = form_data[field_name]
                except KeyError:
                    pass

        # Validate by constructing — raises ValidationError if invalid.
        self.pymodel_class(**model_dict)
