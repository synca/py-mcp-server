"""Base Tool class for MCP server tools."""

import asyncio
import pathlib
import traceback
from functools import cached_property
from typing import Any

from mcp.server.fastmcp import Context

ResultDict = dict[str, None | bool | str | dict[str, str | int | bool | dict]]


class Tool:
    """Base class for MCP server tools."""

    def __init__(self, ctx: Context, path: str) -> None:
        """Initialize the tool with context and path.
        """
        self.ctx = ctx
        self._path_str = path

    @property
    def config_args(self) -> tuple[str, ...]:
        return ()

    @cached_property
    def path(self) -> pathlib.Path:
        """Get the validated path as a pathlib.Path object."""
        path = pathlib.Path(self._path_str)
        self.validate_path(path)
        return path

    @property
    def tool_name(self) -> str:
        raise NotImplementedError

    @property
    def tool_path(self) -> str:
        return self.tool_name

    def command(
            self,
            args: list[str] | None = None) -> list[str]:
        """Build the tool command."""
        return [self.tool_path, *self.config_args, *(args or [])]

    async def execute(
            self,
            cmd: list[str]) -> tuple[str, str, int | None]:
        """Execute the tool command."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode(), process.returncode

    async def handle(
            self,
            args: list[str] | None = None) -> ResultDict:
        """Run tool on a Python project."""
        return self.result(
            *self.parse_output(
                *await self.execute(
                    self.command(args))))

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            returncode: int | None) -> tuple[int, str, dict]:
        """Parse the tool output."""
        raise NotImplementedError

    def result(
            self,
            issues_count: int,
            output: str,
            data: dict) -> ResultDict:
        """Format the final result."""
        return {
            "success": True,
            "data": {
                "message": (
                    f"Found {issues_count} issues for {self.tool_name}"),
                "output": output,
                "project_path": str(self.path),
                "issues_count": issues_count,
                "data": data,
            },
            "error": None}

    async def run(self, *args: Any, **kwargs: Any) -> ResultDict:
        """Run the tool and handle exceptions."""
        try:
            return await self.handle(*args, **kwargs)
        except BaseException as e:
            trace = traceback.format_exc()
            tool_name = self.__class__.__name__.lower().replace("tool", "")
            error_msg = f"Failed to run {tool_name}: {str(e)}\n{trace}"
            return {
                "success": False,
                "data": None,
                "error": error_msg}

    def validate_path(self, path: pathlib.Path) -> None:
        """Validate that the project path exists.
        """
        if not pathlib.Path(path).exists():
            raise FileNotFoundError(f"Path '{path}' does not exist")
