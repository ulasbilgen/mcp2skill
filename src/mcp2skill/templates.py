"""Templates for generating SKILL.md and Python scripts."""

from typing import Any
from mcp2skill.schema_utils import generate_argparse_from_schema, snake_to_kebab


def create_skill_md(
    server_name: str,
    server_info: dict[str, Any],
    tools: list[dict[str, Any]],
    mcp2rest_url: str
) -> str:
    """Generate SKILL.md content for a server.

    Args:
        server_name: Name of the MCP server
        server_info: Server information from mcp2rest
        tools: List of tool schemas
        mcp2rest_url: Base URL of mcp2rest service

    Returns:
        SKILL.md content as string
    """
    # Create description from server info
    tool_count = len(tools)
    package = server_info.get('package', server_info.get('url', 'N/A'))

    # Categorize tools if possible (basic heuristic)
    categories = _categorize_tools(tools)

    # Generate tool listing
    tool_list = _generate_tool_list(tools, categories)

    # Generate example workflows
    workflows = _generate_example_workflows(server_name, tools)

    return f"""---
name: mcp-{server_name}
description: {_generate_description(server_name, server_info, tool_count)}
---

# {server_name.replace('-', ' ').title()} MCP Server

{_generate_intro(server_name, server_info)}

## Prerequisites
- mcp2rest running on {mcp2rest_url}
- {server_name} server loaded in mcp2rest
- Package: `{package}`

## Quick Start

```bash
# Navigate to the skill scripts directory
cd scripts/

# Example: List available options
python {tools[0]['name']}.py --help
```

## Available Tools

{tool_list}

## State Persistence

This server maintains state between calls (managed by mcp2rest):
- Sequential commands interact with the same server instance
- State persists until server restart
- Multiple scripts can access shared state

{workflows}

## Troubleshooting

If you get connection errors:
1. Check mcp2rest is running: `curl {mcp2rest_url}/health`
2. Verify server is loaded: `curl {mcp2rest_url}/servers`
3. Check server status in the list

For tool-specific errors, use `--help` flag on any script.
"""


def _generate_description(server_name: str, server_info: dict[str, Any], tool_count: int) -> str:
    """Generate concise skill description."""
    # Extract key info
    transport = server_info.get('transport', 'unknown')

    # Common patterns
    if 'chrome' in server_name.lower() or 'browser' in server_name.lower():
        return f"Browser automation and DevTools control ({tool_count} tools)"
    elif 'figma' in server_name.lower():
        return f"Figma design tool integration ({tool_count} tools)"
    elif 'filesystem' in server_name.lower() or 'file' in server_name.lower():
        return f"File system operations ({tool_count} tools)"
    elif 'weather' in server_name.lower():
        return f"Weather data and forecasts ({tool_count} tools)"
    else:
        return f"MCP server with {tool_count} tools"


def _generate_intro(server_name: str, server_info: dict[str, Any]) -> str:
    """Generate introduction paragraph."""
    if 'chrome' in server_name.lower():
        return "Control Chrome browser programmatically via the Chrome DevTools Protocol. Navigate pages, interact with elements, take screenshots, and more."
    elif 'figma' in server_name.lower():
        return "Interact with Figma designs, extract design tokens, and automate design workflows."
    else:
        return f"Access {server_name} functionality via REST API."


