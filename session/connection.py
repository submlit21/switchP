import serial
import time
import re
from typing import Optional, Pattern, cast

from config import config


class SerialConnection:
    """
    Persistent serial connection manager with auto-reconnect capability.
    Maintains an open connection between commands instead of opening/closing for each command.
    """

    def __init__(
        self,
        port: Optional[str] = None,
        baud_rate: Optional[int] = None,
        max_reconnect_attempts: int = 3,
        reconnect_backoff: float = 1.0,
    ):
        """
        Initialize SerialConnection with configuration.

        Args:
            port: Serial port path (defaults to config.port)
            baud_rate: Serial baud rate (defaults to config.baud_rate)
            max_reconnect_attempts: Maximum number of reconnect attempts on failure
            reconnect_backoff: Initial backoff in seconds between reconnect attempts (doubles each attempt)
        """
        self.port = port or config.port
        self.baud_rate = baud_rate or config.baud_rate
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_backoff = reconnect_backoff
        self._serial: Optional[serial.Serial] = None

    @property
    def is_open(self) -> bool:
        """Check if the serial connection is currently open."""
        return self._serial is not None and self._serial.is_open

    def open(self) -> None:
        """
        Open the serial connection.
        If connection fails, attempts auto-reconnect with backoff.

        Raises:
            serial.SerialException: If all connection attempts fail
        """
        if self.is_open:
            return

        attempts = 0
        current_backoff = self.reconnect_backoff
        last_exception = None

        while attempts < self.max_reconnect_attempts:
            try:
                self._serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baud_rate,
                    timeout=1,  # Base timeout, will be overridden by method-specific timeouts
                )
                # Clear buffers after opening
                self._serial.reset_input_buffer()
                self._serial.reset_output_buffer()
                return
            except serial.SerialException as e:
                last_exception = e
                attempts += 1
                if attempts < self.max_reconnect_attempts:
                    time.sleep(current_backoff)
                    current_backoff *= 2  # Exponential backoff

        # If we get here, all attempts failed
        if last_exception:
            raise last_exception
        else:
            raise serial.SerialException(
                f"Failed to connect to {self.port} after {self.max_reconnect_attempts} attempts"
            )

    def close(self) -> None:
        """Close the serial connection if it's open."""
        if self._serial is not None and self._serial.is_open:
            self._serial.close()
        self._serial = None

    def _ensure_connection(self) -> None:
        """
        Ensure connection is alive, attempt reconnect if it's not open.

        Raises:
            serial.SerialException: If connection is not open and reconnect fails
        """
        if not self.is_open:
            self.open()

    def send_command(self, command: str, timeout: int = 30) -> str:
        """
        Send a command and read the complete response.

        Args:
            command: The command to send to the device
            timeout: Maximum time to wait for response in seconds

        Returns:
            The response string from the device

        Raises:
            serial.SerialException: If connection issues occur
            TimeoutError: If no response received within timeout
        """
        self._ensure_connection()
        assert self._serial is not None, (
            "Serial connection should be open after _ensure_connection"
        )
        # Assign to local variable for type safety
        serial_port = cast(serial.Serial, self._serial)

        try:
            # Set the requested timeout
            original_timeout = serial_port.timeout
            serial_port.timeout = timeout

            # Clear input buffer to remove any stale data
            serial_port.reset_input_buffer()

            # Send command with newline
            serial_port.write(f"{command}\n".encode("utf-8"))
            serial_port.flush()

            # Read all available response
            data = serial_port.read_all()
            if data is None:
                response = ""
            else:
                response = data.decode("utf-8", errors="replace")

            # Restore original timeout
            serial_port.timeout = original_timeout

            return (
                response
                if response
                else f"Command '{command}' sent, but no response received."
            )

        except serial.SerialException:
            # Connection dropped, close and let reconnect handle it next time
            self.close()
            raise

    def read_until_prompt(self, prompt_pattern: str, timeout: int = 30) -> str:
        """
        Read data from serial port until the prompt pattern matches.
        Useful for interactive sessions where you need to read until a CLI prompt.

        Args:
            prompt_pattern: Regular expression pattern to match the prompt
            timeout: Maximum time to wait for prompt in seconds

        Returns:
            The collected data up to and including the prompt

        Raises:
            serial.SerialException: If connection issues occur
            TimeoutError: If timeout reached before prompt matched
        """
        self._ensure_connection()
        assert self._serial is not None, (
            "Serial connection should be open after _ensure_connection"
        )
        # Assign to local variable for type safety
        serial_port = cast(serial.Serial, self._serial)

        try:
            # Compile the regex pattern
            pattern: Pattern = re.compile(prompt_pattern)
            collected = []
            start_time = time.time()
            original_timeout = serial_port.timeout
            serial_port.timeout = 0.1  # Read in small chunks with short timeout

            while time.time() - start_time < timeout:
                if serial_port.in_waiting > 0:
                    chunk = serial_port.read(serial_port.in_waiting).decode(
                        "utf-8", errors="replace"
                    )
                    collected.append(chunk)

                    # Check if we've found the prompt
                    full_response = "".join(collected)
                    if pattern.search(full_response):
                        serial_port.timeout = original_timeout
                        return full_response
                else:
                    # Small sleep to reduce CPU usage
                    time.sleep(0.01)

            # If we get here, timeout occurred
            serial_port.timeout = original_timeout
            full_response = "".join(collected)
            raise TimeoutError(
                f"Timeout waiting {timeout}s for prompt pattern '{prompt_pattern}'. "
                f"Collected {len(full_response)} bytes:\n{full_response}"
            )

        except serial.SerialException:
            # Connection dropped, close and let reconnect handle it next time
            self.close()
            raise
