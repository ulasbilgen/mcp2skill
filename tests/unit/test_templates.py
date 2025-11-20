"""Tests for templates module."""

import pytest
import ast
from mcp2skill.templates import (
    create_skill_md,
    create_mcp_client_script,
    create_tool_script,
    _generate_description,
    _generate_intro,
    _categorize_tools,
    _generate_tool_list
)


class TestGenerateDescription:
    """Test _generate_description function."""

    def test_chrome_server(self):
        """Test description for chrome server."""
        desc = _generate_description("chrome-devtools", {"transport": "stdio"}, 15)
        assert "Browser automation" in desc
        assert "15 tools" in desc

    def test_figma_server(self):
        """Test description for figma server."""
        desc = _generate_description("figma-api", {"transport": "http"}, 8)
        assert "Figma design tool" in desc
        assert "8 tools" in desc

    def test_filesystem_server(self):
        """Test description for filesystem server."""
        desc = _generate_description("filesystem", {"transport": "stdio"}, 10)
        assert "File system operations" in desc
        assert "10 tools" in desc

    def test_weather_server(self):
        """Test description for weather server."""
        desc = _generate_description("weather-api", {"transport": "http"}, 5)
        assert "Weather data" in desc
        assert "5 tools" in desc

    def test_generic_server(self):
        """Test description for generic server."""
        desc = _generate_description("custom-server", {"transport": "stdio"}, 12)
        assert "MCP server with 12 tools" in desc

    def test_browser_keyword(self):
        """Test description with 'browser' keyword."""
        desc = _generate_description("browser-controller", {}, 7)
        assert "Browser automation" in desc


class TestGenerateIntro:
    """Test _generate_intro function."""

    def test_chrome_intro(self):
        """Test intro for chrome server."""
        intro = _generate_intro("chrome-devtools", {})
        assert "Chrome browser" in intro
        assert "DevTools Protocol" in intro

    def test_figma_intro(self):
        """Test intro for figma server."""
        intro = _generate_intro("figma-api", {})
        assert "Figma designs" in intro
        assert "design workflows" in intro

    def test_generic_intro(self):
        """Test intro for generic server."""
        intro = _generate_intro("custom-api", {})
        assert "custom-api" in intro
        assert "REST API" in intro


class TestCategorizeTools:
    """Test _categorize_tools function."""

    def test_page_management_tools(self):
        """Test categorization of page management tools."""
        tools = [
            {"name": "navigate"},
            {"name": "new_page"},
            {"name": "close_page"}
        ]
        categories = _categorize_tools(tools)
        assert "Page Management" in categories
        assert len(categories["Page Management"]) == 3

    def test_element_interaction_tools(self):
        """Test categorization of element interaction tools."""
        tools = [
            {"name": "click"},
            {"name": "fill"},
            {"name": "hover"}
        ]
        categories = _categorize_tools(tools)
        assert "Element Interaction" in categories
        assert len(categories["Element Interaction"]) == 3

    def test_inspection_tools(self):
        """Test categorization of inspection tools."""
        tools = [
            {"name": "snapshot"},
            {"name": "screenshot"},
            {"name": "get_status"}
        ]
        categories = _categorize_tools(tools)
        assert "Inspection" in categories
        assert len(categories["Inspection"]) == 3

    def test_network_tools(self):
        """Test categorization of network tools."""
        tools = [
            {"name": "network_info"},
            {"name": "request_log"}
        ]
        categories = _categorize_tools(tools)
        assert "Network" in categories
        assert len(categories["Network"]) == 2

    def test_performance_tools(self):
        """Test categorization of performance tools."""
        tools = [
            {"name": "performance_metrics"},
            {"name": "trace_events"}
        ]
        categories = _categorize_tools(tools)
        assert "Performance" in categories
        assert len(categories["Performance"]) == 2

    def test_other_category(self):
        """Test uncategorized tools go to 'Other'."""
        tools = [
            {"name": "custom_tool"},
            {"name": "special_function"}
        ]
        categories = _categorize_tools(tools)
        assert "Other" in categories
        assert len(categories["Other"]) == 2

    def test_mixed_categories(self):
        """Test tools are sorted into multiple categories."""
        tools = [
            {"name": "navigate"},
            {"name": "click"},
            {"name": "snapshot"},
            {"name": "custom"}
        ]
        categories = _categorize_tools(tools)
        assert len(categories) == 4
        assert "Page Management" in categories
        assert "Element Interaction" in categories
        assert "Inspection" in categories
        assert "Other" in categories

    def test_empty_categories_removed(self):
        """Test that empty categories are removed."""
        tools = [
            {"name": "click"}
        ]
        categories = _categorize_tools(tools)
        assert "Element Interaction" in categories
        assert "Network" not in categories
        assert "Performance" not in categories


