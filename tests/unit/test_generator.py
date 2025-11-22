"""Tests for generator module."""

import pytest
import requests
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from mcp2skill.generator import SkillGenerator


class TestSkillGeneratorInit:
    """Test SkillGenerator initialization."""

    def test_init_default_url(self):
        """Test initialization with default URL."""
        gen = SkillGenerator()
        assert gen.base_url == "http://localhost:28888"

    def test_init_custom_url(self):
        """Test initialization with custom URL."""
        gen = SkillGenerator("http://192.168.1.100:5000")
        assert gen.base_url == "http://192.168.1.100:5000"

    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from URL."""
        gen = SkillGenerator("http://localhost:28888/")
        assert gen.base_url == "http://localhost:28888"

    def test_init_multiple_trailing_slashes(self):
        """Test that multiple trailing slashes are removed."""
        gen = SkillGenerator("http://localhost:28888///")
        assert gen.base_url == "http://localhost:28888"


class TestListServers:
    """Test list_servers method."""

    def test_list_servers_success(self, monkeypatch, mock_servers_response):
        """Test successful server listing."""
        mock_response = Mock()
        mock_response.json.return_value = mock_servers_response
        mock_response.raise_for_status = Mock()

        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr(requests, "get", mock_get)

        gen = SkillGenerator()
        servers = gen.list_servers()

        assert len(servers) == 3
        assert servers[0]["name"] == "chrome-devtools"
        assert servers[1]["name"] == "filesystem"
        mock_get.assert_called_once_with("http://localhost:28888/servers", timeout=10)

    def test_list_servers_empty(self, monkeypatch):
        """Test listing when no servers exist."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))

        gen = SkillGenerator()
        servers = gen.list_servers()

        assert servers == []

    def test_list_servers_connection_error(self, monkeypatch):
        """Test connection error handling."""
        def mock_get(*args, **kwargs):
            raise requests.exceptions.ConnectionError("Connection refused")

        monkeypatch.setattr(requests, "get", mock_get)

        gen = SkillGenerator()
        with pytest.raises(ConnectionError) as exc_info:
            gen.list_servers()

        assert "Cannot connect to mcp2rest" in str(exc_info.value)
        assert "http://localhost:28888" in str(exc_info.value)

    def test_list_servers_timeout(self, monkeypatch):
        """Test timeout error handling."""
        def mock_get(*args, **kwargs):
            raise requests.exceptions.Timeout("Request timed out")

        monkeypatch.setattr(requests, "get", mock_get)

        gen = SkillGenerator()
        with pytest.raises(ConnectionError) as exc_info:
            gen.list_servers()

        assert "Timeout connecting to mcp2rest" in str(exc_info.value)

    def test_list_servers_http_error(self, monkeypatch):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))

        gen = SkillGenerator()
        with pytest.raises(requests.exceptions.HTTPError):
            gen.list_servers()


class TestGetTools:
    """Test get_tools method."""

    def test_get_tools_success(self, monkeypatch, mock_tools_response, mock_servers_response):
        """Test successful tool retrieval."""
        def mock_get(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        monkeypatch.setattr(requests, "get", mock_get)

        gen = SkillGenerator()
        tools = gen.get_tools("chrome-devtools")

        assert len(tools) == 3
        assert tools[0]["name"] == "click"
        assert tools[1]["name"] == "search"

    def test_get_tools_empty(self, monkeypatch, mock_servers_response):
        """Test getting tools when none exist."""
        def mock_get(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = []
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        monkeypatch.setattr(requests, "get", mock_get)

        gen = SkillGenerator()
        tools = gen.get_tools("chrome-devtools")

        assert tools == []

    def test_get_tools_server_not_found(self, monkeypatch, mock_servers_response):
        """Test error when server not found."""
        def mock_get(url, **kwargs):
            if "/tools" in url:
                mock_response = Mock()
                mock_response.status_code = 404
                error = requests.exceptions.HTTPError("404 Not Found")
                error.response = mock_response
                mock_response.raise_for_status.side_effect = error
                return mock_response
            else:
                # list_servers call
                mock_response = Mock()
                mock_response.json.return_value = mock_servers_response
                mock_response.raise_for_status = Mock()
                return mock_response

        monkeypatch.setattr(requests, "get", mock_get)

        gen = SkillGenerator()
        with pytest.raises(ValueError) as exc_info:
            gen.get_tools("nonexistent-server")

        assert "Server 'nonexistent-server' not found" in str(exc_info.value)

    def test_get_tools_other_http_error(self, monkeypatch):
        """Test non-404 HTTP errors are raised."""
        mock_response = Mock()
        mock_response.status_code = 500
        error = requests.exceptions.HTTPError("500 Server Error")
        error.response = mock_response
        mock_response.raise_for_status.side_effect = error

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))

        gen = SkillGenerator()
        with pytest.raises(requests.exceptions.HTTPError):
            gen.get_tools("chrome-devtools")


