from typing import Optional, List


class PromptDetector:
    """Detects different types of prompts in network device output."""

    def __init__(self) -> None:
        self.username_patterns: List[str] = ["Username:", "Login:"]
        self.password_patterns: List[str] = ["Password:", "password:"]
        self.learned_prompts: List[str] = []

    def detect_prompt(self, output: str) -> Optional[str]:
        """Detects the type of prompt in the given output.

        Args:
            output: The output string from the device to analyze

        Returns:
            Prompt type string ("username", "password", "cli") or None if no prompt detected
        """
        for pattern in self.username_patterns:
            if pattern in output:
                return "username"

        for pattern in self.password_patterns:
            if pattern in output:
                return "password"

        stripped_output = output.strip()
        if stripped_output.endswith("#") or stripped_output.endswith(">"):
            return "cli"

        for prompt in self.learned_prompts:
            if stripped_output.endswith(prompt):
                return "cli"

        return None

    def learn_prompt(self, prompt_suffix: str) -> None:
        """Learn a new prompt suffix for the current session.

        Args:
            prompt_suffix: The suffix pattern of the CLI prompt
        """
        if prompt_suffix not in self.learned_prompts:
            self.learned_prompts.append(prompt_suffix)

    @staticmethod
    def strip_echo(command: str, output: str) -> str:
        """Removes the command echo from the beginning of the output.

        Args:
            command: The command that was sent
            output: The output including possible echo

        Returns:
            Output with command echo removed
        """
        if not command:
            return output

        command_clean = command.rstrip("\n\r")

        if output.startswith(command_clean):
            return output[len(command_clean) :].lstrip("\n\r")

        if output.startswith(command_clean + "\r"):
            return output[len(command_clean) + 1 :].lstrip("\n\r")

        return output
