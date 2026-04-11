"""Tool implementations for NetworkConsole MCP server."""

from .execute import register_tools as register_execute_tools
from .interactive import register_tools as register_interactive_tools
from .device import register_tools as register_device_tools

__all__ = [
    "register_execute_tools",
    "register_interactive_tools",
    "register_device_tools",
]
