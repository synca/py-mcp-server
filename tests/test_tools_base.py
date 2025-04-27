"""Isolated tests for snake.mcp.server.tools.base."""

import pytest
from unittest.mock import AsyncMock, MagicMock, PropertyMock

from snake.mcp.server.tools.base import Tool


def test_tools_base_constructor():
    """Test Tool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = Tool(ctx, path)
    assert isinstance(tool, Tool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    with pytest.raises(NotImplementedError):
        tool.tool_name


def test_tools_base_path(patches):
    """Test Tool path."""
    ctx = MagicMock()
    path = MagicMock()
    tool = Tool(ctx, path)
    patched = patches(
        "pathlib",
        "Tool.validate_path",
        prefix="snake.mcp.server.tools.base")

    with patched as (m_path, m_valid):
        assert (
            tool.path
            == m_path.Path.return_value)

    assert (
        m_path.Path.call_args
        == [(path, ), {}])
    assert (
        m_valid.call_args
        == [(m_path.Path.return_value, ), {}])
    assert "path" in tool.__dict__


def test_tools_base_tool_path(patches):
    """Test Tool path."""
    ctx = MagicMock()
    path = MagicMock()
    tool = Tool(ctx, path)
    patched = patches(
        ("Tool.tool_name",
         dict(new_callable=PropertyMock)),
        prefix="snake.mcp.server.tools.base")

    with patched as (m_name, ):
        assert (
            tool.tool_path
            == m_name.return_value)


@pytest.mark.parametrize(
    "args",
    [None,
     [MagicMock()],
     [MagicMock(), MagicMock()]])
def test_tools_base_command(patches, args):
    """Test command with parametrized arguments."""
    path = "/test/path"
    ctx = MagicMock()
    path = MagicMock()
    tool = Tool(ctx, path)
    patched = patches(
        ("Tool.tool_path",
         dict(new_callable=PropertyMock)),
        prefix="snake.mcp.server.tools.base")

    with patched as (m_tool_path, ):
        assert (
            tool.command(args)
            == [m_tool_path.return_value, *(args or [])])

    assert "tool_path" not in tool.__dict__


@pytest.mark.asyncio
async def test_tools_base_execute(patches):
    """Test execute method."""
    cmd = (MagicMock(), MagicMock(), MagicMock())
    ctx = MagicMock()
    path = MagicMock()
    tool = Tool(ctx, path)
    stdout = MagicMock()
    stderr = MagicMock()
    patched = patches(
        "asyncio",
        "str",
        ("Tool.path",
         dict(new_callable=PropertyMock)),
        prefix="snake.mcp.server.tools.base")

    with patched as (m_aio, m_str, m_path):
        m_subproc = m_aio.create_subprocess_exec = AsyncMock()
        proc = m_subproc.return_value
        proc.communicate.return_value = (stdout, stderr)
        assert (
            await tool.execute(cmd)
            == (stdout.decode.return_value,
                stderr.decode.return_value,
                proc.returncode))

    assert (
        m_subproc.call_args
        == [cmd,
            dict(
                cwd=m_str.return_value,
                stdout=m_aio.subprocess.PIPE,
                stderr=m_aio.subprocess.PIPE)])
    assert (
        m_str.call_args
        == [(m_path.return_value, ), {}])


@pytest.mark.parametrize("args", [None, ["--ignore=E501"]])
@pytest.mark.asyncio
async def test_tools_base_handle(patches, args):
    """Test handle method with various parameters."""
    ctx = MagicMock()
    path = MagicMock()
    tool = Tool(ctx, path)
    patched = patches(
        "Tool.command",
        "Tool.execute",
        "Tool.parse_output",
        "Tool.result",
        prefix="snake.mcp.server.tools.base")

    with patched as (m_build, m_exec, m_parse, m_format):
        m_exec.return_value = (MagicMock(), MagicMock(), MagicMock())
        m_parse.return_value = (MagicMock(), MagicMock())
        assert (
            await tool.handle(args)
            == m_format.return_value)

    assert (
        m_build.call_args
        == [(args, ), {}])
    assert (
        m_exec.call_args
        == [(m_build.return_value, ), {}])
    assert (
        m_parse.call_args
        == [m_exec.return_value, {}])
    assert (
        m_format.call_args
        == [m_parse.return_value, {}])


def test_tools_base_parse_output(patches):
    """Test parse_output method."""
    ctx = MagicMock()
    path = MagicMock()
    tool = Tool(ctx, path)
    with pytest.raises(NotImplementedError):
        tool.parse_output(
            MagicMock(), MagicMock(), MagicMock())


@pytest.mark.parametrize("issues_count", [0, 1, 5])
def test_tools_base_result(patches, issues_count):
    """Test result method with parametrized inputs."""
    ctx = MagicMock()
    path = MagicMock()
    output = MagicMock()
    tool = Tool(ctx, path)
    data = MagicMock()
    patched = patches(
        "str",
        ("Tool.path",
         dict(new_callable=PropertyMock)),
        ("Tool.tool_name",
         dict(new_callable=PropertyMock)),
        prefix="snake.mcp.server.tools.base")

    with patched as (m_str, m_path, m_tool):
        assert (
            tool.result(issues_count, output, data)
            == {
                "success": True,
                "data": {
                    "message": (
                        f"Found {issues_count} issues "
                        f"for {m_tool.return_value}"),
                    "output": output,
                    "project_path": m_str.return_value,
                    "issues_count": issues_count,
                    "data": data,
                },
                "error": None})

    assert (
        m_str.call_args
        == [(m_path.return_value, ), {}])


@pytest.mark.parametrize("exists", [True, False])
def test_tools_base_validate_path(patches, exists):
    """Test validate_path method with parametrized path existence."""
    patched = patches(
        "pathlib.Path",
        prefix="snake.mcp.server.tools.base")
    ctx = MagicMock()
    path = MagicMock()
    tool = Tool(ctx, path)
    with patched as (m_path, ):
        m_path.return_value.exists.return_value = exists
        if not exists:
            with pytest.raises(FileNotFoundError) as e:
                tool.validate_path(path)
        else:
            assert not tool.validate_path(path)

    assert m_path.call_args == [(path,), {}]
    assert m_path.return_value.exists.called
    if not exists:
        assert (
            e.value.args[0]
            == f"Path '{path}' does not exist")


@pytest.mark.parametrize(
    "error",
    [None,
     BaseException])
@pytest.mark.parametrize(
    "args",
    [(MagicMock(),),
     (MagicMock(), MagicMock()),
     ()])
@pytest.mark.parametrize(
    "kwargs",
    [{"args": ["--check"], "verbose": False},
     {"verbose": True},
     {}])
@pytest.mark.asyncio
async def test_tools_base_run(patches, iters, args, kwargs, error):
    """Test run() with parametrized arguments."""
    ctx = MagicMock()
    path = MagicMock()
    tool = Tool(ctx, path)
    tool.__class__.__name__ = "CustomTool"
    patched = patches(
        "traceback",
        "Tool.handle",
        prefix="snake.mcp.server.tools.base")

    with patched as (m_tb, m_handle):
        if error:
            m_handle.side_effect = error("Test error")
        assert (
            await tool.run(*args, **kwargs)
            == (m_handle.return_value
                if not error
                else dict(
                    success=False,
                    data=None,
                    error=(
                        "Failed to run custom: Test error\n"
                        f"{m_tb.format_exc.return_value}"))))

    assert (
        m_handle.call_args
        == [args, kwargs])
    if error:
        assert (
            m_tb.format_exc.call_args
            == [(), {}])
        return
    assert not m_tb.format_exc.called
