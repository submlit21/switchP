# TOOLS KNOWLEDGE BASE

**Generated:** 2026-04-11
**Parent:** ../AGENTS.md

## OVERVIEW
MCP tool implementations exposing network device console functionality via FastMCP decorators. Each tool module follows strict separation of concerns: tools only handle MCP interface, delegating business logic to core/session layers.

## STRUCTURE
```
tools/
├── execute.py      # Main command execution with guardrails and session management
├── device.py       # Device info retrieval and connection status checks
├── interactive.py  # Interactive session lifecycle management
├── credentials.py  # Secure credential storage and authentication
└── __init__.py    # Public API: tool registration functions
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Execute commands on devices | `execute.py` | Main MCP tool with guardrails and session locking |
| Get device info/connection status | `device.py` | Vendor/model/version detection, serial number extraction |
| Manage interactive sessions | `interactive.py` | Start/stop persistent sessions with custom stop patterns |
| Handle authentication | `credentials.py` | Secure credential storage for device login sequences |
| Register all tools | `__init__.py` | Public API for server.py to import and register |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `register_tools` | function | `execute.py:20` | Register execute_command tool with guardrails |
| `execute_command` | function | `execute.py:31` | Main MCP tool: execute with risk assessment |
| `register_tools` | function | `device.py:19` | Register device info and connection tools |
| `get_device_info` | function | `device.py:31` | Extract vendor/model/version/serial from output |
| `check_connection` | function | `device.py:29` | Verify serial port connectivity |
| `start_interactive_session` | function | `interactive.py:17` | Create persistent session with custom stop pattern |
| `stop_interactive_session` | function | `interactive.py:55` | Cleanly terminate session and release resources |
| `set_credentials` | function | `credentials.py:22` | Store auth credentials for session login |

## CONVENTIONS
- Each tool module has a `register_tools(mcp: FastMCP)` function
- Tools return structured JSON: `success`, `message`, `output`, `action`
- Global singleton instances (`_session_manager`, `_guardrails`) initialized once
- All imports use absolute paths via `sys.path.insert(0, ...)`
- Tool decorators include comprehensive docstrings for MCP schema generation
- Error handling follows: try/catch → structured error response → session cleanup

## ANTI-PATTERNS (THIS DIRECTORY)
- Business logic in tool functions - must delegate to core/session
- Multiple tool registrations per module - one `register_tools` function only
- Direct file I/O in tools - use SessionLogger for all logging
- Hardcoded session IDs - use `client_id` parameter with defaults
- Missing error handling - all tools must catch exceptions and return structured errors
- Stateful tool instances - tools must be stateless, using global singletons

## UNIQUE STYLES
- Guardrail integration: execute_command calls Guardrails.assess_risk before execution
- Session-aware design: all tools accept `client_id` for multi-client support
- Thread-safe by design: tools rely on SessionManager's two-level locking
- Credential security: credentials stored in session state, never logged in plaintext
- Interactive mode: stop patterns allow custom command output detection
- Vendor detection: regex-based parsing of device output for vendor/model info