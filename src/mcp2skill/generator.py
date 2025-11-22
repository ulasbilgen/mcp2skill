"""Generate Claude Code skills from mcp2rest servers."""

import json
import requests
from pathlib import Path
from typing import Any

from mcp2skill.templates import create_skill_md, create_mcp_client_script, create_tool_script
from mcp2skill.schema_utils import generate_argparse_from_schema


class SkillGenerator:
    """Generator for Claude Code skills from mcp2rest servers."""

    def __init__(self, mcp2rest_url: str = "http://localhost:28888"):
        """Initialize skill generator.

        Args:
            mcp2rest_url: Base URL of mcp2rest service (default: http://localhost:28888)
        """
        self.base_url = mcp2rest_url.rstrip('/')

    def list_servers(self) -> list[dict[str, Any]]:
        """Get all servers from mcp2rest.

        Returns:
            List of server info dictionaries

        Raises:
            ConnectionError: If cannot connect to mcp2rest
            requests.HTTPError: If request fails
        """
        try:
            resp = requests.get(f"{self.base_url}/servers", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Cannot connect to mcp2rest at {self.base_url}. "
                "Make sure mcp2rest is running."
            ) from e
        except requests.exceptions.Timeout as e:
            raise ConnectionError(
                f"Timeout connecting to mcp2rest at {self.base_url}"
            ) from e

    def get_tools(self, server_name: str) -> list[dict[str, Any]]:
        """Get tool schemas for a server.

        Args:
            server_name: Name of the MCP server

        Returns:
            List of tool schema dictionaries

        Raises:
            ValueError: If server not found
            requests.HTTPError: If request fails
        """
        try:
            resp = requests.get(
                f"{self.base_url}/servers/{server_name}/tools",
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(
                    f"Server '{server_name}' not found in mcp2rest. "
                    f"Available servers: {[s['name'] for s in self.list_servers()]}"
                ) from e
            raise

    def get_server_info(self, server_name: str) -> dict[str, Any] | None:
        """Get info about a specific server.

        Args:
            server_name: Name of the MCP server

        Returns:
            Server info dict or None if not found
        """
        servers = self.list_servers()
        for server in servers:
            if server['name'] == server_name:
                return server
        return None

    def generate_skill(
        self,
        server_name: str,
        output_dir: str | Path = "~/.claude/skills"
    ) -> Path:
        """Generate Claude Code skill for an MCP server.

        Creates:
          {output_dir}/mcp-{server_name}/
            ├── SKILL.md              # Minimal skill documentation
            ├── scripts/
            │   ├── mcp_client.py     # Shared REST client
            │   ├── tool1.py          # Generated script for tool1
            │   ├── tool2.py          # Generated script for tool2
            │   └── ...

        Args:
            server_name: Name of the MCP server in mcp2rest
            output_dir: Directory to create skill in (default: ~/.claude/skills)

        Returns:
            Path to generated skill directory

        Raises:
            ValueError: If server not found or has no tools
            OSError: If cannot write files
        """
        # Expand user path
        output_path = Path(output_dir).expanduser()

        # Get server info and tools
        server_info = self.get_server_info(server_name)
        if not server_info:
            raise ValueError(
                f"Server '{server_name}' not found in mcp2rest. "
                f"Run 'mcp2skill servers' to see available servers."
            )

        tools = self.get_tools(server_name)
        if not tools:
            raise ValueError(
                f"Server '{server_name}' has no tools available."
            )

        # Create skill directory
        skill_dir = output_path / f"mcp-{server_name}"
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Generate SKILL.md
        skill_md = create_skill_md(
            server_name=server_name,
            server_info=server_info,
            tools=tools,
            mcp2rest_url=self.base_url
        )
        (skill_dir / "SKILL.md").write_text(skill_md)

        # Create scripts directory
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        # Generate shared mcp_client.py utility
        mcp_client_code = create_mcp_client_script(self.base_url)
        (scripts_dir / "mcp_client.py").write_text(mcp_client_code)

        # Generate Python script for each tool
        for tool in tools:
            script_code = create_tool_script(
                server_name=server_name,
                tool=tool
            )
            script_file = scripts_dir / f"{tool['name']}.py"
            script_file.write_text(script_code)
            # Make executable
            script_file.chmod(0o755)

        return skill_dir

    def generate_all_skills(
        self,
        output_dir: str | Path = "~/.claude/skills"
    ) -> list[Path]:
        """Generate skills for all servers in mcp2rest.

        Args:
            output_dir: Directory to create skills in (default: ~/.claude/skills)

        Returns:
            List of paths to generated skill directories
        """
        servers = self.list_servers()
        generated = []

        for server in servers:
            if server['status'] == 'connected' and server.get('toolCount', 0) > 0:
                try:
                    skill_dir = self.generate_skill(
                        server['name'],
                        output_dir
                    )
                    generated.append(skill_dir)
                except Exception as e:
                    print(f"Warning: Failed to generate skill for {server['name']}: {e}")

        return generated
