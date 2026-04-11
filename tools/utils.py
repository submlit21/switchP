"""JSON response formatting utilities for consistent tool responses."""

from typing import Optional, Dict, Any


def format_response(
    success: bool,
    output: Optional[str] = None,
    message: Optional[str] = None,
    action: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Format a tool response into consistent JSON structure.

    All MCP tool responses must follow this format to ensure consistency.

    Args:
        success: Whether the operation succeeded
        output: Result/output data if succeeded (optional)
        message: Error/information message if failed or needs confirmation (optional)
        action: Required action from the caller: blocked, confirmation_required, completed, error (optional)
        **kwargs: Additional fields to include in the response

    Returns:
        Consistent JSON-structured dictionary with all fields
    """
    response = {
        "success": success,
        "output": output,
        "message": message,
        "action": action,
    }
    # Add any additional fields provided by the caller
    response.update(kwargs)
    return response
