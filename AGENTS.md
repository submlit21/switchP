# PROJECT KNOWLEDGE BASE

**Generated:** 2026-04-11
**Commit:** n/a (not a git repo)
**Branch:** n/a

## OVERVIEW
MCP (Model Context Protocol) server for network device console management via serial port. Python-based project with complete modular architecture implementing thread-safe multi-session management, command safety guardrails, automatic credential handling, and vendor command extensibility.

## STRUCTURE
```
switchP/
├── core/          # Core business logic: guardrails, state machine
├── session/       # Session management: connection, manager, logger, parser
├── tools/         # MCP tool implementations: execute, device, credentials, interactive
├── resources/     # Vendor command resource system with plugin architecture
├── resources/vendor/ # Abstract base class for vendor implementations
├── tests/         # pytest test suite with comprehensive coverage
├── logs/          # Session logging directory (credentials automatically redacted)
├── config.py      # Pydantic Settings configuration
├── server.py      # Main MCP server entry point
└── requirements.txt # Python dependencies
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| MCP server entry point | `server.py` | Server initialization and tool/resource registration |
| Configuration | `config.py` | Environment-based serial port/baud rate configuration |
| Core business logic | `core/` | Command guardrails, device state machine |
| Session management | `session/` | Serial connection, session manager, logging, prompt detection |
| MCP tool implementations | `tools/` | All MCP-exposed tools |
| Vendor extensibility | `resources/vendor/` | Abstract base class for adding new vendors |
| Test suite | `tests/` | pytest tests for all core components |
| Session logging | `logs/` | Automatic logging with credential redaction |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `Settings` | class | `config.py:5` | Pydantic Settings for application configuration |
| `CommandRiskLevel` | enum | `core/guardrails.py:5` | Risk classification: SAFE, CONFIRMATION_REQUIRED, BLOCKED |
| `Guardrails` | class | `core/guardrails.py:15` | Command safety validation with 2-tier checking |
| `DeviceState` | enum | `core/state_machine.py:5` | Connection state: disconnected → error |
| `DeviceSessionState` | class | `core/state_machine.py:15` | Validated state machine with transition guards |
| `SerialConnection` | class | `session/connection.py:15` | Serial port management with auto-reconnect |
| `SessionManager` | class | `session/manager.py:40` | Thread-safe multi-session management with two-level locking |
| `SessionLogger` | class | `session/logger.py:15` | File logging with automatic credential redaction |
| `PromptParser` | class | `session/parser.py:5` | Prompt detection (username/password/cli) with learning |
| `VendorCommandTable` | ABC | `resources/vendor/base.py:5` | Abstract base for vendor plugin architecture |
| `execute_command` | function | `tools/execute.py` | Main MCP tool: execute command with guardrails |
| `get_device_info` | function | `tools/device.py` | MCP tool: retrieve device info (vendor/model/version/serial) |

## CONVENTIONS
- 4-space indentation (no tabs)
- Type hints used on all public methods
- Snake_case for functions/variables, PascalCase for classes/enums
- Explicit `__all__` in `__init__.py` for public API
- All MCP tools return structured JSON with `success`, `message`, `output`, and `action` fields
- Pytest naming: `test_*.py` files, `Test*` classes, `test_*` methods
- Every test class and method has a docstring explaining purpose

## ANTI-PATTERNS (THIS PROJECT)
- Business logic in `server.py` - only initialization and registration allowed
- Missing `__init__.py` in package directories - all packages must have it
- Hardcoded configuration - all configurable values must come from environment
- Plaintext credential logging - credentials **always** must be redacted (*** )
- Reconnecting for every command - must use persistent connections
- Multiple concurrent commands per session - must use per-session locking
- Business logic in tool modules - tools only expose MCP interface, delegate to core/session

## UNIQUE STYLES
- Two-level thread locking: global RLock for session dictionary, per-session RLock for command serialization
- Plugin architecture for vendors: auto-discovery via `__init__.py` scanning
- Detailed implementation planning in `docs/superpowers/plans/` before coding
- Architectural decision records stored in `.sisyphus/notepads/`
- TDD approach: write failing test first, then implement to pass
- Chinese comments in original placeholder files indicate original intended module purpose

## COMMANDS
```bash
# Run MCP server
python server.py # or python3 server.py

# Run all tests
pytest             # configured in pytest.ini with verbose output

# Run specific test file
pytest tests/test_guardrails.py

# Install dependencies
pip install -r requirements.txt
```

## NOTES
- Log files are stored in `logs/{client_id}_{timestamp}_{session_id}.log`
- All credentials are automatically redacted in logs - never stored in plaintext
- The project follows strict separation of concerns: tools → session manager → core/connection
- Thread safety is a primary design goal - session manager tested with 10 concurrent threads
