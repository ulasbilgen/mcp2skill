"""Tests for CLI module."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
from mcp2skill.cli import cli


class TestCliVersion:
    """Test CLI version option."""

    def test_version_flag(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '0.5.0' in result.output


class TestServersCommand:
    """Test servers command."""

    @patch('mcp2skill.cli.SkillGenerator')
    def test_servers_success(self, mock_gen_class):
        """Test successful servers listing."""
        mock_gen = Mock()
        mock_gen.list_servers.return_value = [
            {"name": "chrome", "status": "connected", "toolCount": 15, "transport": "stdio"},
            {"name": "filesystem", "status": "connected", "toolCount": 8, "transport": "stdio"}
        ]
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['servers'])

        assert result.exit_code == 0
        assert 'chrome' in result.output
        assert 'filesystem' in result.output
        assert 'connected' in result.output.lower()

    @patch('mcp2skill.cli.SkillGenerator')
    def test_servers_empty(self, mock_gen_class):
        """Test servers command with no servers."""
        mock_gen = Mock()
        mock_gen.list_servers.return_value = []
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['servers'])

        assert result.exit_code == 0
        assert 'No servers found' in result.output

    @patch('mcp2skill.cli.SkillGenerator')
    def test_servers_connection_error(self, mock_gen_class):
        """Test servers command with connection error."""
        mock_gen = Mock()
        mock_gen.list_servers.side_effect = ConnectionError("Cannot connect")
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['servers'])

        assert result.exit_code == 1
        assert 'Error' in result.output

    @patch('mcp2skill.cli.SkillGenerator')
    def test_servers_custom_endpoint(self, mock_gen_class):
        """Test servers command with custom endpoint."""
        mock_gen = Mock()
        mock_gen.list_servers.return_value = []
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['servers', '--endpoint', 'http://custom:8080'])

        assert result.exit_code == 0
        mock_gen_class.assert_called_once_with('http://custom:8080')


class TestGenerateCommand:
    """Test generate command."""

    @patch('mcp2skill.cli.SkillGenerator')
    def test_generate_success(self, mock_gen_class, tmp_path):
        """Test successful skill generation."""
        mock_gen = Mock()
        skill_dir = tmp_path / "mcp-test"
        skill_dir.mkdir()
        (skill_dir / "scripts").mkdir()
        (skill_dir / "scripts" / "tool1.py").touch()
        (skill_dir / "scripts" / "tool2.py").touch()
        (skill_dir / "scripts" / "mcp_client.py").touch()

        mock_gen.generate_skill.return_value = skill_dir
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['generate', 'test-server', '-o', str(tmp_path)])

        assert result.exit_code == 0
        assert 'Generated skill' in result.output
        assert 'SKILL.md' in result.output

    @patch('mcp2skill.cli.SkillGenerator')
    def test_generate_no_server_name_no_all(self, mock_gen_class):
        """Test generate without server name and without --all flag."""
        mock_gen = Mock()
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['generate'])

        assert result.exit_code == 1
        assert 'Must specify SERVER_NAME or use --all' in result.output

    @patch('mcp2skill.cli.SkillGenerator')
    def test_generate_both_server_and_all(self, mock_gen_class):
        """Test generate with both server name and --all flag."""
        mock_gen = Mock()
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['generate', 'test', '--all'])

        assert result.exit_code == 1
        assert 'Cannot use SERVER_NAME and --all together' in result.output

    @patch('mcp2skill.cli.SkillGenerator')
    def test_generate_server_not_found(self, mock_gen_class):
        """Test generate with non-existent server."""
        mock_gen = Mock()
        mock_gen.generate_skill.side_effect = ValueError("Server not found")
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['generate', 'nonexistent'])

        assert result.exit_code == 1
        assert 'Error' in result.output

    @patch('mcp2skill.cli.SkillGenerator')
    def test_generate_all_success(self, mock_gen_class, tmp_path):
        """Test generate --all command."""
        mock_gen = Mock()
        skill_dirs = [
            tmp_path / "mcp-server1",
            tmp_path / "mcp-server2"
        ]
        for d in skill_dirs:
            d.mkdir()

        mock_gen.generate_all_skills.return_value = skill_dirs
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['generate', '--all'])

        assert result.exit_code == 0
        assert 'Generated 2 skill(s)' in result.output

    @patch('mcp2skill.cli.SkillGenerator')
    def test_generate_all_no_servers(self, mock_gen_class):
        """Test generate --all with no servers."""
        mock_gen = Mock()
        mock_gen.generate_all_skills.return_value = []
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['generate', '--all'])

        assert result.exit_code == 1
        assert 'No connected servers' in result.output

    @patch('mcp2skill.cli.SkillGenerator')
    def test_generate_custom_endpoint(self, mock_gen_class, tmp_path):
        """Test generate with custom endpoint."""
        mock_gen = Mock()
        skill_dir = tmp_path / "mcp-test"
        skill_dir.mkdir()
        (skill_dir / "scripts").mkdir()
        (skill_dir / "scripts" / "mcp_client.py").touch()

        mock_gen.generate_skill.return_value = skill_dir
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['generate', 'test', '--endpoint', 'http://custom:9000']
        )

        assert result.exit_code == 0
        mock_gen_class.assert_called_once_with('http://custom:9000')

    @patch('mcp2skill.cli.SkillGenerator')
    def test_generate_connection_error(self, mock_gen_class):
        """Test generate with connection error."""
        mock_gen = Mock()
        mock_gen.generate_skill.side_effect = ConnectionError("Cannot connect")
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['generate', 'test'])

        assert result.exit_code == 1
        assert 'Error' in result.output


class TestToolsCommand:
    """Test tools command."""

    @patch('mcp2skill.cli.SkillGenerator')
    def test_tools_success(self, mock_gen_class):
        """Test successful tools listing."""
        mock_gen = Mock()
        mock_gen.get_server_info.return_value = {"name": "test", "status": "connected"}
        mock_gen.get_tools.return_value = [
            {
                "name": "click",
                "description": "Click an element",
                "inputSchema": {
                    "required": ["selector"],
                    "properties": {
                        "selector": {"type": "string"},
                        "timeout": {"type": "integer"}
                    }
                }
            }
        ]
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['tools', 'test'])

        assert result.exit_code == 0
        assert 'click' in result.output
        assert 'Click an element' in result.output
        assert 'Required: selector' in result.output
        assert 'Optional: timeout' in result.output

    @patch('mcp2skill.cli.SkillGenerator')
    def test_tools_server_not_found(self, mock_gen_class):
        """Test tools command with non-existent server."""
        mock_gen = Mock()
        mock_gen.get_server_info.return_value = None
        mock_gen.list_servers.return_value = [{"name": "other"}]
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['tools', 'nonexistent'])

        assert result.exit_code == 1
        assert "Server 'nonexistent' not found" in result.output

    @patch('mcp2skill.cli.SkillGenerator')
    def test_tools_custom_endpoint(self, mock_gen_class):
        """Test tools command with custom endpoint."""
        mock_gen = Mock()
        mock_gen.get_server_info.return_value = {"name": "test"}
        mock_gen.get_tools.return_value = []
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['tools', 'test', '--endpoint', 'http://custom:7000']
        )

        assert result.exit_code == 0
        mock_gen_class.assert_called_once_with('http://custom:7000')

    @patch('mcp2skill.cli.SkillGenerator')
    def test_tools_connection_error(self, mock_gen_class):
        """Test tools command with connection error."""
        mock_gen = Mock()
        mock_gen.get_server_info.side_effect = ConnectionError("Cannot connect")
        mock_gen_class.return_value = mock_gen

        runner = CliRunner()
        result = runner.invoke(cli, ['tools', 'test'])

        assert result.exit_code == 1
        assert 'Error' in result.output
