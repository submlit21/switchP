# Execute Command Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `tools/execute.py` with session-aware `execute_command` that uses session manager and guardrails for safe command execution with proper logging.

**Architecture:** The tool will follow the modular architecture - it only handles MCP tool registration and input/output marshalling. All business logic is delegated to existing modules:
- SessionManager gets/creates the session for the client
- Guardrails validates command risk level
- SerialConnection executes the command on the serial port
- SessionLogger logs command and response with credential redaction

The tool returns structured JSON responses for different outcomes: blocked error, confirmation required, success with output, error with message.

**Tech Stack:** Python, MCP FastMCP, threading for session safety, existing serial connection management.

---

### Task 1: Create `tools/execute.py` with imports and basic structure

**Files:**
- Create: `tools/execute.py`

- [ ] **Step 1: Create the file with imports and basic structure**

```python
"""execute_command MCP tool implementation with session-awareness and guardrails."""

from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from session.manager import SessionManager, Session
from core.guardrails import Guardrails, CommandRiskLevel
from session.logger import SessionLogger
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
        command: str, 
        client_id: str = "default", 
        confirm: Optional[bool] = False
    ) -> Dict[str, Any]:
        """Execute a command on the network device console with safety guardrails.
        
        Args:
            command: The command string to execute (e.g., 'show version', 'display interface brief')
            client_id: Optional client identifier for multi-session management (default: "default")
            confirm: Optional confirmation flag for commands that require approval (default: False)
        
        Returns:
            Structured JSON response with status, output/error message, and required action.
        """
        # Implementation will be added in next task
        return {
            "success": False,
            "error": "Not implemented",
            "action": "error"
        }
```

- [ ] **Step 2: Verify the file is created and imports are valid**

Run: `python -c "import tools.execute; print('Import successful')"`
Expected: "Import successful" with no errors.

- [ ] **Step 3: Commit**

```bash
git add tools/execute.py
git commit -m "feat: create tools/execute.py skeleton with register_tools"
```

---

### Task 2: Implement the core execute_command logic

**Files:**
- Modify: `tools/execute.py`

- [ ] **Step 1: Implement the complete execute_command logic**

Replace the placeholder function with this complete implementation:

```python
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
        command: str, 
        client_id: str = "default", 
        confirm: Optional[bool] = False
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
            
            # Check command with guardrails
            is_allowed, risk_level, message = _guardrails.check_command(command)
            
            # Handle blocked commands
            if risk_level == CommandRiskLevel.BLOCKED:
                return {
                    "success": False,
                    "error": message,
                    "action": "blocked",
                    "command": command
                }
            
            # Handle confirmation required
            if risk_level == CommandRiskLevel.CONFIRMATION_REQUIRED:
                if not confirm:
                    return {
                        "success": False,
                        "error": message,
                        "action": "confirmation_required",
                        "command": command
                    }
                # If confirmed, mark as allowed and proceed
                _guardrails.confirm_command(command)
            
            # Execute command with session lock to ensure sequential execution
            def execute_with_lock(sess: Session) -> Dict[str, Any]:
                # Send command and get response
                response = sess.connection.send_command(command)
                
                # Update session state with last output
                sess.state.update_last_output(response)
                
                # Log command and response (credentials redacted by logger)
                sess.logger.log_command(command)
                sess.logger.log_response(response)
                
                return {
                    "success": True,
                    "output": response,
                    "action": "completed",
                    "command": command
                }
            
            return _session_manager.with_session_lock(client_id, execute_with_lock)
            
        except KeyError:
            error_msg = f"No session found for client_id '{client_id}'. Please initialize the connection first."
            return {
                "success": False,
                "error": error_msg,
                "action": "error",
                "client_id": client_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "action": "error"
            }
```

- [ ] **Step 2: Check for LSP diagnostics**

Run diagnostics to catch any import or type errors.

- [ ] **Step 3: Test the module imports**

Run: `python -c "from tools.execute import register_tools; print('Import successful after implementation')"`
Expected: No import errors.

- [ ] **Step 4: Commit**

```bash
git add tools/execute.py
git commit -m "feat: implement core execute_command logic with guardrails and logging"
```

---

### Task 3: Add __init__.py to tools package and verify structure

**Files:**
- Create: `tools/__init__.py`
- Verify: `tools/execute.py` follows architecture requirements

- [ ] **Step 1: Create tools package __init__.py**

```python
"""Tool implementations for NetworkConsole MCP server."""
from .execute import register_tools as register_execute_tools

__all__ = ["register_execute_tools"]
```

- [ ] **Step 2: Verify package structure**

Run: `ls -la tools/ && python -c "import tools; from tools import register_execute_tools; print('Package import successful')"`
Expected: Package is importable.

- [ ] **Step 3: Commit**

```bash
git add tools/__init__.py
git commit -m "chore: add tools package __init__.py"
```

---

### Task 4: Verify implementation meets all requirements

**Files:**
- Verify: `tools/execute.py` meets all spec requirements

Checklist verification:
- [ ] **Requirement 1:** `register_tools(mcp)` function implemented ✓
- [ ] **Requirement 2:** Tool accepts `command: string`, `client_id: string = "default"`, `confirm: Optional[bool] = False` ✓
- [ ] **Requirement 3:** Gets session from session manager ✓
- [ ] **Requirement 4:** Checks command with guardrails ✓
- [ ] **Requirement 5:** BLOCKED commands return JSON error ✓
- [ ] **Requirement 6:** CONFIRMATION_REQUIRED when confirm != True returns confirmation request ✓
- [ ] **Requirement 7:** Confirmed/allowed commands execute via session connection ✓
- [ ] **Requirement 8:** Logs command and response via session logger ✓
- [ ] **Requirement 9:** Credential redaction handled by SessionLogger ✓
- [ ] **Requirement 10:** Returns JSON structured response ✓
- [ ] **Requirement 11:** Tool only exposes interface, all business logic in existing modules ✓

- [ ] **Step 1: Run final diagnostics check**

Run LSP diagnostics on the file.

- [ ] **Step 2: Run Python syntax check**

Run: `python -m py_compile tools/execute.py && echo "Syntax check passed"`
Expected: "Syntax check passed"

- [ ] **Step 3: Commit if any fixes needed**

If everything passes:
"Verification complete - implementation ready."
```