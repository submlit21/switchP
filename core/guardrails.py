from enum import Enum
from typing import Tuple, Optional


class CommandRiskLevel(Enum):
    SAFE = 1
    CONFIRMATION_REQUIRED = 2
    BLOCKED = 3


class Guardrails:
    """
    2-tier command safety validation for network device commands
    """

    # Blocked commands that can cause severe impact to the device/configuration
    BLOCKED_COMMANDS = [
        "reload",
        "reboot",
        "format",
        "format flash:",
        "erase startup-config",
        "write erase",
        "delete flash:",
        "erase flash:",
        "factory-reset",
        "reset saved-configuration",
    ]

    # Commands that require confirmation before execution
    CONFIRMATION_COMMANDS = [
        "interface",
        "shutdown",
        "no shutdown",
        "ip address",
        "vlan",
        "route",
        "ip route",
        "access-list",
        "firewall",
        "nat",
        "security-policy",
    ]

    # Credential prompt patterns
    CREDENTIAL_PROMPTS = [
        "Username:",
        "Password:",
        "password:",
    ]

    def __init__(self):
        self._confirmed_command: Optional[str] = None

    def check_command(self, command: str) -> Tuple[bool, CommandRiskLevel, str]:
        """
        Check if a command is allowed based on risk assessment

        Args:
            command: The command string to check

        Returns:
            Tuple of (is_allowed, risk_level, message)
            - BLOCKED -> is_allowed=False, message explains blocking
            - CONFIRMATION_REQUIRED -> is_allowed=False, message asks for confirmation
            - SAFE -> is_allowed=True, empty message
        """
        # Clean input
        cleaned_command = command.strip().lower()

        # Check if this command was already confirmed
        if (
            self._confirmed_command is not None
            and cleaned_command == self._confirmed_command.lower()
        ):
            self._confirmed_command = None
            return (
                True,
                CommandRiskLevel.CONFIRMATION_REQUIRED,
                "Command confirmed, executing...",
            )

        # Check for blocked commands
        for blocked in self.BLOCKED_COMMANDS:
            blocked_lower = blocked.lower()
            if cleaned_command == blocked_lower or cleaned_command.startswith(
                blocked_lower
            ):
                return (
                    False,
                    CommandRiskLevel.BLOCKED,
                    f"Command '{blocked}' is blocked - this operation can cause severe configuration or device impact.",
                )

        # Check for confirmation required commands
        for confirm_required in self.CONFIRMATION_COMMANDS:
            confirm_lower = confirm_required.lower()
            if cleaned_command == confirm_lower or cleaned_command.startswith(
                confirm_lower + " "
            ):
                return (
                    False,
                    CommandRiskLevel.CONFIRMATION_REQUIRED,
                    f"Command '{confirm_required}' requires confirmation. Please confirm to execute this change.",
                )

        # If we get here, command is safe
        return (True, CommandRiskLevel.SAFE, "")

    def confirm_command(self, command: str) -> None:
        """
        Store confirmation for a risky command to allow execution

        Args:
            command: The command that was confirmed
        """
        self._confirmed_command = command.strip()

    def detect_credential_prompt(self, output: str) -> bool:
        """
        Check if the current output contains a credential prompt (username/password)

        Args:
            output: The output string to check

        Returns:
            True if credential prompt detected, False otherwise
        """
        for prompt in self.CREDENTIAL_PROMPTS:
            if prompt in output:
                return True
        return False
