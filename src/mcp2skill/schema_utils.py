"""Utilities for converting JSON Schema to Python argparse code."""

import json
from typing import Any


def snake_to_kebab(name: str) -> str:
    """Convert snake_case to kebab-case.

    Args:
        name: String in snake_case

    Returns:
        String in kebab-case
    """
    return name.replace('_', '-')


def kebab_to_snake(name: str) -> str:
    """Convert kebab-case to snake_case.

    Args:
        name: String in kebab-case

    Returns:
        String in snake_case
    """
    return name.replace('-', '_')


def generate_argparse_from_schema(schema: dict[str, Any]) -> tuple[str, str]:
    """Generate argparse code from JSON Schema.

    Args:
        schema: JSON Schema dictionary (inputSchema from tool)

    Returns:
        Tuple of (argparse_add_argument_code, args_to_dict_code)
    """
    properties = schema.get('properties', {})
    required = schema.get('required', [])

    if not properties:
        # No arguments
        return "    # No arguments required\n    pass", "    arguments = {}"

    argparse_lines = []
    args_dict_lines = ["    # Build arguments dictionary", "    arguments = {}"]

    for prop_name, prop_schema in properties.items():
        cli_name = snake_to_kebab(prop_name)
        prop_type = prop_schema.get('type', 'string')
        prop_desc = prop_schema.get('description', '').replace('"', '\\"')
        is_required = prop_name in required

        # Determine argparse parameters
        if prop_type == 'boolean':
            # Boolean: use store_true
            argparse_lines.append(
                f'    parser.add_argument(\n'
                f'        "--{cli_name}",\n'
                f'        action="store_true",\n'
                f'        help="{prop_desc}"\n'
                f'    )'
            )
            args_dict_lines.append(
                f'    if args.{kebab_to_snake(cli_name)}:\n'
                f'        arguments["{prop_name}"] = True'
            )

        elif prop_type == 'integer':
            # Integer
            argparse_lines.append(
                f'    parser.add_argument(\n'
                f'        "--{cli_name}",\n'
                f'        type=int,\n'
                f'        {"required=True," if is_required else ""}\n'
                f'        help="{prop_desc}"\n'
                f'    )'
            )
            args_dict_lines.append(
                f'    if args.{kebab_to_snake(cli_name)} is not None:\n'
                f'        arguments["{prop_name}"] = args.{kebab_to_snake(cli_name)}'
            )

        elif prop_type == 'number':
            # Float/number
            argparse_lines.append(
                f'    parser.add_argument(\n'
                f'        "--{cli_name}",\n'
                f'        type=float,\n'
                f'        {"required=True," if is_required else ""}\n'
                f'        help="{prop_desc}"\n'
                f'    )'
            )
            args_dict_lines.append(
                f'    if args.{kebab_to_snake(cli_name)} is not None:\n'
                f'        arguments["{prop_name}"] = args.{kebab_to_snake(cli_name)}'
            )

        elif prop_type == 'array':
            # Array: use nargs='+'
            item_type = prop_schema.get('items', {}).get('type', 'string')
            python_type = _json_type_to_python_type(item_type)

            argparse_lines.append(
                f'    parser.add_argument(\n'
                f'        "--{cli_name}",\n'
                f'        nargs="+",\n'
                f'        type={python_type},\n'
                f'        {"required=True," if is_required else ""}\n'
                f'        help="{prop_desc}"\n'
                f'    )'
            )
            args_dict_lines.append(
                f'    if args.{kebab_to_snake(cli_name)} is not None:\n'
                f'        arguments["{prop_name}"] = args.{kebab_to_snake(cli_name)}'
            )

        elif prop_type == 'object':
            # Object: accept as JSON string
            argparse_lines.append(
                f'    parser.add_argument(\n'
                f'        "--{cli_name}",\n'
                f'        type=str,\n'
                f'        {"required=True," if is_required else ""}\n'
                f'        help="{prop_desc} (JSON string)"\n'
                f'    )'
            )
            args_dict_lines.append(
                f'    if args.{kebab_to_snake(cli_name)} is not None:\n'
                f'        import json\n'
                f'        arguments["{prop_name}"] = json.loads(args.{kebab_to_snake(cli_name)})'
            )

        else:
            # String or unknown: treat as string
            # Check for enum
            enum_values = prop_schema.get('enum', [])
            if enum_values:
                choices_str = ', '.join(f'"{v}"' for v in enum_values)
                argparse_lines.append(
                    f'    parser.add_argument(\n'
                    f'        "--{cli_name}",\n'
                    f'        choices=[{choices_str}],\n'
                    f'        {"required=True," if is_required else ""}\n'
                    f'        help="{prop_desc}"\n'
                    f'    )'
                )
            else:
                argparse_lines.append(
                    f'    parser.add_argument(\n'
                    f'        "--{cli_name}",\n'
                    f'        type=str,\n'
                    f'        {"required=True," if is_required else ""}\n'
                    f'        help="{prop_desc}"\n'
                    f'    )'
                )

            args_dict_lines.append(
                f'    if args.{kebab_to_snake(cli_name)} is not None:\n'
                f'        arguments["{prop_name}"] = args.{kebab_to_snake(cli_name)}'
            )

    argparse_code = '\n'.join(argparse_lines)
    args_dict_code = '\n'.join(args_dict_lines)

    return argparse_code, args_dict_code


def _json_type_to_python_type(json_type: str) -> str:
    """Convert JSON type to Python type for argparse.

    Args:
        json_type: JSON Schema type string

    Returns:
        Python type name as string
    """
    type_map = {
        'string': 'str',
        'integer': 'int',
        'number': 'float',
        'boolean': 'bool',
    }
    return type_map.get(json_type, 'str')
