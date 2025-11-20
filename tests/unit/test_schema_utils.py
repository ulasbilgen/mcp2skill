"""Tests for schema_utils module."""

import pytest
from mcp2skill.schema_utils import (
    snake_to_kebab,
    kebab_to_snake,
    generate_argparse_from_schema,
    _json_type_to_python_type
)


class TestNamingConversions:
    """Test naming convention conversion functions."""

    def test_snake_to_kebab_basic(self):
        """Test basic snake_case to kebab-case conversion."""
        assert snake_to_kebab("hello_world") == "hello-world"

    def test_snake_to_kebab_multiple_underscores(self):
        """Test conversion with multiple underscores."""
        assert snake_to_kebab("this_is_a_test") == "this-is-a-test"

    def test_snake_to_kebab_no_underscores(self):
        """Test conversion with no underscores."""
        assert snake_to_kebab("hello") == "hello"

    def test_snake_to_kebab_empty(self):
        """Test conversion with empty string."""
        assert snake_to_kebab("") == ""

    def test_kebab_to_snake_basic(self):
        """Test basic kebab-case to snake_case conversion."""
        assert kebab_to_snake("hello-world") == "hello_world"

    def test_kebab_to_snake_multiple_hyphens(self):
        """Test conversion with multiple hyphens."""
        assert kebab_to_snake("this-is-a-test") == "this_is_a_test"

    def test_kebab_to_snake_no_hyphens(self):
        """Test conversion with no hyphens."""
        assert kebab_to_snake("hello") == "hello"

    def test_kebab_to_snake_empty(self):
        """Test conversion with empty string."""
        assert kebab_to_snake("") == ""

    def test_roundtrip_conversion(self):
        """Test that conversions are reversible."""
        original = "some_variable_name"
        kebab = snake_to_kebab(original)
        back_to_snake = kebab_to_snake(kebab)
        assert back_to_snake == original


class TestJsonTypeToPythonType:
    """Test JSON Schema type to Python type conversion."""

    def test_string_type(self):
        """Test string type mapping."""
        assert _json_type_to_python_type("string") == "str"

    def test_integer_type(self):
        """Test integer type mapping."""
        assert _json_type_to_python_type("integer") == "int"

    def test_number_type(self):
        """Test number type mapping."""
        assert _json_type_to_python_type("number") == "float"

    def test_boolean_type(self):
        """Test boolean type mapping."""
        assert _json_type_to_python_type("boolean") == "bool"

    def test_unknown_type(self):
        """Test unknown type defaults to str."""
        assert _json_type_to_python_type("unknown") == "str"

    def test_empty_type(self):
        """Test empty type defaults to str."""
        assert _json_type_to_python_type("") == "str"


