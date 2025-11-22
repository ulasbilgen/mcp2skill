"""Integration tests for end-to-end skill generation."""

import pytest
import requests
from pathlib import Path
from unittest.mock import Mock, patch
from mcp2skill.generator import SkillGenerator


class TestEndToEndSkillGeneration:
    """Test complete skill generation workflow."""

    @patch('requests.get')
    def test_complete_skill_generation_workflow(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test complete workflow from API calls to file generation."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator("http://localhost:28888")
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        # Verify directory structure
        assert skill_dir.exists()
        assert (skill_dir / "SKILL.md").exists()
        assert (skill_dir / "scripts").exists()
        assert (skill_dir / "scripts" / "mcp_client.py").exists()

        # Verify tool scripts generated
        tool_scripts = list((skill_dir / "scripts").glob("*.py"))
        assert len(tool_scripts) == 4  # 3 tools + mcp_client.py

    @patch('requests.get')
    def test_skill_directory_structure(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that generated skill has correct directory structure."""
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
        skill_dir = gen.generate_skill("filesystem", temp_skill_dir)

        # Check required files
        assert (skill_dir / "SKILL.md").is_file()
        assert (skill_dir / "scripts").is_dir()
        assert (skill_dir / "scripts" / "mcp_client.py").is_file()

        # Check naming convention
        assert skill_dir.name == "mcp-filesystem"

    @patch('requests.get')
    def test_multiple_skill_generation(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test generating skills for multiple servers."""
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

        # Generate two skills
        skill1 = gen.generate_skill("chrome-devtools", temp_skill_dir)
        skill2 = gen.generate_skill("filesystem", temp_skill_dir)

        # Both should exist
        assert skill1.exists()
        assert skill2.exists()
        assert skill1 != skill2

        # Both should have SKILL.md
        assert (skill1 / "SKILL.md").exists()
        assert (skill2 / "SKILL.md").exists()

    @patch('requests.get')
    def test_skill_regeneration_overwrites(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that regenerating a skill overwrites existing files."""
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

        # Generate skill first time
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)
        skill_md = skill_dir / "SKILL.md"
        original_content = skill_md.read_text()

        # Modify the file
        skill_md.write_text("# Modified content")
        assert skill_md.read_text() == "# Modified content"

        # Regenerate skill
        skill_dir2 = gen.generate_skill("chrome-devtools", temp_skill_dir)

        # Should overwrite with original
        assert skill_dir2 == skill_dir
        assert skill_md.read_text() != "# Modified content"
        assert "# Chrome Devtools MCP Server" in skill_md.read_text() or "# Chrome-Devtools MCP Server" in skill_md.read_text()

    @patch('requests.get')
    def test_generate_all_skills(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test generating all skills at once."""
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
        skill_dirs = gen.generate_all_skills(temp_skill_dir)

        # Should generate for connected servers with tools (2 in mock data: chrome-devtools, filesystem)
        assert len(skill_dirs) == 2

        # All should exist
        for skill_dir in skill_dirs:
            assert skill_dir.exists()
            assert (skill_dir / "SKILL.md").exists()
            assert (skill_dir / "scripts").exists()

    @patch('requests.get')
    def test_skill_md_content_validity(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that SKILL.md contains expected content."""
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

        # Check frontmatter
        assert skill_md.startswith("---")
        assert "name: mcp-chrome-devtools" in skill_md

        # Check main sections
        assert "## Prerequisites" in skill_md
        assert "## Quick Start" in skill_md
        assert "## Available Tools" in skill_md

        # Check tool mentions
        for tool in mock_tools_response:
            assert tool["name"] in skill_md

    @patch('requests.get')
    def test_mcp_client_functionality(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that mcp_client.py is properly generated."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator("http://custom-host:8080")
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        mcp_client = (skill_dir / "scripts" / "mcp_client.py").read_text()

        # Check key elements
        assert "def call_tool" in mcp_client
        assert "import requests" in mcp_client
        assert "custom-host:8080" in mcp_client

    @patch('requests.get')
    def test_tool_scripts_have_correct_names(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that tool scripts are named correctly."""
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

        # Check each tool has corresponding script
        for tool in mock_tools_response:
            script_path = scripts_dir / f"{tool['name']}.py"
            assert script_path.exists(), f"Script for {tool['name']} not found"

    @patch('requests.get')
    def test_file_permissions_on_scripts(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that tool scripts have executable permissions."""
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

        # Check tool scripts are executable
        for tool in mock_tools_response:
            script_path = scripts_dir / f"{tool['name']}.py"
            import stat
            st = script_path.stat()
            assert bool(st.st_mode & stat.S_IXUSR), f"{script_path} is not executable"

    @patch('requests.get')
    def test_skill_generation_with_minimal_tools(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_empty_tool
    ):
        """Test skill generation with tools that have no parameters."""
        def get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = [mock_empty_tool]
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        # Should still generate successfully
        assert skill_dir.exists()
        assert (skill_dir / "SKILL.md").exists()

        # Tool script should exist
        script_path = skill_dir / "scripts" / f"{mock_empty_tool['name']}.py"
        assert script_path.exists()

    @patch('requests.get')
    def test_error_handling_during_generation(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response
    ):
        """Test error handling during skill generation."""
        def get_side_effect(url, **kwargs):
            if "/tools" in url:
                # Tools request returns 404
                mock_response = Mock()
                mock_response.status_code = 404
                error = requests.exceptions.HTTPError("404")
                error.response = mock_response
                mock_response.raise_for_status.side_effect = error
                return mock_response
            else:
                # Servers request succeeds
                mock_response = Mock()
                mock_response.json.return_value = mock_servers_response
                mock_response.raise_for_status = Mock()
                return mock_response

        mock_get.side_effect = get_side_effect

        gen = SkillGenerator()

        with pytest.raises(ValueError) as exc_info:
            gen.generate_skill("nonexistent", temp_skill_dir)

        assert "not found" in str(exc_info.value).lower()

    @patch('requests.get')
    def test_path_expansion(
        self,
        mock_get,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that ~ in paths is expanded correctly."""
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

        # This should not raise an error (actual path expansion tested elsewhere)
        # Just verify it doesn't crash
        with patch.object(Path, 'expanduser') as mock_expand:
            from tempfile import mkdtemp
            temp_dir = Path(mkdtemp())
            mock_expand.return_value = temp_dir

            skill_dir = gen.generate_skill("chrome-devtools", "~/skills")
            assert skill_dir.exists()

    @patch('requests.get')
    def test_concurrent_skill_generation(
        self,
        mock_get,
        temp_skill_dir,
        mock_servers_response,
        mock_tools_response
    ):
        """Test that multiple skills can be generated to the same output directory."""
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

        # Generate multiple skills
        skill1 = gen.generate_skill("chrome-devtools", temp_skill_dir)
        skill2 = gen.generate_skill("filesystem", temp_skill_dir)

        # Both should exist in same parent directory
        assert skill1.parent == skill2.parent == temp_skill_dir
        assert skill1.exists()
        assert skill2.exists()