class TestGenerateToolList:
    """Test _generate_tool_list function."""

    def test_simple_tool_list(self):
        """Test tool list generation with simple tools."""
        tools = [
            {
                "name": "click",
                "description": "Click an element",
                "inputSchema": {
                    "required": ["selector"],
                    "properties": {
                        "selector": {"type": "string"}
                    }
                }
            }
        ]
        categories = _categorize_tools(tools)
        tool_list = _generate_tool_list(tools, categories)

        assert "### Element Interaction" in tool_list
        assert "click.py" in tool_list
        assert "--selector SELECTOR" in tool_list
        assert "Click an element" in tool_list

    def test_tool_with_optional_params(self):
        """Test tool list shows optional parameter count."""
        tools = [
            {
                "name": "search",
                "description": "Search for items",
                "inputSchema": {
                    "required": ["query"],
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer"},
                        "sort": {"type": "string"}
                    }
                }
            }
        ]
        categories = {"Other": tools}
        tool_list = _generate_tool_list(tools, categories)

        assert "search.py" in tool_list
        assert "--query QUERY" in tool_list
        assert "[2 optional]" in tool_list

    def test_tool_without_required_params(self):
        """Test tool list for tool with no required params."""
        tools = [
            {
                "name": "status",
                "description": "Get status",
                "inputSchema": {
                    "properties": {}
                }
            }
        ]
        categories = {"Other": tools}
        tool_list = _generate_tool_list(tools, categories)

        assert "status.py" in tool_list
        assert "Get status" in tool_list

    def test_multiple_categories(self):
        """Test tool list with multiple categories."""
        tools = [
            {"name": "click", "description": "Click", "inputSchema": {"properties": {}}},
            {"name": "navigate", "description": "Navigate", "inputSchema": {"properties": {}}}
        ]
        categories = _categorize_tools(tools)
        tool_list = _generate_tool_list(tools, categories)

        assert "### Element Interaction" in tool_list
        assert "### Page Management" in tool_list
        assert "click.py" in tool_list
        assert "navigate.py" in tool_list


class TestCreateMcpClientScript:
    """Test create_mcp_client_script function."""

    def test_creates_valid_python(self):
        """Test that generated client script is valid Python."""
        script = create_mcp_client_script("http://localhost:3000")

        # Should be parseable as Python
        try:
            ast.parse(script)
        except SyntaxError as e:
            pytest.fail(f"Generated script has invalid syntax: {e}")

    def test_includes_mcp2rest_url(self):
        """Test that script includes mcp2rest URL."""
        url = "http://custom-host:8080"
        script = create_mcp_client_script(url)
        assert url in script

    def test_includes_call_tool_function(self):
        """Test that script includes call_tool function."""
        script = create_mcp_client_script("http://localhost:3000")
        assert "def call_tool" in script

    def test_includes_imports(self):
        """Test that script includes necessary imports."""
        script = create_mcp_client_script("http://localhost:3000")
        assert "import json" in script
        assert "import os" in script
        assert "import sys" in script
        assert "import requests" in script

    def test_includes_error_handling(self):
        """Test that script includes error handling."""
        script = create_mcp_client_script("http://localhost:3000")
        assert "ConnectionError" in script
        assert "Timeout" in script
        assert "HTTPError" in script

    def test_sys_import_at_top(self):
        """Test that sys import is at the top with other imports."""
        script = create_mcp_client_script("http://localhost:3000")
        lines = script.split('\n')

        # Find import section (after docstring)
        in_imports = False
        sys_import_line = None
        last_import_line = None

        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                in_imports = True
                last_import_line = i
                if 'sys' in line:
                    sys_import_line = i

        # sys import should be in the imports section
        assert sys_import_line is not None, "sys import not found"
        assert sys_import_line <= last_import_line + 5, "sys import not near other imports"


class TestCreateToolScript:
    """Test create_tool_script function."""

    def test_creates_valid_python(self, mock_simple_tool):
        """Test that generated tool script is valid Python."""
        script = create_tool_script("chrome-devtools", mock_simple_tool)

        try:
            ast.parse(script)
        except SyntaxError as e:
            pytest.fail(f"Generated script has invalid syntax: {e}")

    def test_includes_shebang(self, mock_simple_tool):
        """Test that script starts with shebang."""
        script = create_tool_script("chrome-devtools", mock_simple_tool)
        assert script.startswith("#!/usr/bin/env python3")

    def test_includes_tool_description(self, mock_simple_tool):
        """Test that script includes tool description."""
        script = create_tool_script("chrome-devtools", mock_simple_tool)
        assert mock_simple_tool["description"] in script

    def test_includes_argparse(self, mock_simple_tool):
        """Test that script includes argparse setup."""
        script = create_tool_script("chrome-devtools", mock_simple_tool)
        assert "import argparse" in script
        assert "ArgumentParser" in script

    def test_includes_mcp_client_import(self, mock_simple_tool):
        """Test that script imports mcp_client."""
        script = create_tool_script("chrome-devtools", mock_simple_tool)
        assert "from mcp_client import call_tool" in script

    def test_includes_server_name(self, mock_simple_tool):
        """Test that script includes server name."""
        script = create_tool_script("chrome-devtools", mock_simple_tool)
        assert "chrome-devtools" in script

    def test_includes_tool_name(self, mock_simple_tool):
        """Test that script includes tool name."""
        script = create_tool_script("chrome-devtools", mock_simple_tool)
        assert mock_simple_tool["name"] in script

    def test_complex_tool_parameters(self, mock_complex_tool):
        """Test script generation with complex parameters."""
        script = create_tool_script("test-server", mock_complex_tool)

        # Should include all parameter types
        # Note: CLI args preserve the original property names (camelCase is kept)
        assert "--query" in script
        assert "--sources" in script
        assert "--limit" in script
        assert "--includeMetadata" in script  # camelCase preserved
        assert "--sortBy" in script  # camelCase preserved

    def test_tool_with_no_parameters(self, mock_empty_tool):
        """Test script generation for tool with no parameters."""
        script = create_tool_script("test-server", mock_empty_tool)

        # Should still be valid Python
        try:
            ast.parse(script)
        except SyntaxError as e:
            pytest.fail(f"Generated script has invalid syntax: {e}")

        # Should handle no arguments
        assert "# No arguments required" in script or "arguments = {}" in script


