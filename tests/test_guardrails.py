"""Tests for command guardrails validation."""

import pytest
from core.guardrails import Guardrails, CommandRiskLevel


class TestGuardrails:
    """Tests for command guardrail validation."""

    def test_safe_command_returns_allowed(self):
        """Test that safe commands are allowed."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("show version")

        assert allowed is True
        assert level == CommandRiskLevel.SAFE
        assert msg == ""

    def test_blocked_command_reload_is_blocked(self):
        """Test that blocked command reload is correctly blocked."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("reload")

        assert allowed is False
        assert level == CommandRiskLevel.BLOCKED
        assert "blocked" in msg

    def test_blocked_command_write_erase_is_blocked(self):
        """Test that blocked command write erase is correctly blocked."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("write erase")

        assert allowed is False
        assert level == CommandRiskLevel.BLOCKED
        assert "blocked" in msg

    def test_blocked_command_with_argument_is_blocked(self):
        """Test that blocked commands with arguments are still blocked."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("delete flash:config.text")

        assert allowed is False
        assert level == CommandRiskLevel.BLOCKED

    def test_confirmation_required_command_shutdown_requires_confirm(self):
        """Test that confirmation required commands ask for confirmation."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("shutdown")

        assert allowed is False
        assert level == CommandRiskLevel.CONFIRMATION_REQUIRED
        assert "requires confirmation" in msg

    def test_confirmation_required_command_with_args_requires_confirm(self):
        """Test that confirmation required commands with arguments need confirmation."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("interface GigabitEthernet 0/1")

        assert allowed is False
        assert level == CommandRiskLevel.CONFIRMATION_REQUIRED
        assert "requires confirmation" in msg

    def test_confirmed_command_gets_allowed(self):
        """Test that once confirmed, a command is allowed to execute."""
        guard = Guardrails()

        # First check requires confirmation
        allowed, level, msg = guard.check_command("shutdown")
        assert allowed is False
        assert level == CommandRiskLevel.CONFIRMATION_REQUIRED

        # Confirm the command
        guard.confirm_command("shutdown")

        # Second check should allow it
        allowed_confirm, level_confirm, msg_confirm = guard.check_command("shutdown")
        assert allowed_confirm is True
        assert level_confirm == CommandRiskLevel.CONFIRMATION_REQUIRED
        assert "Command confirmed" in msg_confirm

    def test_detect_credential_prompt_username(self):
        """Test that username prompt is correctly detected."""
        guard = Guardrails()
        result = guard.detect_credential_prompt("Please enter your Username: ")
        assert result is True

    def test_detect_credential_prompt_password(self):
        """Test that password prompt is correctly detected."""
        guard = Guardrails()
        result = guard.detect_credential_prompt("Enter your password:")
        assert result is True

    def test_detect_no_credential_prompt_in_normal_output(self):
        """Test that normal output doesn't trigger credential detection."""
        guard = Guardrails()
        result = guard.detect_credential_prompt("System uptime is 10 days")
        assert result is False

    def test_case_insensitive_checking(self):
        """Test that command checking is case insensitive."""
        guard = Guardrails()
        allowed, level, _ = guard.check_command("RELOAD")

        assert allowed is False
        assert level == CommandRiskLevel.BLOCKED

    def test_empty_command_is_safe(self):
        """Test that empty command is considered safe (no blocking/confirmation)."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("")

        assert allowed is True
        assert level == CommandRiskLevel.SAFE

    def test_show_running_config_is_safe(self):
        """Test that show running-config is safe (doesn't contain confirmation keywords)."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("show running-config")

        assert allowed is True
        assert level == CommandRiskLevel.SAFE
        assert msg == ""

    def test_show_interfaces_is_safe(self):
        """Test that show interfaces is SAFE (not flagged by 'interface' substring match)."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("show interfaces")

        assert allowed is True
        assert level == CommandRiskLevel.SAFE

    def test_show_ip_route_is_safe(self):
        """Test that show ip route is SAFE (not flagged by 'route' substring match)."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("show ip route")

        assert allowed is True
        assert level == CommandRiskLevel.SAFE

    def test_traceroute_is_safe(self):
        """Test that traceroute is SAFE (not flagged by 'route' substring match)."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("traceroute 192.168.1.1")

        assert allowed is True
        assert level == CommandRiskLevel.SAFE

    def test_show_vlan_is_safe(self):
        """Test that show vlan is SAFE (not flagged by 'vlan' substring match)."""
        guard = Guardrails()
        allowed, level, msg = guard.check_command("show vlan")

        assert allowed is True
        assert level == CommandRiskLevel.SAFE
