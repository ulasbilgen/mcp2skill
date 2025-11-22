"""Command-line interface for mcp2skill."""

import sys
import click
from pathlib import Path

from mcp2skill import __version__
from mcp2skill.generator import SkillGenerator


@click.group()
@click.version_option(version=__version__, prog_name="mcp2skill")
def cli():
    """Generate Claude Code skills from mcp2rest servers.

    mcp2skill queries your local mcp2rest service and generates
    SKILL.md files with Python script wrappers for each MCP tool.
    """
    pass


@cli.command()
@click.option(
    '--endpoint',
    default='http://localhost:28888',
    help='mcp2rest service URL (default: http://localhost:28888)',
    show_default=True
)
def servers(endpoint):
    """List available MCP servers from mcp2rest."""
    try:
        gen = SkillGenerator(endpoint)
        servers = gen.list_servers()

        if not servers:
            click.echo("No servers found in mcp2rest.")
            click.echo(f"\nMake sure mcp2rest is running at {endpoint}")
            return

        click.echo(f"Available servers in mcp2rest ({endpoint}):\n")

        for server in servers:
            name = server['name']
            status = server['status']
            tool_count = server.get('toolCount', 0)
            transport = server.get('transport', 'unknown')

            # Color-code status
            if status == 'connected':
                status_color = 'green'
                status_symbol = '✓'
            elif status == 'disconnected':
                status_color = 'red'
                status_symbol = '✗'
            else:
                status_color = 'yellow'
                status_symbol = '!'

            click.echo(f"  {click.style(status_symbol, fg=status_color)} {name}")
            click.echo(f"    Status: {click.style(status, fg=status_color)}")
            click.echo(f"    Tools: {tool_count}")
            click.echo(f"    Transport: {transport}")

            if server.get('package'):
                click.echo(f"    Package: {server['package']}")
            elif server.get('url'):
                click.echo(f"    URL: {server['url']}")

            click.echo()

    except ConnectionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {type(e).__name__}: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('server_name', required=False)
@click.option(
    '--all',
    is_flag=True,
    help='Generate skills for all connected servers'
)
@click.option(
    '--output',
    '-o',
    default='~/.claude/skills',
    help='Output directory for generated skills',
    show_default=True
)
@click.option(
    '--endpoint',
    default='http://localhost:28888',
    help='mcp2rest service URL',
    show_default=True
)
def generate(server_name, all, output, endpoint):
    """Generate Claude Code skill(s) from MCP server(s).

    Examples:

      \b
      # Generate skill for chrome-devtools server
      mcp2skill generate chrome-devtools

      \b
      # Generate skills for all servers
      mcp2skill generate --all

      \b
      # Generate to custom directory
      mcp2skill generate chrome-devtools -o ./my-skills

      \b
      # Use custom mcp2rest endpoint
      mcp2skill generate chrome-devtools --endpoint http://192.168.1.100:28888
    """
    if not server_name and not all:
        click.echo("Error: Must specify SERVER_NAME or use --all flag", err=True)
        click.echo("\nRun 'mcp2skill generate --help' for usage info", err=True)
        sys.exit(1)

    if server_name and all:
        click.echo("Error: Cannot use SERVER_NAME and --all together", err=True)
        sys.exit(1)

    try:
        gen = SkillGenerator(endpoint)

        if all:
            # Generate for all servers
            click.echo(f"Generating skills for all servers...")
            click.echo(f"mcp2rest: {endpoint}")
            click.echo(f"Output: {output}\n")

            skill_dirs = gen.generate_all_skills(output)

            if not skill_dirs:
                click.echo("No connected servers with tools found.", err=True)
                sys.exit(1)

            click.echo(f"\n{click.style('✓', fg='green')} Generated {len(skill_dirs)} skill(s):")
            for skill_dir in skill_dirs:
                click.echo(f"  {skill_dir}")

        else:
            # Generate for specific server
            click.echo(f"Generating skill for '{server_name}'...")
            click.echo(f"mcp2rest: {endpoint}")
            click.echo(f"Output: {output}\n")

            skill_dir = gen.generate_skill(server_name, output)

            # Count generated scripts
            scripts_dir = skill_dir / "scripts"
            script_count = len(list(scripts_dir.glob("*.py"))) - 1  # Exclude mcp_client.py

            click.echo(f"{click.style('✓', fg='green')} Generated skill: {skill_dir}")
            click.echo(f"  SKILL.md: {skill_dir / 'SKILL.md'}")
            click.echo(f"  Scripts: {script_count} tools + 1 shared client")

        click.echo(f"\n{click.style('Next steps:', bold=True)}")
        click.echo("  1. Claude Code will auto-discover skills in ~/.claude/skills/")
        click.echo("  2. Or manually navigate to skill directory")
        click.echo(f"  3. Run scripts: python scripts/tool_name.py --help")

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ConnectionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {type(e).__name__}: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('server_name')
@click.option(
    '--endpoint',
    default='http://localhost:28888',
    help='mcp2rest service URL',
    show_default=True
)
def tools(server_name, endpoint):
    """Show tools available on a server.

    Example:

      \b
      mcp2skill tools chrome-devtools
    """
    try:
        gen = SkillGenerator(endpoint)

        # Get server info
        server_info = gen.get_server_info(server_name)
        if not server_info:
            click.echo(f"Error: Server '{server_name}' not found", err=True)
            click.echo("\nAvailable servers:", err=True)
            for s in gen.list_servers():
                click.echo(f"  - {s['name']}", err=True)
            sys.exit(1)

        # Get tools
        tools_list = gen.get_tools(server_name)

        click.echo(f"Tools for '{server_name}' ({len(tools_list)} total):\n")

        for tool in tools_list:
            name = tool['name']
            desc = tool.get('description', 'No description')
            schema = tool.get('inputSchema', {})
            required = schema.get('required', [])
            properties = schema.get('properties', {})

            click.echo(f"  {click.style(name, bold=True)}")
            click.echo(f"    {desc}")

            if required:
                click.echo(f"    Required: {', '.join(required)}")

            optional = [p for p in properties.keys() if p not in required]
            if optional:
                click.echo(f"    Optional: {', '.join(optional)}")

            click.echo()

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ConnectionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {type(e).__name__}: {e}", err=True)
        sys.exit(1)


def cli_main():
    """Entry point for console script."""
    cli()


if __name__ == '__main__':
    cli_main()
