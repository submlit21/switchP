"""Device information and connection check MCP tool implementation."""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Dict, Any, Tuple
from mcp.server.fastmcp import FastMCP
from session.manager import SessionManager, Session
from session.connection import SerialConnection
from config import config
from .utils import format_response

# Global instances - initialized once when registering tools
_session_manager: Optional[SessionManager] = None


def register_tools(mcp: FastMCP) -> None:
    """Register device-related tools with the MCP server.

    Args:
        mcp: The MCP server instance to register with.
    """
    global _session_manager
    _session_manager = SessionManager()

    @mcp.tool()
    def check_connection(
        port: Optional[str] = None,
        baud_rate: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Check if the configured serial port is accessible and connection is working.

        Args:
            port: Optional serial port path to check (defaults to configured port)
            baud_rate: Optional baud rate to use (defaults to configured baud rate)

        Returns:
            Structured JSON response with connection status and details.
        """
        check_port = port or config.port
        check_baud = baud_rate or config.baud_rate

        try:
            # Try to open the serial port to verify it's accessible
            connection = SerialConnection(port=check_port, baud_rate=check_baud)
            connection.open()
            connection.close()

            return format_response(
                success=True,
                connected=True,
                port=check_port,
                baud_rate=check_baud,
                message=f"Connection successful: port {check_port} is accessible with baud rate {check_baud}",
                error=None,
            )

        except FileNotFoundError:
            return format_response(
                success=False,
                connected=False,
                port=check_port,
                baud_rate=check_baud,
                message=f"Device not found: {check_port} does not exist. Please check the console cable connection.",
                error="FileNotFoundError",
            )

        except PermissionError:
            return format_response(
                success=False,
                connected=False,
                port=check_port,
                baud_rate=check_baud,
                message=f"Permission denied: cannot access {check_port}. Try executing 'sudo chmod 666 {check_port}'.",
                error="PermissionError",
            )

        except Exception as e:
            return format_response(
                success=False,
                connected=False,
                port=check_port,
                baud_rate=check_baud,
                message=f"Connection failed: {str(e)}",
                error=type(e).__name__,
            )

    @mcp.tool()
    def get_device_info(
        client_id: str = "default",
        command: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get device information by executing version command and parsing the output.

        Automatically tries common version commands: 'show version' (Cisco/Huawei) and 'display version' (Huawei).

        Args:
            client_id: Optional client identifier for session management (default: "default")
            command: Optional custom version command to use instead of auto-detection

        Returns:
            Structured JSON response with parsed device information including vendor, model, version.
        """
        assert _session_manager is not None, "SessionManager not initialized"

        # List of common version commands to try if none provided
        version_commands = (
            command
            and [command]
            or [
                "show version",
                "display version",
                "show version verbose",
                "display version brief",
            ]
        )

        try:
            # Get or create session for this client
            session = _session_manager.create_session(client_id)

            def get_info_with_lock(sess: Session) -> Dict[str, Any]:
                last_error = None
                raw_output = ""
                success = False

                # Try each version command until one succeeds
                for cmd in version_commands:
                    try:
                        output = sess.connection.send_command(cmd)
                        raw_output = output

                        if (
                            output
                            and "error" not in output.lower()
                            and "% invalid" not in output
                        ):
                            success = True
                            break
                        last_error = output
                    except Exception as e:
                        last_error = str(e)
                        continue

                if not success:
                    return format_response(
                        success=False,
                        vendor=None,
                        model=None,
                        version=None,
                        serial_number=None,
                        raw_output=raw_output,
                        message=f"All version commands failed. Last error: {last_error}",
                        tried_commands=version_commands,
                    )

                # Parse the output to extract device information
                parsed = parse_device_info(raw_output)

                return format_response(
                    success=True,
                    vendor=parsed.get("vendor"),
                    model=parsed.get("model"),
                    version=parsed.get("version"),
                    serial_number=parsed.get("serial_number"),
                    uptime=parsed.get("uptime"),
                    raw_output=raw_output,
                    message="Device information retrieved successfully",
                )

            return _session_manager.with_session_lock(client_id, get_info_with_lock)

        except KeyError:
            error_msg = f"No session found for client_id '{client_id}'. Please initialize the connection first."
            return format_response(
                success=False,
                vendor=None,
                model=None,
                version=None,
                serial_number=None,
                raw_output="",
                message=error_msg,
            )
        except Exception as e:
            return format_response(
                success=False,
                vendor=None,
                model=None,
                version=None,
                serial_number=None,
                raw_output="",
                message=f"Failed to get device info: {str(e)}",
            )


def parse_device_info(output: str) -> Dict[str, Optional[str]]:
    """Parse device version output to extract key information.

    Uses common regex patterns to detect vendor, model, version, and serial number.
    Works with Cisco, Huawei, and other common network devices.

    Args:
        output: Raw output from the version command

    Returns:
        Dictionary containing parsed device information
    """
    result: Dict[str, Optional[str]] = {
        "vendor": None,
        "model": None,
        "version": None,
        "serial_number": None,
        "uptime": None,
    }

    # Detect vendor based on output content
    vendor_patterns = [
        (r"Cisco IOS", "Cisco"),
        (r"Cisco (?:Systems|Nexus| Catalyst)", "Cisco"),
        (r"Huawei|Versatile Routing Platform", "Huawei"),
        (r"H3C|Comware", "H3C"),
        (r"Juniper|Junos", "Juniper"),
        (r"Aruba|ArubaOS", "Aruba"),
    ]

    for pattern, vendor in vendor_patterns:
        if re.search(pattern, output, re.IGNORECASE):
            result["vendor"] = vendor
            break

    # Extract version information
    version_patterns = [
        r"Version\s+([^\s]+)",
        r"Version\s+(.+?)\s*\n",
        r"Software.*Version\s+([^\s]+)",
        r"System Version\s+(.+?)\s*\n",
        r"Release\s+([^\s]+)",
    ]

    for pattern in version_patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            result["version"] = match.group(1).strip()
            break

    # Extract model information
    model_patterns = [
        r"(Cisco\s+(?:Catalyst|Nexus|ISR|ASR)\s+[^\s]+)",
        r"Model\s+(.+?)\s*\n",
        r"Hardware:\s+(.+?)\s*,",
        r"Chassis\s+:\s+(.+?)\s*\n",
        r"Device Model:\s+(.+?)\s*\n",
    ]

    for pattern in model_patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            result["model"] = match.group(1).strip()
            break

    # Extract serial number
    serial_patterns = [
        r"Serial Number\s*:\s*([^\s]+)",
        r"System Serial.*:\s*(.+?)\s*\n",
        r"Chassis Serial.*:\s*(.+?)\s*\n",
        r"Serial#\s*:\s*([^\s]+)",
    ]

    for pattern in serial_patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            result["serial_number"] = match.group(1).strip()
            break

    # Extract uptime
    uptime_patterns = [
        r"uptime is\s*(.+?)\s*\n",
        r"System uptime:\s*(.+?)\s*\n",
        r"uptime:\s*(.+?)\s*\n",
    ]

    for pattern in uptime_patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            result["uptime"] = match.group(1).strip()
            break

    return result