class TestGenerateArgparseFromSchema:
    """Test argparse code generation from JSON Schema."""

    def test_empty_schema(self):
        """Test generation with empty schema."""
        schema = {"properties": {}}
        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert "# No arguments required" in argparse_code
        assert "arguments = {}" in args_dict_code

    def test_no_properties(self):
        """Test generation with no properties key."""
        schema = {}
        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert "# No arguments required" in argparse_code
        assert "arguments = {}" in args_dict_code

    def test_simple_string_required(self):
        """Test required string parameter."""
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "User name"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--name' in argparse_code
        assert 'required=True' in argparse_code
        assert 'type=str' in argparse_code
        assert 'User name' in argparse_code
        assert 'arguments["name"]' in args_dict_code

    def test_simple_string_optional(self):
        """Test optional string parameter."""
        schema = {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Optional description"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--description' in argparse_code
        assert 'required=True' not in argparse_code
        assert 'type=str' in argparse_code
        assert 'Optional description' in argparse_code

    def test_integer_parameter(self):
        """Test integer parameter."""
        schema = {
            "type": "object",
            "required": ["count"],
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Number of items"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--count' in argparse_code
        assert 'type=int' in argparse_code
        assert 'required=True' in argparse_code
        assert 'Number of items' in argparse_code

    def test_number_parameter(self):
        """Test number (float) parameter."""
        schema = {
            "type": "object",
            "properties": {
                "ratio": {
                    "type": "number",
                    "description": "Ratio value"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--ratio' in argparse_code
        assert 'type=float' in argparse_code
        assert 'Ratio value' in argparse_code

    def test_boolean_parameter(self):
        """Test boolean parameter."""
        schema = {
            "type": "object",
            "properties": {
                "verbose": {
                    "type": "boolean",
                    "description": "Enable verbose output"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--verbose' in argparse_code
        assert 'action="store_true"' in argparse_code
        assert 'Enable verbose output' in argparse_code
        assert 'if args.verbose:' in args_dict_code
        assert 'arguments["verbose"] = True' in args_dict_code

    def test_array_parameter_string_items(self):
        """Test array parameter with string items."""
        schema = {
            "type": "object",
            "required": ["tags"],
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tags"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--tags' in argparse_code
        assert 'nargs="+"' in argparse_code
        assert 'type=str' in argparse_code
        assert 'required=True' in argparse_code
        assert 'List of tags' in argparse_code

    def test_array_parameter_integer_items(self):
        """Test array parameter with integer items."""
        schema = {
            "type": "object",
            "properties": {
                "numbers": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of numbers"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--numbers' in argparse_code
        assert 'nargs="+"' in argparse_code
        assert 'type=int' in argparse_code

    def test_object_parameter(self):
        """Test object parameter (JSON string)."""
        schema = {
            "type": "object",
            "properties": {
                "config": {
                    "type": "object",
                    "description": "Configuration object"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--config' in argparse_code
        assert 'type=str' in argparse_code
        assert 'Configuration object (JSON string)' in argparse_code
        assert 'json.loads' in args_dict_code

    def test_enum_parameter(self):
        """Test enum parameter."""
        schema = {
            "type": "object",
            "required": ["mode"],
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["fast", "normal", "slow"],
                    "description": "Operation mode"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--mode' in argparse_code
        assert 'choices=[' in argparse_code
        assert '"fast"' in argparse_code
        assert '"normal"' in argparse_code
        assert '"slow"' in argparse_code
        assert 'required=True' in argparse_code
        assert 'Operation mode' in argparse_code

    def test_snake_case_to_kebab_case_conversion(self):
        """Test that snake_case properties become kebab-case CLI args."""
        schema = {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--max-results' in argparse_code
        assert 'args.max_results' in args_dict_code
        assert 'arguments["max_results"]' in args_dict_code

    def test_multiple_properties(self):
        """Test schema with multiple properties."""
        schema = {
            "type": "object",
            "required": ["name", "count"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name"
                },
                "count": {
                    "type": "integer",
                    "description": "Count"
                },
                "enabled": {
                    "type": "boolean",
                    "description": "Enabled"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        # Check all parameters are present
        assert '--name' in argparse_code
        assert '--count' in argparse_code
        assert '--enabled' in argparse_code

        # Check required flags
        assert argparse_code.count('required=True') == 2  # name and count

    def test_description_with_quotes(self):
        """Test that quotes in descriptions are escaped."""
        schema = {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": 'Use "quotes" here'
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        # Should escape quotes
        assert '\\"quotes\\"' in argparse_code or "\\\"quotes\\\"" in argparse_code

    def test_missing_description(self):
        """Test parameter without description."""
        schema = {
            "type": "object",
            "properties": {
                "value": {
                    "type": "string"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        assert '--value' in argparse_code
        # Should have empty help string
        assert 'help=""' in argparse_code

    def test_complex_schema(self):
        """Test complex schema with all types."""
        schema = {
            "type": "object",
            "required": ["query", "sources"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sources"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results"
                },
                "threshold": {
                    "type": "number",
                    "description": "Threshold"
                },
                "includeMetadata": {
                    "type": "boolean",
                    "description": "Include metadata"
                },
                "sortBy": {
                    "type": "string",
                    "enum": ["relevance", "date"],
                    "description": "Sort order"
                },
                "filters": {
                    "type": "object",
                    "description": "Filters"
                }
            }
        }

        argparse_code, args_dict_code = generate_argparse_from_schema(schema)

        # Verify all parameters are generated
        # Note: snake_to_kebab only converts underscores, not camelCase
        assert '--query' in argparse_code
        assert '--sources' in argparse_code
        assert '--limit' in argparse_code
        assert '--threshold' in argparse_code
        assert '--includeMetadata' in argparse_code  # camelCase preserved from property name
        assert '--sortBy' in argparse_code  # camelCase preserved from property name
        assert '--filters' in argparse_code

        # Verify correct types
        assert argparse_code.count('type=str') >= 1
        assert 'type=int' in argparse_code
        assert 'type=float' in argparse_code
        assert 'action="store_true"' in argparse_code
        assert 'nargs="+"' in argparse_code
        assert 'choices=[' in argparse_code
        assert 'json.loads' in args_dict_code
