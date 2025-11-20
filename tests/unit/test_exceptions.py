"""Tests for exceptions module."""

import pytest
from mcp2skill.exceptions import (
    MCPError,
    MCPConnectionError,
    MCPToolError,
    MCPResourceError,
    MCPPromptError,
    MCPValidationError,
    MCPSamplingError,
    MCPElicitationError,
    MCPConfigError
)


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_all_exceptions_inherit_from_mcp_error(self):
        """Test that all MCP exceptions inherit from MCPError."""
        exceptions = [
            MCPConnectionError,
            MCPToolError,
            MCPResourceError,
            MCPPromptError,
            MCPValidationError,
            MCPSamplingError,
            MCPElicitationError,
            MCPConfigError
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, MCPError)

    def test_mcp_error_inherits_from_exception(self):
        """Test that MCPError inherits from Exception."""
        assert issubclass(MCPError, Exception)


class TestExceptionInstantiation:
    """Test that exceptions can be instantiated."""

    def test_mcp_error(self):
        """Test MCPError instantiation."""
        exc = MCPError("test message")
        assert str(exc) == "test message"

    def test_mcp_connection_error(self):
        """Test MCPConnectionError instantiation."""
        exc = MCPConnectionError("connection failed")
        assert str(exc) == "connection failed"

    def test_mcp_tool_error(self):
        """Test MCPToolError instantiation."""
        exc = MCPToolError("tool failed")
        assert str(exc) == "tool failed"

    def test_mcp_resource_error(self):
        """Test MCPResourceError instantiation."""
        exc = MCPResourceError("resource not found")
        assert str(exc) == "resource not found"

    def test_mcp_prompt_error(self):
        """Test MCPPromptError instantiation."""
        exc = MCPPromptError("prompt failed")
        assert str(exc) == "prompt failed"

    def test_mcp_validation_error(self):
        """Test MCPValidationError instantiation."""
        exc = MCPValidationError("validation failed")
        assert str(exc) == "validation failed"

    def test_mcp_sampling_error(self):
        """Test MCPSamplingError instantiation."""
        exc = MCPSamplingError("sampling failed")
        assert str(exc) == "sampling failed"

    def test_mcp_elicitation_error(self):
        """Test MCPElicitationError instantiation."""
        exc = MCPElicitationError("elicitation failed")
        assert str(exc) == "elicitation failed"

    def test_mcp_config_error(self):
        """Test MCPConfigError instantiation."""
        exc = MCPConfigError("config invalid")
        assert str(exc) == "config invalid"


class TestExceptionRaising:
    """Test that exceptions can be raised and caught."""

    def test_raise_mcp_error(self):
        """Test raising MCPError."""
        with pytest.raises(MCPError) as exc_info:
            raise MCPError("test")
        assert str(exc_info.value) == "test"

    def test_raise_mcp_connection_error(self):
        """Test raising MCPConnectionError."""
        with pytest.raises(MCPConnectionError):
            raise MCPConnectionError("connection error")

    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        try:
            raise MCPConnectionError("test")
        except MCPConnectionError as e:
            assert isinstance(e, MCPConnectionError)
            assert isinstance(e, MCPError)
            assert str(e) == "test"

    def test_catch_as_mcp_error(self):
        """Test catching specific exceptions as MCPError."""
        with pytest.raises(MCPError):
            raise MCPConnectionError("test")

    def test_catch_as_exception(self):
        """Test catching MCP exceptions as generic Exception."""
        with pytest.raises(Exception):
            raise MCPError("test")


class TestExceptionContextAndChaining:
    """Test exception context and chaining."""

    def test_exception_with_cause(self):
        """Test exception chaining with __cause__."""
        original = ValueError("original error")

        try:
            raise MCPConnectionError("wrapped error") from original
        except MCPConnectionError as e:
            assert e.__cause__ is original
            assert str(e) == "wrapped error"
            assert str(e.__cause__) == "original error"

    def test_exception_without_message(self):
        """Test exceptions can be raised without message."""
        with pytest.raises(MCPError):
            raise MCPError()
