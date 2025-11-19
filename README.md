# mcp2skill: Generate Claude Code Skills from MCP Servers

**Turn MCP servers into Claude Code skills in 3 steps.**

```bash
# 1. Check available servers
mcp2skill servers

# 2. Generate skill
mcp2skill generate chrome-devtools

# 3. Done! Claude Code auto-discovers it
```

Skills include minimal SKILL.md documentation and Python scripts that wrap REST API calls to your [mcp2rest](https://github.com/ulasbilgen/mcp2rest) service.

---

## What is mcp2skill?

**mcp2skill** is a skill generator that transforms MCP servers running in mcp2rest into Claude Code skills.

- 🎯 **Queries mcp2rest REST API** to get tool schemas
- 📝 **Generates SKILL.md** with concise documentation
- 🐍 **Creates Python scripts** for each tool (clean argparse wrappers)
- 🤖 **Claude Code ready** - auto-discovered from `~/.claude/skills/`
- 🔄 **Stateful** - mcp2rest maintains server state between calls

**Not a runtime library** - it's a code generator that creates skills from MCP servers.

---

## Prerequisites

### 1. Install and Configure mcp2rest

[mcp2rest](https://github.com/ulasbilgen/mcp2rest) is a Node.js service that manages MCP servers and exposes them via REST API.

```bash
# Install globally
npm install -g mcp2rest

# Add MCP servers
mcp2rest add chrome-devtools chrome-devtools-mcp@latest
mcp2rest add figma-desktop --url http://127.0.0.1:3845/mcp

# Start service (runs on localhost:3000)
mcp2rest start

# Or run as system service
mcp2rest service install
mcp2rest service start
```

### 2. Install mcp2skill

```bash
pip install mcp2skill
```

---

## Quick Start

### List Available Servers

```bash
mcp2skill servers
```

Output:
```
Available servers in mcp2rest (http://localhost:3000):

  ✓ chrome-devtools
    Status: connected
    Tools: 26
    Transport: stdio
    Package: chrome-devtools-mcp@latest

  ✓ figma-desktop
    Status: connected
    Tools: 7
    Transport: http
    URL: http://127.0.0.1:3845/mcp
```

### Generate Skills

```bash
# Generate one skill
mcp2skill generate chrome-devtools

# Generate all at once
mcp2skill generate --all

# Custom output location
mcp2skill generate chrome-devtools --output /path/to/skills
```

### Generated Structure

```
~/.claude/skills/
└── mcp-chrome-devtools/
    ├── SKILL.md              # Concise documentation (~130 lines)
    └── scripts/
        ├── mcp_client.py     # Shared REST client
        ├── new_page.py       # Tool: Open new browser page
        ├── click.py          # Tool: Click element
        ├── take_snapshot.py  # Tool: Get page structure
        └── ... (26 tools total)
```

### Use with Claude Code

**Claude Code automatically discovers skills** in `~/.claude/skills/`. Just ask:

```
User: "Open example.com and click the login button"

Claude: [Discovers mcp-chrome-devtools skill]
        [Runs: python scripts/new_page.py --url https://example.com]
        [Runs: python scripts/take_snapshot.py]
        [Finds button UID in snapshot]
        [Runs: python scripts/click.py --uid login_btn_123]

        ✓ Opened example.com and clicked the login button
```

### Use Scripts Directly

```bash
cd ~/.claude/skills/mcp-chrome-devtools/scripts

# Get help for any tool
python new_page.py --help

# Execute tools
python new_page.py --url https://example.com
python take_snapshot.py
python click.py --uid button_abc123
```

---

## Interactive Mode (Slash Commands)

**NEW:** Use Claude Code slash commands for an interactive, LLM-assisted skill generation workflow.

### Available Commands

mcp2skill includes 5 slash commands for interactive use within Claude Code:

| Command | Description |
|---------|-------------|
| `/m2s-init` | First-time setup wizard (installs mcp2rest + mcp2skill) |
| `/m2s-list` | List available MCP servers and their skill status |
| `/m2s-add <server> [package]` | Add new server to mcp2rest |
| `/m2s-generate <server>` | **Interactive skill generation with Claude** |
| `/m2s-update <server>` | Update existing skill with latest tools/docs |

### Interactive Skill Generation

The `/m2s-generate` command provides an **LLM-enhanced** workflow where Claude:

1. **Analyzes your MCP server** - Reads tool descriptions and detects domain
2. **Suggests intelligent groupings** - For servers with >10 tools
3. **Generates enhanced SKILL.md** - Following [best practices](skill-authoring-guide.md)
4. **Creates reference files** - Progressive disclosure for complex skills
5. **Iterates with your feedback** - Refine and improve before finalizing

### Example: Interactive Generation

```
You: /m2s-generate chrome-devtools

Claude: I found 26 tools in chrome-devtools. Let me analyze them...

        I suggest organizing into 4 groups:
        1. Page Management (6 tools) - new_page, navigate, close_page...
        2. Element Interaction (8 tools) - click, fill, hover...
        3. Inspection & Debug (7 tools) - take_snapshot, screenshot...
        4. Advanced (5 tools) - evaluate_script, inject_script...

        Does this structure work for you?

You: Yes, but split Element Interaction into Basic and Forms

Claude: Updated structure:
        2a. Basic Interaction (4 tools) - click, hover, drag...
        2b. Form Automation (4 tools) - fill, submit_form, upload...

        Generating skill with:
        - SKILL.md (overview + quick start)
        - workflows/automation.md (form workflows)
        - workflows/testing.md (inspection workflows)
        - reference/all-tools.md (complete listing)

        [Shows preview of SKILL.md...]

        ✓ Generated skill at ~/.claude/skills/mcp-chrome-devtools/
```

### Benefits of Interactive Mode

**vs. CLI mode:**
- 🤖 **LLM-enhanced** - Claude analyzes tools and generates better docs
- 📊 **Smart grouping** - Automatic tool organization for large skill sets
- 📝 **Best practices** - Follows [skill-authoring-guide.md](skill-authoring-guide.md) automatically
- 🔄 **Iterative** - Review and refine before finalizing
- ✅ **Progressive disclosure** - Proper file structure for complex skills

**CLI mode still available** for automation:
```bash
mcp2skill generate chrome-devtools  # Non-interactive, template-based
```

### First-Time Setup with /m2s-init

```
You: /m2s-init

Claude: Let me help you set up mcp2skill...

        Checking mcp2rest... not installed
        → Installing: npm install -g mcp2rest
        ✓ Installed

        Checking mcp2skill... not installed
        → Installing: pip install mcp2skill
        ✓ Installed

        Starting mcp2rest service...
        ✓ Running on http://localhost:3000

        No servers found. Would you like to add one?

        Popular options:
        - chrome-devtools-mcp@latest (browser automation)
        - @modelcontextprotocol/server-filesystem (file ops)

You: Add chrome-devtools

Claude: Adding chrome-devtools...
        [Runs: mcp2rest add chrome-devtools chrome-devtools-mcp@latest]
        ✓ Connected with 26 tools

        Ready to generate skill? Use: /m2s-generate chrome-devtools
```

---

## Complete Example: Web Form Automation

**Scenario**: Fill out a contact form on example.com

### Step 1: Navigate to the Form

```bash
python scripts/new_page.py --url https://example.com/contact
```

### Step 2: Get Page Structure

```bash
python scripts/take_snapshot.py
```

Output shows element UIDs:
```
# contact_form response
## Accessibility Tree

Window - Contact Us

[uid="email_input"] textbox "Email"
[uid="message_textarea"] textbox "Message"
[uid="submit_btn"] button "Submit"
```

### Step 3: Fill Form Fields

```bash
python scripts/fill.py --uid email_input --value "user@example.com"
python scripts/fill.py --uid message_textarea --value "Hello, I need help!"
```

### Step 4: Submit

```bash
python scripts/click.py --uid submit_btn
```

### Step 5: Verify

```bash
python scripts/take_screenshot.py --format png
```

**All state persists** - the browser session stays open between script calls because mcp2rest maintains the server state.

---

## How It Works

### Architecture Flow

```
┌─────────────────────────────────────────┐
│ 1. mcp2skill queries mcp2rest           │
│    GET /servers/chrome-devtools/tools   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ 2. Generates SKILL.md + Python scripts  │
│    Saves to ~/.claude/skills/           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ 3. Claude Code discovers skill OR       │
│    User runs scripts manually           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ 4. Script calls mcp2rest REST API       │
│    POST /call                           │
│    {server, tool, arguments}            │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ 5. mcp2rest forwards to MCP server      │
│    Server maintains state               │
│    Returns result                       │
└─────────────────────────────────────────┘
```

### Key Concepts

**State Persistence**
- mcp2rest runs MCP servers as persistent processes
- Browser pages, sessions, data persist between script calls
- Scripts are stateless - they just make REST calls
- State lives in mcp2rest/MCP server

**Minimal Context**
- SKILL.md files are concise (~100-150 lines)
- Just tool names, args, and basic examples
- No verbose curl commands cluttering context
- Python scripts handle REST complexity

**Type Safety**
- Scripts auto-generated from JSON Schema
- Proper argparse with types, required/optional args
- Help text from tool descriptions
- `--help` on any script shows usage

---

## Advanced Usage

### Inspect Server Tools

```bash
mcp2skill tools chrome-devtools
```

Shows all 26 tools with descriptions and parameters.

### Custom mcp2rest Endpoint

```bash
# Via command line
mcp2skill servers --endpoint http://192.168.1.100:3000

# Via environment variable
export MCP_REST_URL="http://192.168.1.100:3000"
mcp2skill generate chrome-devtools
```

Scripts respect `MCP_REST_URL` environment variable.

### Generate to Custom Location

```bash
# Project-specific skills
mcp2skill generate chrome-devtools --output ./project-skills

# Then use them
cd project-skills/mcp-chrome-devtools/scripts
python new_page.py --url https://myapp.local
```

### Distribution via Git

```bash
# Generate skills
mcp2skill generate --all --output ./my-mcp-skills

# Publish
cd my-mcp-skills
git init
git add .
git commit -m "MCP skills for our team"
git push origin main

# Team members install
git clone https://github.com/team/my-mcp-skills.git ~/.claude/skills/
```

---

## CLI Reference

### Commands

**`mcp2skill servers [--endpoint URL]`**
- List available MCP servers from mcp2rest
- Shows status, tool count, transport type

**`mcp2skill generate <server_name> [--output DIR] [--endpoint URL]`**
- Generate skill for specific server
- Default output: `~/.claude/skills/`

**`mcp2skill generate --all [--output DIR] [--endpoint URL]`**
- Generate skills for all connected servers

**`mcp2skill tools <server_name> [--endpoint URL]`**
- Show detailed tool information for a server

### Options

- `--output`, `-o`: Output directory (default: `~/.claude/skills/`)
- `--endpoint`: mcp2rest URL (default: `http://localhost:3000`)
- `--help`: Show help message
- `--version`: Show version

---

## Generated Skill Structure

### SKILL.md

Concise documentation with:
- Prerequisites (mcp2rest running)
- Tool listing by category
- Common workflow examples
- State persistence notes
- Troubleshooting tips

### scripts/

**`mcp_client.py`** - Shared REST client
- Handles POST requests to mcp2rest `/call` endpoint
- Formats responses (text, images, errors)
- Error handling with clear messages

**Tool scripts** (e.g., `click.py`)
- Auto-generated from tool's JSON Schema
- Argparse with proper types
- Required vs optional parameters
- `--help` documentation
- Calls `mcp_client.call_tool()`

---

## Real-World Examples

### Browser Automation (chrome-devtools)

```bash
# Full workflow: search and extract data
python new_page.py --url https://news.ycombinator.com
python take_snapshot.py > structure.txt
# Review structure.txt to find article UIDs
python click.py --uid article_5
python evaluate_script.py --function "() => document.title"
```

### Design Tool Integration (figma-desktop)

```bash
# Extract design tokens from Figma
python get_design_context.py --nodeId "1:2"
python get_variable_defs.py --nodeId "1:2"
python get_screenshot.py --nodeId "1:2" --format png
```

### Combining with Other Tools

```bash
# Take screenshot, process with vision model
python new_page.py --url https://myapp.com/dashboard
python take_screenshot.py --format png > dashboard.png
# Use vision API to analyze dashboard.png
```

---

## Troubleshooting

### "Cannot connect to mcp2rest"

```bash
# Check mcp2rest is running
curl http://localhost:3000/health

# If not running, start it
mcp2rest start

# Check what servers are loaded
curl http://localhost:3000/servers
```

### "Server not found"

```bash
# List available servers
mcp2skill servers

# Add server to mcp2rest
mcp2rest add chrome-devtools chrome-devtools-mcp@latest

# Restart mcp2rest
mcp2rest service restart
```

### Script Errors

```bash
# Check tool arguments
python scripts/click.py --help

# Test mcp2rest API directly
curl -X POST http://localhost:3000/call \
  -H "Content-Type: application/json" \
  -d '{"server":"chrome-devtools","tool":"list_pages","arguments":{}}'
```

---

## Why mcp2skill?

**Clean Agent Context**
- SKILL.md is concise (~100 lines) not bloated with curl commands
- Python scripts handle REST complexity
- Agent just needs to know: tool name, arguments

**State Management**
- mcp2rest maintains server state
- Browser sessions persist
- Database connections stay open
- Sequential operations work naturally

**Developer Friendly**
- Type-safe scripts from JSON Schema
- `--help` on every script
- Standard argparse interface
- Easy to test and debug

**Distribution**
- Share skills via git repos
- Team installs: `git clone url ~/.claude/skills/`
- Version control for skills
- Custom skills per project

---

## Related Projects

- **[mcp2rest](https://github.com/ulasbilgen/mcp2rest)** - REST API gateway for MCP servers (required)
- **[MCP](https://modelcontextprotocol.io)** - Model Context Protocol specification
- **[Claude Code](https://claude.com/claude-code)** - AI coding assistant with skill support

---

## License

MIT License - see LICENSE file

## Contributing

Issues and pull requests welcome!

- GitHub: [https://github.com/ulasbilgen/mcp2skill](https://github.com/ulasbilgen/mcp2skill)
- Issues: [https://github.com/ulasbilgen/mcp2skill/issues](https://github.com/ulasbilgen/mcp2skill/issues)

---

## Changelog

### v0.6.0 (Current)
- **NEW: Interactive mode** with 5 Claude Code slash commands
- LLM-assisted skill generation with `/m2s-generate`
- Smart tool grouping for servers with >10 tools
- Progressive disclosure (SKILL.md + reference files)
- Setup wizard (`/m2s-init`) for first-time users
- Skill authoring best practices guide
- CLI mode still available for automation

### v0.5.0
- Complete rewrite as skill generator
- Removed subprocess spawning, daemon features
- Generate Claude Code skills from mcp2rest
- Python scripts with argparse wrappers
- Auto-discovery in ~/.claude/skills/
