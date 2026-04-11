from enum import Enum
from typing import Optional, Dict, Set


class DeviceState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    CONFIGURING = "configuring"
    ERROR = "error"


class DeviceSessionState:
    """Device conversation state machine with transition validation"""

    # Allowed transitions: current state -> set of allowed next states
    _allowed_transitions: Dict[DeviceState, Set[DeviceState]] = {
        DeviceState.DISCONNECTED: {DeviceState.CONNECTING},
        DeviceState.CONNECTING: {DeviceState.AUTHENTICATING, DeviceState.ERROR},
        DeviceState.AUTHENTICATING: {DeviceState.AUTHENTICATED, DeviceState.ERROR},
        DeviceState.AUTHENTICATED: {DeviceState.CONFIGURING, DeviceState.ERROR},
        DeviceState.CONFIGURING: {DeviceState.AUTHENTICATED, DeviceState.ERROR},
        DeviceState.ERROR: {DeviceState.DISCONNECTED},
    }

    def __init__(self):
        self._current_state: DeviceState = DeviceState.DISCONNECTED
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._prompt_patterns: Dict[str, str] = {}
        self._last_output: Optional[str] = None

    @property
    def current_state(self) -> DeviceState:
        return self._current_state

    @property
    def username(self) -> Optional[str]:
        return self._username

    @property
    def password(self) -> Optional[str]:
        return self._password

    @property
    def prompt_patterns(self) -> Dict[str, str]:
        return self._prompt_patterns.copy()

    @property
    def last_output(self) -> Optional[str]:
        return self._last_output

    def set_credentials(self, username: str, password: str) -> None:
        """Set credentials for authentication"""
        self._username = username
        self._password = password

    def set_prompt_pattern(self, name: str, pattern: str) -> None:
        """Store a detected prompt pattern"""
        self._prompt_patterns[name] = pattern

    def update_last_output(self, output: str) -> None:
        """Update the last command output from device"""
        self._last_output = output

    def can_transition(self, new_state: DeviceState) -> bool:
        """Check if transition from current to new state is allowed"""
        # Any state can transition to ERROR
        if new_state == DeviceState.ERROR:
            return True

        allowed = self._allowed_transitions.get(self._current_state, set())
        return new_state in allowed

    def transition(self, new_state: DeviceState) -> bool:
        """
        Attempt to transition to new state.
        Returns True if transition is allowed and successful, False otherwise.
        """
        if not self.can_transition(new_state):
            return False

        self._current_state = new_state
        return True

    def is_authenticated(self) -> bool:
        """Check if device is in authenticated state"""
        return self._current_state == DeviceState.AUTHENTICATED

    def in_error(self) -> bool:
        """Check if device is in error state"""
        return self._current_state == DeviceState.ERROR
