# PROJECT KNOWLEDGE BASE

**Generated:** 2026-04-11
**Commit:** n/a (not a git repo)
**Branch:** n/a

## OVERVIEW
Core business logic for network device console management: command safety guardrails and device state machine.

## STRUCTURE
```
core/
├── guardrails.py      # 2-tier command safety validation with risk classification
├── state_machine.py   # Device conversation state machine with transition validation
└── __init__.py        # Package initialization
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Command safety validation | `guardrails.py:11` | `Guardrails` class with 2-tier checking |
| Risk level classification | `guardrails.py:5` | `CommandRiskLevel` enum: SAFE, CONFIRMATION_REQUIRED, BLOCKED |
| Blocked commands list | `guardrails.py:17` | `BLOCKED_COMMANDS` - severe impact operations |
| Confirmation-required commands | `guardrails.py:31` | `CONFIRMATION_COMMANDS` - configuration changes |
| Device state management | `state_machine.py:14` | `DeviceSessionState` class with transition validation |
| State definitions | `state_machine.py:5` | `DeviceState` enum: DISCONNECTED → ERROR |
| Allowed transitions | `state_machine.py:18` | `_allowed_transitions` dictionary |
| Test coverage | `tests/test_guardrails.py` | Comprehensive guardrail validation tests |
| Test coverage | `tests/test_state_machine.py` | State transition validation tests |

## CONVENTIONS
- All public methods have type hints
- Enums use PascalCase for values (e.g., `SAFE`, `DISCONNECTED`)
- Class properties use `@property` decorators for read-only access
- Transition validation is explicit with `can_transition()` before `transition()`
- Guardrails use 2-tier checking: blocked commands → confirmation commands → safe commands
- All test methods have descriptive docstrings explaining purpose

## ANTI-PATTERNS (THIS MODULE)
- Direct state transitions without validation - must use `can_transition()` check first
- Hardcoded command lists outside `Guardrails` class - all command validation must go through guardrails
- Missing type hints on public interfaces - all public methods must have type hints
- State machine transitions that skip intermediate states - must follow defined transition graph
- Business logic in test files - tests should only verify behavior, not contain logic
- Credential storage in state machine - credentials should be handled by session layer

## UNIQUE STYLES
- Risk-based command classification with explicit enum values
- State machine with explicit transition validation and guard methods
- Property-based access to session state (username, password, prompt patterns)
- Comprehensive test coverage with descriptive test names and docstrings
- Clear separation between safety validation (guardrails) and session state (state machine)

## NOTES
- Guardrails are designed to be extensible: add commands to `BLOCKED_COMMANDS` or `CONFIRMATION_COMMANDS` lists
- State machine ensures valid conversation flow: disconnected → connecting → authenticating → authenticated → configuring
- Error state is terminal and requires resetting to disconnected
- All credentials are optional properties in state machine - actual credential handling is in session layer
- Prompt patterns dictionary allows for vendor-specific prompt detection learning