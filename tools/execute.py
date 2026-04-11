"""execute_command MCP tool implementation with session-awareness and guardrails."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from session.manager import SessionManager, Session
from core.guardrails import Guardrails, CommandRiskLevel
from session.logger import SessionLogger
from .utils import format_response
import uuid

# Global instances - initialized once when registering tools
_session_manager: Optional[SessionManager] = None
_guardrails: Optional[Guardrails] = None


def register_tools(mcp: FastMCP) -> None:
    """Register the execute_command tool with the MCP server.

    Args:
        mcp: The MCP server instance to register with.
    """
    global _session_manager, _guardrails
    _session_manager = SessionManager()
    _guardrails = Guardrails()

    @mcp.tool()
    def execute_command(
        command: str, client_id: str = "default", confirm: Optional[bool] = False
    ) -> Dict[str, Any]:
        """Execute a command on the network device console with safety guardrails.

        Args:
            command: The command string to execute (e.g., 'show version', 'display interface brief')
            client_id: Optional client identifier for multi-session management (default: "default")
            confirm: Optional confirmation flag for commands that require approval (default: False)

        Returns:
            Structured JSON response with status, output/error message, and required action.
        """
        assert _session_manager is not None, "SessionManager not initialized"
        assert _guardrails is not None, "Guardrails not initialized"

        try:
            # Get or create session for this client
            session = _session_manager.create_session(client_id)

            # Initialize logger if not already created
            if session.logger is None:
                session_id = str(uuid.uuid4())[:8]
                session.logger = SessionLogger(client_id, session_id)
            # Type assertion - logger is guaranteed to exist now
            assert session.logger is not None, "Logger should be initialized"

            # Check command with guardrails
            is_allowed, risk_level, message = _guardrails.check_command(command)

            # Handle blocked commands
            if risk_level == CommandRiskLevel.BLOCKED:
                return format_response(
                    success=False,
                    output="",
                    message=message,
                    action="blocked",
                    command=command,
                )

            # Handle confirmation required
            if risk_level == CommandRiskLevel.CONFIRMATION_REQUIRED:
                if not confirm:
                    return format_response(
                        success=False,
                        output="",
                        message=message,
                        action="confirmation_required",
                        command=command,
                    )
                # If confirmed, mark as allowed and proceed
                _guardrails.confirm_command(command)

            # Execute command with session lock to ensure sequential execution
            def execute_with_lock(sess: Session) -> Dict[str, Any]:
                # Send command and get initial response
                response = sess.connection.send_command(command)
                all_responses = [response]

                # Handle credential prompts automatically
                max_prompt_attempts = 3  # username, password, maybe enable
                prompt_attempts = 0

                while prompt_attempts < max_prompt_attempts:
                    prompt_type = sess.prompt_detector.detect_prompt(response)
                    if prompt_type == "username" and sess.username:
                        # Send username
                        cred_response = sess.connection.send_command(sess.username)
                        all_responses.append(cred_response)
                        response = cred_response
                        prompt_attempts += 1
                        continue
                    elif prompt_type == "password" and sess.password:
                        # Send password
                        cred_response = sess.connection.send_command(sess.password)
                        all_responses.append(cred_response)
                        response = cred_response
                        prompt_attempts += 1
                        continue
                    else:
                        # No credential prompt or credentials not available
                        break

                # Combine all responses
                final_output = "".join(all_responses)

                # Update session state with last output
                sess.state.update_last_output(final_output)

                # Log command and response (credentials redacted by logger)
                assert sess.logger is not None
                sess.logger.log_command(command)
                sess.logger.log_response(final_output)

                return format_response(
                    success=True,
                    output=final_output,
                    message="",
                    action="completed",
                    command=command,
                )

            return _session_manager.with_session_lock(client_id, execute_with_lock)

        except KeyError:
            error_msg = f"No session found for client_id '{client_id}'. Please initialize the connection first."
            return format_response(
                success=False,
                output="",
                message=error_msg,
                action="error",
                client_id=client_id,
            )
        except Exception as e:
            return format_response(
                success=False,
                output="",
                message=f"Execution failed: {str(e)}",
                action="error",
            )
