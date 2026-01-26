# dash-form-factory

Generate Dash Bootstrap forms from Pydantic v2 models using a factory pattern.

## Installation

```bash
pip install dash-form-factory
```

Or with uv:

```bash
uv add dash-form-factory
```

## Quick Start

```python
from typing import Annotated
from pydantic import BaseModel, Field
import dash_bootstrap_components as dbc
from dash import Dash, html, callback, Input, Output
from dash_form_factory import FormFactory, InputField

# 1. Define your Pydantic model
class ContactForm(BaseModel):
    name: Annotated[str, Field(
        "",
        title="Name",
        description="Your full name",
        json_schema_extra={"type": "text"}
    )]
    email: Annotated[str, Field(
        "",
        title="Email",
        description="Your email address",
        json_schema_extra={"type": "email"}
    )]

# 2. Create layout with InputField placeholders
layout = dbc.Card([
    dbc.CardBody([
        InputField("name"),
        InputField("email"),
        dbc.Button("Submit", id="submit")
    ])
])

# 3. Process layout with FormFactory
factory = FormFactory(ContactForm, layout)
form = factory.process_layout(factory.layout)

# 4. Create app and register callbacks
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([form, html.Div(id="output")])

@callback(
    output=factory.produce_callback_outputs(),
    inputs=factory.produce_callback_inputs(),
)
def validate(**inputs):
    valid, outputs = factory.validate_callback(inputs)
    return outputs
```

## Pydantic Model Requirements

Each field must include `json_schema_extra` with a `type` key:

```python
from typing import Annotated
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    field_name: Annotated[type, Field(
        default_value,
        title="Display Title",
        description="Help text shown below the field",
        json_schema_extra={"type": "field_type"}
    )]
```

## Supported Field Types

| Type                 | Component             | Python Type          | Description                         |
| -------------------- | --------------------- | -------------------- | ----------------------------------- |
| `text`               | `dbc.Input`           | `str`                | Standard text input                 |
| `email`              | `dbc.Input`           | `str`                | Email input with validation styling |
| `integer`            | `dbc.Input`           | `int`                | Number input with step=1            |
| `float`              | `dbc.Input`           | `float`              | Number input with step="any"        |
| `checkbox`           | `dbc.Checkbox`        | `bool`               | Single checkbox                     |
| `date-picker`        | `dcc.DatePickerRange` | `List[str]`          | Date range selector                 |
| `dropdown-checklist` | `dbc.DropdownMenu`    | `List[Literal[...]]` | Multi-select dropdown               |

### Date Picker Example

```python
from typing import List

date_range: Annotated[List[str], Field(
    ["2024-01-01", "2024-12-31"],
    title="Date Range",
    json_schema_extra={"type": "date-picker"}
)]
```

### Dropdown Checklist Example

```python
from typing import List, Literal

options: Annotated[List[Literal["opt_a", "opt_b", "opt_c"]], Field(
    [],
    title="Options",
    json_schema_extra={"type": "dropdown-checklist"}
)]
```

## FormFactory API

### Constructor

```python
FormFactory(pymodel, layout, active=True)
```

- `pymodel`: Pydantic model class or instance
- `layout`: Dash component tree with InputField placeholders
- `active`: If False, form fields are disabled

### Methods

| Method                                     | Description                                           |
| ------------------------------------------ | ----------------------------------------------------- |
| `process_layout(layout)`                   | Replace InputField placeholders with form components  |
| `produce_callback_outputs()`               | Generate Output dict for validation callbacks         |
| `produce_callback_inputs(use_state=False)` | Generate Input/State dict for callbacks               |
| `validate_callback(form_data)`             | Validate form data, returns `(is_valid, output_dict)` |

## Using with Model Instances

Pass a model instance to pre-fill form values:

```python
instance = ContactForm(name="John", email="john@example.com")
factory = FormFactory(instance, layout)
```

## Disabled Forms

Set `active=False` for read-only forms:

```python
factory = FormFactory(ContactForm, layout, active=False)
```

## Examples

See the `examples/` directory:

- `basic_form.py` - Simple contact form
- `advanced_form.py` - All field types demo

Run examples with:

```bash
uv run python examples/basic_form.py
```

## Comparison with dash-pydantic-form

This package differs has a signifikatn overlap to [dash-pydantic-form](https://github.com/RenaudLN/dash-pydantic-form). Yet differs on some core features:

| Feature            | dash-form-factory                    | dash-pydantic-form        |
| ------------------ | ------------------------------------ | ------------------------- |
| **UI Framework**   | Dash Bootstrap Components            | Dash Mantine Components   |
| **Form Rendering** | Placeholder-based (subset of fields) | Auto-renders entire model |
| **Layout Control** | Full control - embed fields anywhere | 4-column responsive grid  |

Further it is to mention that dash-pydantic-form is much more feautre rich and mature.

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/dash-form-factory
cd dash-form-factory

# Install with dev dependencies
uv sync --all-groups

# Run tests
uv run pytest

# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/
```

## License

MIT
