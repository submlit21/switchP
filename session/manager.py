"""Thread-safe session manager for network device console connections."""

import threading
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from session.connection import SerialConnection
from core.state_machine import DeviceSessionState
from session.parser import PromptDetector
from session.logger import SessionLogger
import config


@dataclass
class Session:
    """Represents a client session with all required components."""

    connection: SerialConnection
    state: DeviceSessionState
    username: Optional[str] = None
    password: Optional[str] = None
    prompt_detector: PromptDetector = field(default_factory=PromptDetector)
    logger: Optional[SessionLogger] = None
    stop_pattern: Optional[str] = None
    lock: threading.RLock = field(default_factory=threading.RLock)


class SessionManager:
    """Thread-safe manager for client sessions.

    Maintains one session per client ID, with per-session locking
    to serialize concurrent commands for the same session.
    """

    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._global_lock = threading.RLock()

    def create_session(self, client_id: str) -> Session:
        """Create a new session for the given client.

        Args:
            client_id: Unique identifier for the client.

        Returns:
            Session object with initialized components.
        """
        with self._global_lock:
            if client_id in self._sessions:
                return self._sessions[client_id]
            connection = SerialConnection()
            state = DeviceSessionState()
            session = Session(connection=connection, state=state)
            self._sessions[client_id] = session
            return session

    def get_session(self, client_id: str) -> Session:
        """Retrieve an existing session for the given client.

        Args:
            client_id: Unique identifier for the client.

        Returns:
            Session object.

        Raises:
            KeyError: If no session exists for this client.
        """
        with self._global_lock:
            return self._sessions[client_id]

    def close_session(self, client_id: str) -> None:
        """Close and remove the session for the given client.

        Args:
            client_id: Unique identifier for the client.
        """
        with self._global_lock:
            session = self._sessions.pop(client_id, None)
            if session:
                session.connection.close()

    def with_session_lock(self, client_id: str, func: Callable[[Session], Any]) -> Any:
        """Execute a function with the session's lock held.

        This ensures commands for the same session are executed sequentially.
        The function receives the session object as its argument.

        Args:
            client_id: Client identifier.
            func: Function to execute with session lock.

        Returns:
            The result of func(session).
        """
        session = self.get_session(client_id)
        with session.lock:
            return func(session)

