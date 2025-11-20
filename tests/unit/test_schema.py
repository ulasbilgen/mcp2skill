"""Tests for schema module."""

import pytest
import inspect
from mcp2skill.schema import (
    parse_command,
    camel_to_snake,
    snake_to_camel,
    json_schema_to_python_type,
    create_function_with_signature
)


class TestParseCommand:
    """Test parse_command function."""

    def test_parse_string_simple(self):
        """Test parsing simple command string."""
        result = parse_command("python script.py")
        assert result == ["python", "script.py"]

    def test_parse_string_with_flags(self):
        """Test parsing command with flags."""
        result = parse_command("npx -y weather-server")
        assert result == ["npx", "-y", "weather-server"]

    def test_parse_list_returns_same(self):
        """Test parsing list returns the same list."""
        cmd = ["python", "server.py"]
        result = parse_command(cmd)
        assert result == cmd

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = parse_command("")
        assert result == []  # split() on empty string returns []

    def test_parse_single_word(self):
        """Test parsing single word."""
        result = parse_command("node")
        assert result == ["node"]


class TestCamelToSnake:
    """Test camel_to_snake function."""

    def test_simple_camel_case(self):
        """Test simple camelCase conversion."""
        assert camel_to_snake("getWeather") == "get_weather"

    def test_multiple_words(self):
        """Test conversion with multiple words."""
        assert camel_to_snake("fetchDataFromServer") == "fetch_data_from_server"

    def test_pascal_case(self):
        """Test PascalCase conversion."""
        assert camel_to_snake("GetWeather") == "get_weather"

    def test_consecutive_capitals(self):
        """Test conversion with consecutive capitals."""
        assert camel_to_snake("HTTPRequest") == "http_request"
        assert camel_to_snake("URLParser") == "url_parser"

    def test_already_snake_case(self):
        """Test conversion of already snake_case."""
        assert camel_to_snake("already_snake") == "already_snake"

    def test_single_word_lowercase(self):
        """Test conversion of single lowercase word."""
        assert camel_to_snake("simple") == "simple"

    def test_single_word_uppercase(self):
        """Test conversion of single uppercase word."""
        assert camel_to_snake("HTTP") == "http"

    def test_with_numbers(self):
        """Test conversion with numbers."""
        assert camel_to_snake("get2Items") == "get2_items"


class TestSnakeToCamel:
    """Test snake_to_camel function."""

    def test_simple_snake_case(self):
        """Test simple snake_case conversion."""
        assert snake_to_camel("get_weather") == "getWeather"

    def test_multiple_words(self):
        """Test conversion with multiple words."""
        assert snake_to_camel("fetch_data_from_server") == "fetchDataFromServer"

    def test_single_word(self):
        """Test conversion of single word."""
        assert snake_to_camel("simple") == "simple"

    def test_already_camel_case(self):
        """Test conversion of already camelCase (no underscores)."""
        assert snake_to_camel("alreadyCamel") == "alreadyCamel"

    def test_roundtrip(self):
        """Test that conversions are reversible."""
        original = "someVariableName"
        snake = camel_to_snake(original)
        back_to_camel = snake_to_camel(snake)
        assert back_to_camel == original


class TestJsonSchemaToPythonType:
    """Test json_schema_to_python_type function."""

    def test_string_type(self):
        """Test string type mapping."""
        assert json_schema_to_python_type({"type": "string"}) == str

    def test_integer_type(self):
        """Test integer type mapping."""
        assert json_schema_to_python_type({"type": "integer"}) == int

    def test_number_type(self):
        """Test number type mapping."""
        assert json_schema_to_python_type({"type": "number"}) == float

    def test_boolean_type(self):
        """Test boolean type mapping."""
        assert json_schema_to_python_type({"type": "boolean"}) == bool

    def test_array_type(self):
        """Test array type mapping."""
        assert json_schema_to_python_type({"type": "array"}) == list

    def test_object_type(self):
        """Test object type mapping."""
        assert json_schema_to_python_type({"type": "object"}) == dict

    def test_null_type(self):
        """Test null type mapping."""
        assert json_schema_to_python_type({"type": "null"}) == type(None)

    def test_missing_type_defaults_to_object(self):
        """Test missing type defaults to dict (default is 'object' type which maps to dict)."""
        assert json_schema_to_python_type({}) == dict  # Default type is 'object' which maps to dict

    def test_unknown_type_defaults_to_object(self):
        """Test unknown type defaults to object."""
        assert json_schema_to_python_type({"type": "unknown"}) == object


class TestCreateFunctionWithSignature:
    """Test create_function_with_signature function."""

    def test_creates_callable(self):
        """Test that function is created."""
        def impl(**kwargs):
            return kwargs

        schema = {"type": "object", "properties": {}}
        func = create_function_with_signature("test", "Test", schema, impl)

        assert callable(func)
        assert func.__name__ == "test"
        assert func.__doc__ == "Test"

    def test_required_parameters(self):
        """Test function with required parameters."""
        def impl(**kwargs):
            return kwargs

        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"}
            }
        }
        func = create_function_with_signature("test", "Test", schema, impl)

        sig = inspect.signature(func)
        assert "name" in sig.parameters
        assert sig.parameters["name"].annotation == str
        assert sig.parameters["name"].default == inspect.Parameter.empty

    def test_optional_parameters_with_defaults(self):
        """Test function with optional parameters with defaults."""
        def impl(**kwargs):
            return kwargs

        schema = {
            "type": "object",
            "properties": {
                "timeout": {"type": "integer", "default": 5000}
            }
        }
        func = create_function_with_signature("test", "Test", schema, impl)

        sig = inspect.signature(func)
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].annotation == int
        assert sig.parameters["timeout"].default == 5000

    def test_optional_parameters_without_defaults(self):
        """Test function with optional parameters without defaults."""
        def impl(**kwargs):
            return kwargs

        schema = {
            "type": "object",
            "properties": {
                "value": {"type": "string"}
            }
        }
        func = create_function_with_signature("test", "Test", schema, impl)

        sig = inspect.signature(func)
        assert "value" in sig.parameters
        assert sig.parameters["value"].default is None

    def test_function_execution(self):
        """Test that created function can be called and executes correctly."""
        def impl(**kwargs):
            return f"Called with {kwargs}"

        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "count": {"type": "integer", "default": 1}
            }
        }
        func = create_function_with_signature("test", "Test", schema, impl)

        result = func(name="test")
        assert "test" in result
        assert "count" in result

    def test_parameter_types(self):
        """Test that various parameter types are handled correctly."""
        def impl(**kwargs):
            return kwargs

        schema = {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "count": {"type": "integer"},
                "ratio": {"type": "number"},
                "enabled": {"type": "boolean"},
                "items": {"type": "array"},
                "config": {"type": "object"}
            }
        }
        func = create_function_with_signature("test", "Test", schema, impl)

        sig = inspect.signature(func)
        assert sig.parameters["text"].annotation == str
        assert sig.parameters["count"].annotation == int
        assert sig.parameters["ratio"].annotation == float
        assert sig.parameters["enabled"].annotation == bool
        assert sig.parameters["items"].annotation == list
        assert sig.parameters["config"].annotation == dict

    def test_empty_schema(self):
        """Test function creation with empty schema."""
        def impl(**kwargs):
            return "called"

        schema = {"type": "object"}
        func = create_function_with_signature("test", "Test", schema, impl)

        sig = inspect.signature(func)
        assert len(sig.parameters) == 0
        assert func() == "called"
