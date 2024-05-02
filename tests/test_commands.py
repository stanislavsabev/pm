from unittest import mock

import pytest

from pm import commands


class TestOpen:
    @pytest.mark.parametrize(
        "proj_name, worktree",
        [
            ("proj-name", "branch-name"),
            ("proj-name", None),
        ],
    )
    @mock.patch("subprocess.Popen")
    @mock.patch("pm.utils.get_proj_path")
    @mock.patch("pm.models.Proj")
    @mock.patch("pm.proj_manager.ProjManager.find_proj")
    @mock.patch("pm.config.get_editor", return_value="ed")
    def test_run(
        self,
        get_editor_mock,
        find_proj_mock,
        proj_mock,
        path_mock,
        popen_mock,
        proj_name,
        worktree,
    ):
        # Setup
        positional = list(filter(None, [proj_name, worktree]))
        tmp_path = "tmp_path"
        proj_mock.path = tmp_path
        proj_mock.name = proj_name
        fake_proj_path = "/".join([tmp_path] + positional)
        path_mock.return_value = fake_proj_path
        find_proj_mock.return_value = proj_mock
        cmd_mock = mock.Mock()
        cmd_mock.communicate.return_value = "out", None
        popen_mock.return_value = cmd_mock

        cmd = commands.Open()
        cmd.positional = positional

        # Test
        cmd.run()

        # Validate
        assert find_proj_mock.called_with(proj_name)
        assert get_editor_mock.called
        assert cmd_mock.communicate.called
        assert popen_mock.called_with(f"ed {fake_proj_path}", shell=True)
