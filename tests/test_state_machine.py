"""Tests for DeviceSessionState machine."""

import pytest
from core.state_machine import DeviceSessionState, DeviceState


class TestDeviceSessionState:
    """Tests for device session state transitions."""

    def test_initial_state_is_disconnected(self):
        """Test that new session starts in disconnected state."""
        state = DeviceSessionState()
        assert state.current_state == DeviceState.DISCONNECTED
        assert not state.is_authenticated()
        assert not state.in_error()

    def test_disconnected_to_connecting_is_allowed(self):
        """Test that disconnected can transition to connecting."""
        state = DeviceSessionState()
        assert state.can_transition(DeviceState.CONNECTING) is True
        result = state.transition(DeviceState.CONNECTING)
        assert result is True
        assert state.current_state == DeviceState.CONNECTING

    def test_disconnected_to_authenticated_is_rejected(self):
        """Test that disconnected cannot transition directly to authenticated."""
        state = DeviceSessionState()
        assert state.can_transition(DeviceState.AUTHENTICATED) is False
        result = state.transition(DeviceState.AUTHENTICATED)
        assert result is False
        assert state.current_state == DeviceState.DISCONNECTED

    def test_any_state_can_transition_to_error(self):
        """Test that any state can transition to error at any time."""
        state = DeviceSessionState()
        state.transition(DeviceState.CONNECTING)

        assert state.can_transition(DeviceState.ERROR) is True
        result = state.transition(DeviceState.ERROR)
        assert result is True
        assert state.in_error() is True
        assert state.current_state == DeviceState.ERROR

    def test_error_can_transition_back_to_disconnected(self):
        """Test that error can transition back to disconnected."""
        state = DeviceSessionState()
        state.transition(DeviceState.ERROR)

        assert state.can_transition(DeviceState.DISCONNECTED) is True
        result = state.transition(DeviceState.DISCONNECTED)
        assert result is True
        assert state.current_state == DeviceState.DISCONNECTED

    def test_normal_flow_works_correctly(self):
        """Test the normal authentication flow."""
        state = DeviceSessionState()

        # Start: DISCONNECTED -> CONNECTING
        assert state.transition(DeviceState.CONNECTING) is True

        # CONNECTING -> AUTHENTICATING
        assert state.transition(DeviceState.AUTHENTICATING) is True

        # AUTHENTICATING -> AUTHENTICATED
        assert state.transition(DeviceState.AUTHENTICATED) is True

        assert state.is_authenticated() is True

        # AUTHENTICATED -> CONFIGURING
        assert state.transition(DeviceState.CONFIGURING) is True

        # CONFIGURING -> AUTHENTICATED
        assert state.transition(DeviceState.AUTHENTICATED) is True

        assert state.current_state == DeviceState.AUTHENTICATED

    def test_set_credentials_stores_correctly(self):
        """Test that credentials are stored correctly."""
        state = DeviceSessionState()
        state.set_credentials("admin", "password123")
        assert state.username == "admin"
        assert state.password == "password123"

    def test_prompt_patterns_stored_correctly(self):
        """Test that prompt patterns are stored and returned."""
        state = DeviceSessionState()
        state.set_prompt_pattern("username", "Username:")
        state.set_prompt_pattern("password", "Password:")

        patterns = state.prompt_patterns
        assert patterns["username"] == "Username:"
        assert patterns["password"] == "Password:"
        # Check that it's a copy
        patterns["new"] = "pattern"
        assert "new" not in state.prompt_patterns

    def test_last_output_updated_correctly(self):
        """Test that last output is stored correctly."""
        state = DeviceSessionState()
        output = "System is starting up..."
        state.update_last_output(output)
        assert state.last_output == output