def _categorize_tools(tools: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Categorize tools by common patterns."""
    categories = {
        'Page Management': [],
        'Element Interaction': [],
        'Inspection': [],
        'Network': [],
        'Performance': [],
        'Other': []
    }

    for tool in tools:
        name = tool['name'].lower()

        if any(kw in name for kw in ['page', 'navigate', 'new_', 'list_pages', 'select_page', 'close_page']):
            categories['Page Management'].append(tool)
        elif any(kw in name for kw in ['click', 'fill', 'hover', 'drag', 'press', 'upload']):
            categories['Element Interaction'].append(tool)
        elif any(kw in name for kw in ['snapshot', 'screenshot', 'console', 'get_']):
            categories['Inspection'].append(tool)
        elif any(kw in name for kw in ['network', 'request']):
            categories['Network'].append(tool)
        elif any(kw in name for kw in ['performance', 'trace', 'insight']):
            categories['Performance'].append(tool)
        else:
            categories['Other'].append(tool)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def _generate_tool_list(tools: list[dict[str, Any]], categories: dict[str, list[dict[str, Any]]]) -> str:
    """Generate formatted tool listing."""
    sections = []

    for category, cat_tools in categories.items():
        lines = [f"### {category}\n"]
        for tool in cat_tools:
            # Get basic arg info from schema
            schema = tool.get('inputSchema', {})
            required = schema.get('required', [])
            properties = schema.get('properties', {})

            # Build arg string
            args = []
            for prop_name in required:
                args.append(f"--{snake_to_kebab(prop_name)} {prop_name.upper()}")

            # Add optional args indicator
            optional_count = len(properties) - len(required)
            if optional_count > 0:
                args.append(f"[{optional_count} optional]")

            arg_str = ' '.join(args) if args else ''

            desc = tool.get('description', 'No description')
            lines.append(f"- `{tool['name']}.py {arg_str}` - {desc}")

        sections.append('\n'.join(lines))

    return '\n\n'.join(sections)


def _generate_example_workflows(server_name: str, tools: list[dict[str, Any]]) -> str:
    """Generate example workflow section."""
    tool_names = [t['name'] for t in tools]

    # Chrome DevTools workflows
    if 'new_page' in tool_names and 'click' in tool_names:
        return """## Example Workflows

### Navigate and Interact

```bash
# 1. Open a page
python new_page.py --url https://example.com

# 2. Take snapshot to see element UIDs
python take_snapshot.py

# 3. Click an element (use UID from snapshot)
python click.py --uid button_123
```

### Fill and Submit Form

```bash
# 1. Navigate to form
python new_page.py --url https://example.com/form

# 2. Get element UIDs
python take_snapshot.py

# 3. Fill form fields
python fill.py --uid email_field --value user@example.com
python fill.py --uid password_field --value secret

# 4. Submit
python click.py --uid submit_button
```

### Take Screenshot

```bash
python new_page.py --url https://example.com
python take_screenshot.py --format png
```"""

    return """## Example Usage

```bash
# List available tools
ls scripts/

# Get help for specific tool
python scripts/tool_name.py --help

# Run a tool
python scripts/tool_name.py --arg value
```"""


def create_mcp_client_script(mcp2rest_url: str) -> str:
    """Generate shared mcp_client.py utility script.

    Args:
        mcp2rest_url: Base URL of mcp2rest service

    Returns:
        Python code for mcp_client.py
    """
    return f'''"""Shared MCP REST client for tool scripts."""

import json
import os
import requests
from typing import Any

# MCP2REST endpoint (configurable via environment variable)
MCP_REST_URL = os.getenv("MCP_REST_URL", "{mcp2rest_url}")


def call_tool(server: str, tool: str, arguments: dict[str, Any]) -> str:
    """Call an MCP tool via mcp2rest REST API.

    Args:
        server: Server name (e.g., "chrome-devtools")
        tool: Tool name (e.g., "click")
        arguments: Tool arguments as dictionary

    Returns:
        Tool result as formatted string

    Raises:
        SystemExit: If request fails
    """
    url = f"{{MCP_REST_URL}}/call"
    payload = {{
        "server": server,
        "tool": tool,
        "arguments": arguments
    }}

    try:
        response = requests.post(
            url,
            json=payload,
            headers={{"Content-Type": "application/json"}},
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        if data.get("success"):
            # Extract and format result
            result = data.get("result", {{}})
            content = result.get("content", [])

            # Format output nicely
            output_parts = []
            for item in content:
                if item.get("type") == "text":
                    output_parts.append(item.get("text", ""))
                elif item.get("type") == "image":
                    # For images, just note their presence
                    output_parts.append(f"[Image data: {{len(item.get('data', ''))}} bytes]")
                elif item.get("type") == "resource":
                    output_parts.append(json.dumps(item.get("resource", {{}}), indent=2))

            return "\\n".join(output_parts) if output_parts else json.dumps(result, indent=2)
        else:
            error = data.get("error", {{}})
            error_msg = error.get("message", "Unknown error")
            error_code = error.get("code", "UNKNOWN")
            print(f"Error [{{error_code}}]: {{error_msg}}", file=sys.stderr)
            sys.exit(1)

    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to mcp2rest at {{MCP_REST_URL}}", file=sys.stderr)
        print("Make sure mcp2rest is running.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after 30 seconds", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {{e.response.status_code}} - {{e.response.text}}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {{type(e).__name__}}: {{e}}", file=sys.stderr)
        sys.exit(1)


import sys  # noqa: E402
'''


def create_tool_script(server_name: str, tool: dict[str, Any]) -> str:
    """Generate Python script for a tool.

    Args:
        server_name: Name of the MCP server
        tool: Tool schema dictionary

    Returns:
        Python code for the tool script
    """
    tool_name = tool['name']
    description = tool.get('description', f"Execute {tool_name} tool")
    schema = tool.get('inputSchema', {})

    # Generate argparse code
    argparse_code, args_to_dict_code = generate_argparse_from_schema(schema)

    return f'''#!/usr/bin/env python3
"""{description}"""

import argparse
import sys
from mcp_client import call_tool


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="{description}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

{argparse_code}

    args = parser.parse_args()

{args_to_dict_code}

    # Call the tool
    result = call_tool(
        server="{server_name}",
        tool="{tool_name}",
        arguments=arguments
    )

    # Print result
    print(result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\nInterrupted", file=sys.stderr)
        sys.exit(130)
'''
