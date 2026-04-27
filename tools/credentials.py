"""Credential management tools for network device authentication."""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any

from session import get_session_manager
from .utils import format_response


# Global session manager instance (shared singleton)
_session_manager = get_session_manager()


def register_tools(mcp: FastMCP) -> None:
    """Register all credential management tools with the MCP server."""

    @mcp.tool()
    def set_credentials(
        username: str, password: str, client_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Store authentication credentials for the specified session.

        Stores username and password in the session state for subsequent
        authentication during device login sequences.

        Args:
            username: Device login username
            password: Device login password
            client_id: Client identifier for multi-session support (default: "default")

        Returns:
            JSON response indicating success or failure with message
        """
        try:
            session = _session_manager.create_session(client_id)

            def update_credentials(sess):
                sess.username = username
                sess.password = password
                sess.state.set_credentials(username, password)

            _session_manager.with_session_lock(client_id, update_credentials)

            return format_response(
                success=True,
                output="",
                message=f"Credentials stored successfully for client_id: {client_id}",
            )

        except Exception as e:
            return format_response(
                success=False,
                output="",
                message=f"Failed to store credentials: {str(e)}",
            )
