# SESSION MANAGEMENT KNOWLEDGE BASE

**Generated:** 2026-04-11
**Parent:** switchP/AGENTS.md

## OVERVIEW
Thread-safe session management for network device console connections with persistent serial connections, automatic credential redaction, and prompt detection.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Session lifecycle management | `manager.py` | Thread-safe session creation, locking, and cleanup |
| Serial port communication | `connection.py` | Persistent serial connections with auto-reconnect |
| Session logging | `logger.py` | Automatic credential redaction and file-based logging |
| Prompt detection | `parser.py` | Username/password/CLI prompt detection with learning |
| Session data structure | `manager.py:Session` | Dataclass containing all session components |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `Session` | dataclass | `manager.py:13` | Container for all session components (connection, state, credentials, logger) |
| `SessionManager` | class | `manager.py:27` | Thread-safe manager with two-level locking (global + per-session) |
| `SerialConnection` | class | `connection.py:14` | Persistent serial port manager with auto-reconnect |
| `SessionLogger` | class | `logger.py:7` | File logger with automatic credential redaction |
| `PromptDetector` | class | `parser.py:4` | Prompt detection with learning capability |
| `create_session()` | method | `manager.py:38` | Creates new session with all components initialized |
| `get_session()` | method | `manager.py:60` | Retrieves existing session or creates new one |
| `cleanup_session()` | method | `manager.py:85` | Safely closes connection and removes session |

## CONVENTIONS
- Two-level thread locking: global RLock for session dictionary, per-session RLock for command serialization
- All credentials stored as `Optional[str]` and never logged in plaintext
- Log files named as `{client_id}_{timestamp}_{session_id}.log` in `logs/` directory
- Prompt detection learns from device output to improve accuracy
- Serial connections remain open between commands for performance

## ANTI-PATTERNS (THIS DOMAIN)
- Opening/closing serial port for each command - must use persistent connections
- Logging credentials in plaintext - always redact with `***`
- Missing per-session locking - concurrent commands for same session must be serialized
- Hardcoded prompt patterns - must support learning from device output
- Storing session state outside `Session` dataclass - all state must be encapsulated
- Direct serial port access bypassing `SerialConnection` - all serial ops must go through connection manager

## UNIQUE STYLES
- Dataclass-based session container with default factories
- Flush-after-write logging for immediate debugging
- Pattern-based credential redaction with common vendor variations
- Prompt detection that learns from actual device output
- Exponential backoff for serial reconnection attempts
- Session cleanup with proper resource disposal

## NOTES
- Session manager tested with 10 concurrent threads in stress tests
- Credential redaction uses regex patterns covering common vendor formats
- Prompt detector can learn new prompt patterns from device output
- Log files are automatically created in `logs/` directory
- All serial operations include timeout handling and error recovery
- Session locking prevents concurrent command execution for same client