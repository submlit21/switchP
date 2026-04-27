"""Session management package for network device connections."""

from .manager import SessionManager, Session
from .connection import SerialConnection
from .logger import SessionLogger
from .parser import PromptDetector

# Shared singleton for multi-tool session management
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the shared SessionManager singleton.

    Returns:
        The global SessionManager instance shared across all tools.
    """
    return _session_manager


__all__ = [
    "SessionManager",
    "Session",
    "SerialConnection",
    "SessionLogger",
    "PromptDetector",
    "get_session_manager",
]
