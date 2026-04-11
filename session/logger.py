import datetime
import os
import re
from typing import Optional


class SessionLogger:
    """Logger for network device console sessions.

    Creates a separate log file per session with automatic credential redaction.
    Logs are flushed after each write for immediate debugging availability.
    """

    # Common patterns for credential prompts and inputs
    CREDENTIAL_PATTERNS = [
        # Username input patterns
        r"(username|Username|login|Login)\s*[:=]\s*(\w+)",
        # Password input patterns
        r"(password|Password|passwd|Passwd)\s*[:=]\s*(\S+)",
        # Enable password patterns
        r"(enable|enable password|secret)\s*[:=]\s*(\S+)",
        # Login prompts with actual credentials
        r"(Password:|Username:)\s*(\S+)",
    ]

    def __init__(self, client_id: str, session_id: str, log_dir: str = "logs"):
        """Initialize a new session logger.

        Args:
            client_id: Identifier for the connected client
            session_id: Unique identifier for this session
            log_dir: Directory to store log files (default: logs)
        """
        self.client_id = client_id
        self.session_id = session_id
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Generate log file name according to pattern: {client_id}_{timestamp}_{session_id}.log
        log_filename = f"{client_id}_{self.timestamp}_{session_id}.log"
        self.log_path = os.path.join(log_dir, log_filename)

        # Open log file for writing
        self.file = open(self.log_path, "a", encoding="utf-8")

        # Write session header
        self._write_header()

    def _write_header(self) -> None:
        """Write session start header to log."""
        start_msg = f"=== Session Started ===\nClient ID: {self.client_id}\nSession ID: {self.session_id}\nStarted at: {self.timestamp}\n\n"
        self.file.write(start_msg)
        self.file.flush()

    def _redact(self, text: str) -> str:
        """Redact credential values from text before logging.

        Replaces any detected password or username values with ***.
        """
        redacted_text = text
        for pattern in self.CREDENTIAL_PATTERNS:
            redacted_text = re.sub(
                pattern, r"\1: ***", redacted_text, flags=re.IGNORECASE
            )
        return redacted_text

    def log_command(self, command: str) -> None:
        """Log a command sent to the device after redaction.

        Args:
            command: The command string to log
        """
        redacted = self._redact(command)
        entry = f"[{datetime.datetime.now().isoformat()}] C: {redacted}\n"
        self.file.write(entry)
        self.file.flush()

    def log_response(self, response: str) -> None:
        """Log a response received from the device after redaction.

        Args:
            response: The response string to log
        """
        redacted = self._redact(response)
        entry = f"[{datetime.datetime.now().isoformat()}] R: {redacted}\n"
        self.file.write(entry)
        self.file.flush()

    def close(self) -> None:
        """Close the log file."""
        if not self.file.closed:
            end_msg = f"\n=== Session Ended ===\nEnded at: {datetime.datetime.now().isoformat()}\n"
            self.file.write(end_msg)
            self.file.flush()
            self.file.close()