class TestGetServerInfo:
    """Test get_server_info method."""

    def test_get_server_info_found(self, monkeypatch, mock_servers_response):
        """Test getting info for existing server."""
        mock_response = Mock()
        mock_response.json.return_value = mock_servers_response
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))

        gen = SkillGenerator()
        info = gen.get_server_info("chrome-devtools")

        assert info is not None
        assert info["name"] == "chrome-devtools"
        assert info["status"] == "connected"
        assert info["toolCount"] == 15

    def test_get_server_info_not_found(self, monkeypatch, mock_servers_response):
        """Test getting info for non-existent server."""
        mock_response = Mock()
        mock_response.json.return_value = mock_servers_response
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))

        gen = SkillGenerator()
        info = gen.get_server_info("nonexistent")

        assert info is None

    def test_get_server_info_multiple_servers(self, monkeypatch, mock_servers_response):
        """Test getting correct server from multiple servers."""
        mock_response = Mock()
        mock_response.json.return_value = mock_servers_response
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))

        gen = SkillGenerator()
        info = gen.get_server_info("filesystem")

        assert info is not None
        assert info["name"] == "filesystem"
        assert info["toolCount"] == 8


class TestGenerateSkill:
    """Test generate_skill method."""

    @patch('mcp2skill.generator.create_skill_md')
    @patch('mcp2skill.generator.create_mcp_client_script')
    @patch('mcp2skill.generator.create_tool_script')
    def test_generate_skill_success(
        self,
        mock_create_tool,
        mock_create_client,
        mock_create_md,
        monkeypatch,
        mock_servers_response,
        mock_tools_response,
        temp_skill_dir
    ):
        """Test successful skill generation."""
        def mock_get(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        monkeypatch.setattr(requests, "get", mock_get)

        mock_create_md.return_value = "# SKILL.md content"
        mock_create_client.return_value = "# mcp_client.py content"
        mock_create_tool.return_value = "#!/usr/bin/env python3\nprint('tool')"

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        # Verify skill directory created
        assert skill_dir.exists()
        assert skill_dir.is_dir()
        assert skill_dir.name == "mcp-chrome-devtools"

        # Verify SKILL.md created
        skill_md = skill_dir / "SKILL.md"
        assert skill_md.exists()
        assert skill_md.read_text() == "# SKILL.md content"

        # Verify scripts directory created
        scripts_dir = skill_dir / "scripts"
        assert scripts_dir.exists()
        assert scripts_dir.is_dir()

        # Verify mcp_client.py created
        mcp_client = scripts_dir / "mcp_client.py"
        assert mcp_client.exists()
        assert mcp_client.read_text() == "# mcp_client.py content"

        # Verify tool scripts created (3 tools in mock_tools_response)
        tool_scripts = list(scripts_dir.glob("*.py"))
        assert len(tool_scripts) == 4  # 3 tools + mcp_client.py

    def test_generate_skill_server_not_found(self, monkeypatch, mock_servers_response):
        """Test error when server doesn't exist."""
        mock_response = Mock()
        mock_response.json.return_value = mock_servers_response
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))

        gen = SkillGenerator()
        with pytest.raises(ValueError) as exc_info:
            gen.generate_skill("nonexistent", "/tmp")

        assert "Server 'nonexistent' not found" in str(exc_info.value)

    def test_generate_skill_no_tools(self, monkeypatch, mock_servers_response):
        """Test error when server has no tools."""
        def mock_get(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = []
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        monkeypatch.setattr(requests, "get", mock_get)

        gen = SkillGenerator()
        with pytest.raises(ValueError) as exc_info:
            gen.generate_skill("chrome-devtools", "/tmp")

        assert "has no tools available" in str(exc_info.value)

    @patch('mcp2skill.generator.create_skill_md')
    @patch('mcp2skill.generator.create_mcp_client_script')
    @patch('mcp2skill.generator.create_tool_script')
    def test_generate_skill_expands_user_path(
        self,
        mock_create_tool,
        mock_create_client,
        mock_create_md,
        monkeypatch,
        mock_servers_response,
        mock_tools_response,
        temp_skill_dir
    ):
        """Test that ~ in path is expanded."""
        def mock_get(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        monkeypatch.setattr(requests, "get", mock_get)
        mock_create_md.return_value = "content"
        mock_create_client.return_value = "content"
        mock_create_tool.return_value = "content"

        gen = SkillGenerator()

        # Use temp_skill_dir as the base
        with patch.object(Path, 'expanduser', return_value=temp_skill_dir):
            skill_dir = gen.generate_skill("chrome-devtools", "~/skills")

        assert skill_dir.exists()

    @patch('mcp2skill.generator.create_skill_md')
    @patch('mcp2skill.generator.create_mcp_client_script')
    @patch('mcp2skill.generator.create_tool_script')
    def test_generate_skill_sets_executable(
        self,
        mock_create_tool,
        mock_create_client,
        mock_create_md,
        monkeypatch,
        mock_servers_response,
        mock_tools_response,
        temp_skill_dir
    ):
        """Test that generated tool scripts are made executable."""
        def mock_get(url, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if "/tools" in url:
                mock_response.json.return_value = mock_tools_response
            else:
                mock_response.json.return_value = mock_servers_response

            return mock_response

        monkeypatch.setattr(requests, "get", mock_get)
        mock_create_md.return_value = "content"
        mock_create_client.return_value = "content"
        mock_create_tool.return_value = "#!/usr/bin/env python3\nprint('test')"

        gen = SkillGenerator()
        skill_dir = gen.generate_skill("chrome-devtools", temp_skill_dir)

        # Check that tool scripts are executable
        scripts_dir = skill_dir / "scripts"
        for script in scripts_dir.glob("*.py"):
            if script.name != "mcp_client.py":
                import stat
                st = script.stat()
                assert bool(st.st_mode & stat.S_IXUSR), f"{script} is not executable"


class TestGenerateAllSkills:
    """Test generate_all_skills method."""

    @patch('mcp2skill.generator.SkillGenerator.generate_skill')
    def test_generate_all_skills_success(
        self,
        mock_generate,
        monkeypatch,
        mock_servers_response,
        temp_skill_dir
    ):
        """Test generating skills for all connected servers."""
        mock_response = Mock()
        mock_response.json.return_value = mock_servers_response
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))

        mock_generate.return_value = temp_skill_dir / "mcp-test"

        gen = SkillGenerator()
        skill_dirs = gen.generate_all_skills(temp_skill_dir)

        # Should generate for 2 connected servers with tools (chrome-devtools, filesystem)
        # disconnected-server should be skipped
        assert len(skill_dirs) == 2
        assert mock_generate.call_count == 2

    @patch('mcp2skill.generator.SkillGenerator.generate_skill')
    def test_generate_all_skills_skips_disconnected(
        self,
        mock_generate,
        monkeypatch,
        temp_skill_dir
    ):
        """Test that disconnected servers are skipped."""
        servers = [
            {"name": "server1", "status": "connected", "toolCount": 5},
            {"name": "server2", "status": "disconnected", "toolCount": 3},
            {"name": "server3", "status": "connected", "toolCount": 2}
        ]

        mock_response = Mock()
        mock_response.json.return_value = servers
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))
        mock_generate.return_value = temp_skill_dir / "test"

        gen = SkillGenerator()
        skill_dirs = gen.generate_all_skills(temp_skill_dir)

        # Should only generate for 2 connected servers
        assert len(skill_dirs) == 2
        assert mock_generate.call_count == 2

    @patch('mcp2skill.generator.SkillGenerator.generate_skill')
    def test_generate_all_skills_skips_no_tools(
        self,
        mock_generate,
        monkeypatch,
        temp_skill_dir
    ):
        """Test that servers with no tools are skipped."""
        servers = [
            {"name": "server1", "status": "connected", "toolCount": 5},
            {"name": "server2", "status": "connected", "toolCount": 0},
            {"name": "server3", "status": "connected", "toolCount": 2}
        ]

        mock_response = Mock()
        mock_response.json.return_value = servers
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))
        mock_generate.return_value = temp_skill_dir / "test"

        gen = SkillGenerator()
        skill_dirs = gen.generate_all_skills(temp_skill_dir)

        # Should only generate for 2 servers with tools
        assert len(skill_dirs) == 2
        assert mock_generate.call_count == 2

    @patch('mcp2skill.generator.SkillGenerator.generate_skill')
    def test_generate_all_skills_handles_errors(
        self,
        mock_generate,
        monkeypatch,
        mock_servers_response,
        temp_skill_dir,
        capsys
    ):
        """Test that errors in individual skill generation are caught."""
        mock_response = Mock()
        mock_response.json.return_value = mock_servers_response
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))

        # First call succeeds, second fails
        mock_generate.side_effect = [
            temp_skill_dir / "skill1",
            ValueError("Test error")
        ]

        gen = SkillGenerator()
        skill_dirs = gen.generate_all_skills(temp_skill_dir)

        # Should return 1 successful generation
        assert len(skill_dirs) == 1

        # Check that warning was printed
        captured = capsys.readouterr()
        assert "Warning:" in captured.out
        assert "Test error" in captured.out

    def test_generate_all_skills_empty_servers(self, monkeypatch, temp_skill_dir):
        """Test generating when no servers exist."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr(requests, "get", Mock(return_value=mock_response))

        gen = SkillGenerator()
        skill_dirs = gen.generate_all_skills(temp_skill_dir)

        assert skill_dirs == []
