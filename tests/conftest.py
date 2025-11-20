"""Pytest configuration and shared fixtures for mcp2skill tests."""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Any


@pytest.fixture
def mock_mcp2rest_url():
    """Mock mcp2rest endpoint URL."""
    return "http://localhost:3000"


@pytest.fixture
def mock_servers_response():
    """Mock response for GET /servers endpoint."""
    return [
        {
            "name": "chrome-devtools",
            "status": "connected",
            "toolCount": 15,
            "transport": "stdio",
            "package": "@modelcontextprotocol/server-chrome"
        },
        {
            "name": "filesystem",
            "status": "connected",
            "toolCount": 8,
            "transport": "stdio",
            "package": "@modelcontextprotocol/server-filesystem"
        },
        {
            "name": "disconnected-server",
            "status": "disconnected",
            "toolCount": 0,
            "transport": "stdio",
            "package": "test-server"
        }
    ]


@pytest.fixture
def mock_simple_tool():
    """Mock simple tool with basic parameters."""
    return {
        "name": "click",
        "description": "Click on an element by its selector",
        "inputSchema": {
            "type": "object",
            "required": ["selector"],
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector for the element to click"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in milliseconds",
                    "default": 5000
                }
            }
        }
    }


@pytest.fixture
def mock_complex_tool():
    """Mock complex tool with various parameter types."""
    return {
        "name": "search",
        "description": "Search with complex parameters",
        "inputSchema": {
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
                    "description": "List of sources to search"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results",
                    "default": 10
                },
                "includeMetadata": {
                    "type": "boolean",
                    "description": "Include metadata in results",
                    "default": False
                },
                "sortBy": {
                    "type": "string",
                    "enum": ["relevance", "date", "title"],
                    "description": "Sort order"
                },
                "filters": {
                    "type": "object",
                    "description": "Additional filters as JSON"
                }
            }
        }
    }


@pytest.fixture
def mock_tools_response(mock_simple_tool, mock_complex_tool):
    """Mock response for GET /servers/{name}/tools endpoint."""
    return [
        mock_simple_tool,
        mock_complex_tool,
        {
            "name": "navigate",
            "description": "Navigate to a URL",
            "inputSchema": {
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    }
                }
            }
        }
    ]


@pytest.fixture
def mock_empty_tool():
    """Mock tool with no input parameters."""
    return {
        "name": "get_status",
        "description": "Get current status",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }


@pytest.fixture
def temp_skill_dir():
    """Create a temporary directory for skill generation tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_requests_get(mock_servers_response, mock_tools_response):
    """Mock requests.get for mcp2rest API calls."""
    def _mock_get(url, **kwargs):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        if url.endswith("/servers"):
            mock_response.json.return_value = mock_servers_response
        elif "/tools" in url:
            mock_response.json.return_value = mock_tools_response
        else:
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("Not found")

        return mock_response

    return _mock_get


@pytest.fixture
def mock_requests_get_error():
    """Mock requests.get that raises ConnectionError."""
    def _mock_get(url, **kwargs):
        raise ConnectionError("Failed to connect to mcp2rest")

    return _mock_get


@pytest.fixture
def mock_skill_generator(mock_mcp2rest_url, monkeypatch, mock_requests_get):
    """Create a SkillGenerator with mocked HTTP requests."""
    from mcp2skill.generator import SkillGenerator
    import requests

    # Patch requests.get to use our mock
    monkeypatch.setattr(requests, "get", mock_requests_get)

    return SkillGenerator(mock_mcp2rest_url)


def assert_valid_skill_structure(skill_dir: Path):
    """Assert that a generated skill has the correct file structure.

    Args:
        skill_dir: Path to the generated skill directory

    Raises:
        AssertionError: If the skill structure is invalid
    """
    # Check directory exists
    assert skill_dir.exists(), f"Skill directory does not exist: {skill_dir}"
    assert skill_dir.is_dir(), f"Skill path is not a directory: {skill_dir}"

    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    assert skill_md.exists(), f"SKILL.md not found in {skill_dir}"
    assert skill_md.is_file(), f"SKILL.md is not a file: {skill_md}"

    # Check scripts directory exists
    scripts_dir = skill_dir / "scripts"
    assert scripts_dir.exists(), f"scripts directory not found in {skill_dir}"
    assert scripts_dir.is_dir(), f"scripts is not a directory: {scripts_dir}"

    # Check mcp_client.py exists
    mcp_client = scripts_dir / "mcp_client.py"
    assert mcp_client.exists(), f"mcp_client.py not found in {scripts_dir}"
    assert mcp_client.is_file(), f"mcp_client.py is not a file: {mcp_client}"


def assert_valid_python_syntax(file_path: Path):
    """Assert that a Python file has valid syntax.

    Args:
        file_path: Path to the Python file

    Raises:
        AssertionError: If the file has invalid syntax
    """
    import ast

    assert file_path.exists(), f"File does not exist: {file_path}"

    content = file_path.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        raise AssertionError(f"Invalid Python syntax in {file_path}: {e}")


def assert_script_executable(file_path: Path):
    """Assert that a script file has executable permissions.

    Args:
        file_path: Path to the script file

    Raises:
        AssertionError: If the file is not executable
    """
    import os
    import stat

    assert file_path.exists(), f"File does not exist: {file_path}"

    st = file_path.stat()
    is_executable = bool(st.st_mode & stat.S_IXUSR)

    assert is_executable, f"Script is not executable: {file_path}"


def load_fixture(fixture_name: str) -> Any:
    """Load a JSON fixture file.

    Args:
        fixture_name: Name of the fixture file (without .json extension)

    Returns:
        Parsed JSON data
    """
    fixtures_dir = Path(__file__).parent / "fixtures"
    fixture_path = fixtures_dir / f"{fixture_name}.json"

    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")

    with open(fixture_path, 'r') as f:
        return json.load(f)
