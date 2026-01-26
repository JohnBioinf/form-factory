"""Tests for InputField placeholder class."""

from dash_form_factory import InputField


class TestInputField:
    """Tests for InputField class."""

    def test_init_with_empty_string(self):
        """InputField accepts empty string as field name."""
        field = InputField("")
        assert field.field_name == ""

    def test_field_name_attribute(self):
        """InputField.field_name is accessible."""
        field = InputField("test_field")
        assert field.field_name == "test_field"
