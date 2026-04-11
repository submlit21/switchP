"""Interactive session management tools for NetworkConsole MCP server."""

import sys
import os
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session.manager import SessionManager, Session
from .utils import format_response

# Global singleton session manager instance
_session_manager = SessionManager()


def start_interactive_session(
    client_id: str = "default", stop_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """
    Start a new interactive session for a client.

    Creates a persistent serial connection session for the client and optionally
    sets a custom stop pattern for interactive command execution.

    Args:
        client_id: Unique identifier for the client (defaults to "default")
        stop_pattern: Optional custom regex pattern to detect end of command output

    Returns:
        JSON response with success status and session information
    """
    try:
        session = _session_manager.create_session(client_id)

        # Set custom stop pattern if provided
        if stop_pattern is not None:
            session.stop_pattern = stop_pattern

        return format_response(
            success=True,
            message="Interactive session started successfully",
            client_id=client_id,
            has_stop_pattern=stop_pattern is not None,
            stop_pattern=stop_pattern,
        )
    except Exception as e:
        return format_response(success=False, message=str(e), client_id=client_id)


def stop_interactive_session(client_id: str = "default") -> Dict[str, Any]:
    """
    Stop and close an existing interactive session for a client.

    Closes the serial connection and removes the session from management.

    Args:
        client_id: Unique identifier for the client (defaults to "default")

    Returns:
        JSON response with success status
    """
    try:
        _session_manager.close_session(client_id)
        return format_response(
            success=True,
            message="Interactive session stopped successfully",
            client_id=client_id,
        )
    except Exception as e:
        return format_response(success=False, message=str(e), client_id=client_id)


def register_tools(mcp: FastMCP) -> None:
    """Register all interactive session tools with the MCP server."""
    mcp.tool()(start_interactive_session)
    mcp.tool()(stop_interactive_session)
