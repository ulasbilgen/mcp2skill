"""Custom exceptions for mcp2skill.

Provides clear, actionable error messages for common failure modes.
"""


class MCPError(Exception):
    """Base exception for all mcp2skill errors.

    All mcp2skill exceptions inherit from this base class.
    """
    pass


class MCPConnectionError(MCPError):
    """Failed to connect to MCP server.

    This error occurs when:
    - Server executable not found
    - Server crashes during startup
    - Network connection fails (for remote servers)
    - Server process terminates unexpectedly

    Example:
        >>> from mcp2skill import SkillGenerator
        >>> try:
        ...     gen = SkillGenerator("http://invalid-endpoint:9999")
        ...     servers = gen.list_servers()
        ... except MCPConnectionError as e:
        ...     print(f"Connection failed: {e}")
    """
    pass


class MCPToolError(MCPError):
    """Tool execution failed.

    This error occurs when:
    - Tool call fails on the server
    - Tool returns an error response
    - Tool arguments are invalid

    The error message includes details from the server about what went wrong.

    Example:
        >>> # Note: Currently unused in mcp2skill (reserved for future use)
        >>> # Originally from mcp2py for tool execution errors
        >>> pass
    """
    pass


class MCPResourceError(MCPError):
    """Resource access failed.

    This error occurs when:
    - Requested resource doesn't exist
    - Resource access is denied
    - Resource fetch fails

    Example:
        >>> # Note: Currently unused in mcp2skill (reserved for future use)
        >>> # Originally from mcp2py for resource access errors
        >>> pass
    """
    pass


class MCPPromptError(MCPError):
    """Prompt execution failed.

    This error occurs when:
    - Requested prompt doesn't exist
    - Prompt arguments are invalid
    - Prompt generation fails

    Example:
        >>> # Note: Currently unused in mcp2skill (reserved for future use)
        >>> # Originally from mcp2py for prompt execution errors
        >>> pass
    """
    pass


class MCPValidationError(MCPError):
    """Arguments failed validation.

    This error occurs when:
    - Required arguments are missing
    - Argument types don't match schema
    - Argument values are out of range

    Example:
        >>> # Note: Currently unused in mcp2skill (reserved for future use)
        >>> # Originally from mcp2py for argument validation errors
        >>> pass
    """
    pass


class MCPSamplingError(MCPError):
    """Sampling request failed.

    This error occurs when:
    - Sampling is disabled but server requests it
    - LLM API call fails
    - No API keys available for sampling

    Example:
        >>> # Note: Currently unused in mcp2skill (reserved for future use)
        >>> # Originally from mcp2py for LLM sampling errors
        >>> pass
    """
    pass


class MCPElicitationError(MCPError):
    """Elicitation request failed.

    This error occurs when:
    - Elicitation is disabled but server requests it
    - User input fails validation
    - Input prompt fails

    Example:
        >>> # Note: Currently unused in mcp2skill (reserved for future use)
        >>> # Originally from mcp2py for user input elicitation errors
        >>> pass
    """
    pass


class MCPConfigError(MCPError):
    """Configuration error.

    This error occurs when:
    - Invalid configuration provided
    - Registry file is corrupted
    - Configuration file has syntax errors

    Example:
        >>> # Note: Currently unused in mcp2skill (reserved for future use)
        >>> # Originally from mcp2py for configuration errors
        >>> pass
    """
    pass
