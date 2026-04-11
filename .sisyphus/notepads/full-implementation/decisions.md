# Architectural Decisions

## Session Manager Design
- **One session per client**: SessionManager maps client_id to Session object; create_session is idempotent.
- **Thread safety**: Global RLock protects session dictionary; per-session RLock serializes commands.
- **Component integration**: Session dataclass contains SerialConnection, DeviceSessionState, PromptDetector, logger placeholder, and lock.
- **Command queuing**: Provided via `with_session_lock` method that acquires session lock and executes a user function.
- **Logging placeholder**: `_log_command` method ready for future integration.

## Rationale
- Using RLock allows re-entrancy (same thread can acquire lock multiple times).
- Default factories in dataclass ensure each session gets its own instances.
- Global lock ensures atomic operations on session dictionary without deadlocks.
- Separate per-session locks allow concurrent commands across different sessions.
- Placeholder logger avoids premature implementation while preserving interface.