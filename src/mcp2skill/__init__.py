"""mcp2skill: Generate Claude Code skills from mcp2rest servers.

mcp2skill queries your local mcp2rest service and generates SKILL.md files
with Python script wrappers for each MCP tool, making them available as
Claude Code skills.

Example:
    >>> from mcp2skill import SkillGenerator
    >>> gen = SkillGenerator("http://localhost:3000")
    >>> skill_dir = gen.generate_skill("chrome-devtools")
    >>> print(f"Skill generated at: {skill_dir}")

CLI Usage:
    $ mcp2skill servers
    $ mcp2skill generate chrome-devtools
    $ mcp2skill generate --all
"""

__version__ = "0.5.0"

# Core generator
from mcp2skill.generator import SkillGenerator

# Exceptions (reused from original mcp2py)
from mcp2skill.exceptions import (
    MCPError,
    MCPConnectionError,
    MCPToolError,
    MCPResourceError,
    MCPPromptError,
    MCPValidationError,
    MCPSamplingError,
    MCPElicitationError,
    MCPConfigError,
)

__all__ = [
    "SkillGenerator",
    "MCPError",
    "MCPConnectionError",
    "MCPToolError",
    "MCPResourceError",
    "MCPPromptError",
    "MCPValidationError",
    "MCPSamplingError",
    "MCPElicitationError",
    "MCPConfigError",
    "__version__",
]
