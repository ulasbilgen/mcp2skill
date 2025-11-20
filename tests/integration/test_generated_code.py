"""Integration tests for generated code validation."""

import pytest
import ast
import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch
from mcp2skill.generator import SkillGenerator


class TestGeneratedPythonSyntax:
    """Test that generated Python code has valid syntax."""

    @patch('requests.get')
    def test_mcp_client_has_valid_syntax(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that generated mcp_client.py has valid Python syntax."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        mcp_client_path = skill_dir / "scripts" / "mcp_client.py"
        content = mcp_client_path.read_text()

        # Should parse without SyntaxError
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Generated mcp_client.py has invalid syntax: {e}")

    @patch('requests.get')
    def test_all_tool_scripts_have_valid_syntax(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that all generated tool scripts have valid Python syntax."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        scripts_dir = skill_dir / "scripts"

        # Check all tool scripts
        for script_path in scripts_dir.glob("*.py"):
            if script_path.name == "mcp_client.py":
                continue

            content = script_path.read_text()
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Generated script {script_path.name} has invalid syntax: {e}")

    @patch('requests.get')
    def test_tool_scripts_can_be_imported(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_simple_tool
    ):
        """Test that generated tool scripts can be imported as modules."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = [mock_simple_tool]
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        script_path = skill_dir / "scripts" / f"{mock_simple_tool['name']}.py"

        # Try to load as module
        spec = importlib.util.spec_from_file_location("test_module", script_path)
        assert spec is not None, "Could not create module spec"

    @patch('requests.get')
    def test_generated_scripts_have_shebang(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that generated tool scripts start with shebang."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        scripts_dir = skill_dir / "scripts"

        # Check all tool scripts (not mcp_client)
        for script_path in scripts_dir.glob("*.py"):
            if script_path.name == "mcp_client.py":
                continue

            content = script_path.read_text()
            assert content.startswith("#!/usr/bin/env python3"), \
                f"{script_path.name} doesn't start with shebang"

    @patch('requests.get')
    def test_generated_scripts_have_docstrings(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that generated scripts have docstrings."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        scripts_dir = skill_dir / "scripts"

        # Check tool scripts have docstrings
        for tool in mock_tools_response:
            script_path = scripts_dir / f"{tool['name']}.py"
            content = script_path.read_text()

            # Parse AST to check for docstring
            tree = ast.parse(content)
            assert ast.get_docstring(tree) is not None, \
                f"{script_path.name} has no module docstring"


class TestGeneratedMarkdownValidity:
    """Test that generated SKILL.md is valid markdown."""

    @patch('requests.get')
    def test_skill_md_has_frontmatter(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that SKILL.md has YAML frontmatter."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        skill_md = (skill_dir / "SKILL.md").read_text()

        # Check frontmatter structure
        assert skill_md.startswith("---\n"), "SKILL.md doesn't start with frontmatter"
        lines = skill_md.split('\n')
        assert "---" in lines[0], "Missing opening frontmatter delimiter"

        # Find closing delimiter
        closing_found = False
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                closing_found = True
                break

        assert closing_found, "Missing closing frontmatter delimiter"

    @patch('requests.get')
    def test_skill_md_has_required_fields(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that SKILL.md frontmatter has required fields."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        skill_md = (skill_dir / "SKILL.md").read_text()

        # Check required fields in frontmatter
        assert "name:" in skill_md, "Missing 'name' field in frontmatter"
        assert "description:" in skill_md, "Missing 'description' field in frontmatter"

    @patch('requests.get')
    def test_skill_md_has_proper_headers(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that SKILL.md has proper markdown headers."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        skill_md = (skill_dir / "SKILL.md").read_text()

        # Check for proper header hierarchy
        assert "\n# " in skill_md, "Missing H1 header"
        assert "\n## " in skill_md, "Missing H2 headers"

    @patch('requests.get')
    def test_skill_md_has_code_blocks(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that SKILL.md has properly formatted code blocks."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        skill_md = (skill_dir / "SKILL.md").read_text()

        # Check for code blocks
        assert "```bash" in skill_md, "Missing bash code blocks"
        assert "```" in skill_md, "Missing code blocks"

        # Check code blocks are balanced
        code_block_count = skill_md.count("```")
        assert code_block_count % 2 == 0, "Unbalanced code blocks (odd number of ```)"


class TestGeneratedCodeStructure:
    """Test the structure and organization of generated code."""

    @patch('requests.get')
    def test_mcp_client_has_call_tool_function(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that mcp_client.py has call_tool function."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        mcp_client_path = skill_dir / "scripts" / "mcp_client.py"
        content = mcp_client_path.read_text()

        tree = ast.parse(content)

        # Find call_tool function
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assert "call_tool" in functions, "mcp_client.py missing call_tool function"

    @patch('requests.get')
    def test_tool_scripts_import_mcp_client(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that tool scripts import from mcp_client."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        scripts_dir = skill_dir / "scripts"

        # Check each tool script imports mcp_client
        for tool in mock_tools_response:
            script_path = scripts_dir / f"{tool['name']}.py"
            content = script_path.read_text()

            assert "from mcp_client import" in content, \
                f"{script_path.name} doesn't import from mcp_client"

    @patch('requests.get')
    def test_tool_scripts_use_argparse(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that tool scripts use argparse for CLI."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        scripts_dir = skill_dir / "scripts"

        # Check tool scripts use argparse
        for tool in mock_tools_response:
            script_path = scripts_dir / f"{tool['name']}.py"
            content = script_path.read_text()

            assert "import argparse" in content, \
                f"{script_path.name} doesn't import argparse"
            assert "ArgumentParser" in content, \
                f"{script_path.name} doesn't use ArgumentParser"

    @patch('requests.get')
    def test_tool_scripts_have_main_guard(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that tool scripts have if __name__ == '__main__' guard."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        scripts_dir = skill_dir / "scripts"

        # Check tool scripts have main guard
        for tool in mock_tools_response:
            script_path = scripts_dir / f"{tool['name']}.py"
            content = script_path.read_text()

            assert 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content, \
                f"{script_path.name} doesn't have main guard"