class TestCreateSkillMd:
    """Test create_skill_md function."""

    def test_creates_valid_structure(self, mock_simple_tool):
        """Test that generated SKILL.md has valid structure."""
        server_info = {
            "name": "test-server",
            "status": "connected",
            "toolCount": 1,
            "package": "test-package"
        }
        tools = [mock_simple_tool]

        md = create_skill_md("test-server", server_info, tools, "http://localhost:3000")

        # Should have frontmatter
        assert md.startswith("---")
        assert "name: mcp-test-server" in md
        assert "description:" in md

        # Should have main sections
        assert "# Test Server MCP Server" in md
        assert "## Prerequisites" in md
        assert "## Quick Start" in md
        assert "## Available Tools" in md
        assert "## State Persistence" in md
        assert "## Troubleshooting" in md

    def test_includes_server_name(self, mock_simple_tool):
        """Test that SKILL.md includes server name."""
        server_info = {"name": "chrome-devtools", "toolCount": 1}
        tools = [mock_simple_tool]

        md = create_skill_md("chrome-devtools", server_info, tools, "http://localhost:3000")

        assert "chrome-devtools" in md

    def test_includes_tool_count(self, mock_simple_tool, mock_complex_tool):
        """Test that SKILL.md includes correct tool count."""
        server_info = {"name": "test", "toolCount": 2}
        tools = [mock_simple_tool, mock_complex_tool]

        md = create_skill_md("test", server_info, tools, "http://localhost:3000")

        # Tool count should appear in description
        assert "2 tools" in md.lower()

    def test_includes_mcp2rest_url(self, mock_simple_tool):
        """Test that SKILL.md includes mcp2rest URL."""
        server_info = {"name": "test", "toolCount": 1}
        tools = [mock_simple_tool]
        url = "http://custom-host:9000"

        md = create_skill_md("test", server_info, tools, url)

        assert url in md

    def test_includes_package_info(self, mock_simple_tool):
        """Test that SKILL.md includes package information."""
        server_info = {
            "name": "test",
            "toolCount": 1,
            "package": "@scope/package-name"
        }
        tools = [mock_simple_tool]

        md = create_skill_md("test", server_info, tools, "http://localhost:3000")

        assert "@scope/package-name" in md

    def test_uses_url_when_no_package(self, mock_simple_tool):
        """Test that SKILL.md uses URL when package is not available."""
        server_info = {
            "name": "test",
            "toolCount": 1,
            "url": "https://example.com/api"
        }
        tools = [mock_simple_tool]

        md = create_skill_md("test", server_info, tools, "http://localhost:3000")

        assert "https://example.com/api" in md

    def test_includes_tool_names(self, mock_simple_tool, mock_complex_tool):
        """Test that SKILL.md includes tool names."""
        server_info = {"name": "test", "toolCount": 2}
        tools = [mock_simple_tool, mock_complex_tool]

        md = create_skill_md("test", server_info, tools, "http://localhost:3000")

        assert "click" in md
        assert "search" in md

    def test_includes_quick_start_example(self, mock_simple_tool):
        """Test that SKILL.md includes quick start example."""
        server_info = {"name": "test", "toolCount": 1}
        tools = [mock_simple_tool]

        md = create_skill_md("test", server_info, tools, "http://localhost:3000")

        assert "Quick Start" in md
        assert "```bash" in md
        assert f"{tools[0]['name']}.py --help" in md

    def test_includes_troubleshooting(self, mock_simple_tool):
        """Test that SKILL.md includes troubleshooting section."""
        server_info = {"name": "test", "toolCount": 1}
        tools = [mock_simple_tool]

        md = create_skill_md("test", server_info, tools, "http://localhost:3000")

        assert "Troubleshooting" in md
        assert "connection errors" in md.lower()
