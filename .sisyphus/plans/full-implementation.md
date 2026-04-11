# Complete Implementation of Network Device Console MCP Server

## TL;DR

> **Quick Summary**: Full refactoring of existing single-file MCP server into modular architecture with interactive session support, vendor skill framework, and safety/audit logging.
> 
> **Deliverables**:
> - Modular architecture per requirements: server.py only registers tools
> - Persistent sessions (one per MCP client) with automatic prompt detection
> - Automatic credential handling with separate `set_credentials` tool
> - Safety guardrails with 2-tier confirmation for dangerous commands
> - Full session logging to files with credential redaction
> - Vendor skill framework using MCP resources (extensible for future command tables)
> - Environment-based configuration with defaults
> - JSON-structured responses from all tools
> - State machine for device conversation state
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Project Setup → Core Modules → Session Modules → Tools → Server Refactoring → Final Integration

---

## Context

### Original Request
Refactor the existing single-file MCP server into the planned modular architecture and implement the full feature set for AI-driven automatic network device configuration:
1. Smart interactive sessions with prompt detection and automatic credential handling
2. Vendor-specific skills framework with device detection and MCP resources
3. Safety & audit with command blacklist/confirmation and full session logging
4. Strict architectural constraints on module responsibilities

### Interview Summary
**Key Decisions**:
- **Credential handling**: Separate `set_credentials` MCP tool (in-memory storage per session)
- **Vendor command tables**: Framework only implemented, actual content to be added later
- **Session model**: One persistent session per MCP client, multiple concurrent clients supported
- **Testing**: Add test infrastructure but no requirement for passing automated tests at this stage
- **Session persistence**: "One per client" - each MCP client connection gets one persistent session
- **Credential storage**: In-memory only (cleared on restart/disconnect)
- **Dangerous command handling**: 2-tier:
  - Critical commands (reload, reboot, format, erase): **Blocked by default** - require explicit confirmation
  - High-risk configuration changes: **Warn and require confirmation** before executing
  - After confirmation: allow and log as warning
- **Credential logging**: Always redact credentials from logs (replace with ***)
- **Concurrent commands same session**: Queue sequentially (device console is single-threaded)
- **Connection drops**: Auto-detect, attempt 3 reconnects from session layer, if fails mark as failed

**Research Findings**:
- Current server.py has working implementation but everything is in one file with serial logic directly
- All module directories (core/, session/, tools/) exist as empty placeholders
- MCP best practices confirm: tools for active operations, resources for passive data, lifespan for session state

### Metis Review
**Identified Gaps** (all addressed via user confirmation):
- Credential storage: In-memory confirmed
- Dangerous command handling: 2-tier confirmation confirmed
- Concurrent command same session: Queuing confirmed
- Connection drop handling: 3-auto-reconnect confirmed
- Credential redaction: Required and confirmed

---

## Work Objectives

### Core Objective
Complete implementation of the full modular architecture as planned, implementing all three core features (interactive sessions, vendor skills, safety/audit) while respecting all architectural constraints.

### Concrete Deliverables
- Add `__init__.py` to all package directories (core/, session/, tools/)
- Add `requirements.txt` with all dependencies
- Add configuration module that loads from environment variables with sensible defaults
- Implement `core/state_machine.py` - device state machine with proper transitions
- Implement `core/guardrails.py` - 2-tier command validation with confirmation requirements
- Implement `session/connection.py` - persistent serial connection management
- Implement `session/parser.py` - prompt detection and output parsing
- Implement `session/manager.py` - session lifecycle management (one per client, thread-safe)
- Implement all tool modules:
  - `tools/execute.py` - execute command (session-aware)
  - `tools/interactive.py` - interactive session management
  - `tools/device.py` - get_device_info + check_connection
  - Add `tools/credentials.py` - set_credentials tool
- Implement vendor resource framework (extensible)
- Implement session logging (one file per session, credential redaction)
- Refactor `server.py` to ONLY: initialize MCP, load config, register tools/resources, start server
- All tool returns are JSON structured with success/error status

### Definition of Done
- [x] `server.py` contains no serial communication or business logic directly
- [x] All modules respect separation of concerns (tools only interface, core/session for logic)
- [x] Configuration works via environment variables with defaults
- [x] One log file per session with identifiable name (`{session_id}_{timestamp}.log`)
- [x] Multiple concurrent sessions supported (one per client)
- [x] Credentials never logged in plaintext (always redacted)
- [x] Dangerous commands blocked/warned and require confirmation
- [x] Automatic credential injection when prompts detected
- [x] All responses are JSON-structured

### Must Have
- Strict separation of concerns per architectural constraints
- Thread-safe concurrent session management
- Persistent connections (no reconnect on every command)
- Credential redaction in logs
- 2-tier confirmation for dangerous commands

### Must NOT Have (Guardrails)
- Business logic in `server.py`
- Implementation in tool modules beyond interface exposure
- Hardcoded configuration
- Plaintext credential logging
- Reconnecting for every command

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO - will create test infrastructure
- **Automated tests**: YES - add test infrastructure with basic tests, but tests don't need to pass at completion
- **Framework**: pytest
- **Agent-Executed QA**: EVERY task includes QA scenarios (mandatory)

### QA Policy
Every task MUST include agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **CLI/Module**: Use Bash (Python REPL/one-liners) - Import, call functions, compare output
- **Logging**: Verify files created with expected content/redaction
- **Thread Safety**: Test concurrent access with simple multi-threaded script

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves.

**Wave 1 (Start Immediately - foundation + scaffolding - 7 tasks, all quick/quick):**
├── Task 1: Add __init__.py files to all packages + requirements.txt
├── Task 2: Create configuration module with environment variable support
├── Task 3: Implement core/state_machine.py - device state machine
├── Task 4: Implement core/guardrails.py - 2-tier command safety
├── Task 5: Add test infrastructure (pytest config, directory structure, base fixtures)
└── Task 6: Create base vendor resource framework (extensible)

**Wave 2 (After Wave 1 - core session modules, MAX PARALLEL):**
├── Task 7: Implement session/connection.py - persistent serial connection with auto-reconnect
├── Task 8: Implement session/parser.py - prompt detection and output parsing
├── Task 9: Implement session/manager.py - thread-safe session lifecycle (one per client)
├── Task 10: Implement session logging - one file per session with redaction
└── Task 11: Implement tools/credentials.py - set_credentials MCP tool

**Wave 3 (After Wave 2 - tools + server refactoring, parallel):**
├── Task 12: Implement tools/execute.py - execute_command with session-awareness and guardrails
├── Task 13: Implement tools/interactive.py - interactive_session start/stop
├── Task 14: Implement tools/device.py - check_connection + get_device_info
├── Task 15: Refactor server.py - extract all logic, only register tools/resources
└── Task 16: Add JSON response wrapping for all tools

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.
> **A task WITHOUT QA Scenarios is INCOMPLETE. No exceptions.**

- [x] 1. Add package structure + dependencies

  **What to do**:
  - Add `__init__.py` (empty is fine) to `core/`, `session/`, `tools/`
  - Create `requirements.txt` with all needed dependencies: `pyserial`, `mcp[fastmcp]`, `pydantic-settings` (for env config), `pytest` (for testing)
  - Create `tests/` directory with `__init__.py`
  - Create `.env.example` showing all available environment variables (PORT, BAUD_RATE, etc.)

  **Must NOT do**:
  - Don't implement any business logic yet - this is just scaffolding

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple file creation, no complex logic
  - **Skills**: []
  - **Skills Evaluated but Omitted**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1 - can run with other foundation tasks)
  - **Parallel Group**: Wave 1
  - **Blocks**: All subsequent tasks (depend on this scaffolding)
  - **Blocked By**: None (can start immediately)

  **References**:
  - Current project structure: `AGENTS.md` in root - shows existing directory layout

  **Acceptance Criteria**:
  - [ ] `__init__.py` exists in all three package directories
  - [ ] `requirements.txt` contains all necessary dependencies
  - [ ] `tests/__init__.py` exists
  - [ ] `.env.example` documents all configurable environment variables

  **QA Scenarios**:
  ```
  Scenario: Verify all files created correctly
    Tool: Bash
    Preconditions: Scaffolding not yet created
    Steps:
      1. After task completes, check: ls -la core/__init__.py session/__init__.py tools/__init__.py
      2. Check: ls requirements.txt tests/__init__.py .env.example
      3. Verify: cat requirements.txt contains pyserial, mcp, pydantic-settings, pytest
    Expected Result: All files exist, dependencies listed correctly
    Failure Indicators: Any file missing or wrong dependencies
    Evidence: .sisyphus/evidence/task-01-scaffolding.txt

  Scenario: Verify .env.example documents all config vars
    Tool: Bash (grep)
    Preconditions: Files created
    Steps:
      1. Check: grep -c "PORT" .env.example
      2. Check: grep -c "BAUD_RATE" .env.example
    Expected Result: Both PORT and BAUD_RATE documented
    Evidence: .sisyphus/evidence/task-01-env-example.txt
  ```

  **Commit**: YES
  - Message: `chore: add package scaffolding and dependencies`
  - Files: `core/__init__.py`, `session/__init__.py`, `tools/__init__.py`, `requirements.txt`, `tests/__init__.py`, `.env.example`

- [x] 2. Create configuration module with environment support

  **What to do**:
  - Create `config.py` at root that uses `pydantic-settings` to load configuration from environment variables
  - Provide sensible defaults: PORT="/dev/ttyUSB0", BAUD_RATE=9600, etc.
  - Export the config object so other modules can import from `config import config`

  **Must NOT do**:
  - Don't hardcode configuration - all configurable values must come from env with defaults
  - Don't put configuration in any other module

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple configuration module, just settings class
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: Wave 1
  - **Blocks**: All modules that import configuration
  - **Blocked By**: Task 1 (needs package structure)

  **References**:
  - Current hardcoded config: `server.py:9-10`

  **Acceptance Criteria**:
  - [ ] `config.py` exists with Settings class using pydantic-settings
  - [ ] All configurable parameters have defaults
  - [ ] Config object exported for import

  **QA Scenarios**:
  ```
  Scenario: Configuration loads from environment with defaults
    Tool: Bash (Python REPL)
    Preconditions: Empty environment, no .env set
    Steps:
      1. Run: python -c "from config import config; print(config.port); print(config.baud_rate)"
      2. Verify output is "/dev/ttyUSB0" and 9600
      3. Set env vars and test: PORT=/dev/ttyACM0 BAUD_RATE=115200 python -c "from config import config; print(config.port); print(config.baud_rate)"
      4. Verify output matches environment variables
    Expected Result: Defaults work when env not set, env vars override defaults
    Failure Indicators: Doesn't load defaults or doesn't respect env vars
    Evidence: .sisyphus/evidence/task-02-config-env.txt
  ```

  **Commit**: YES
  - Message: `feat: add environment-based configuration`
  - Files: `config.py`

- [x] 3. Implement core/state_machine.py - device conversation state machine

  **What to do**:
  - Create `DeviceState` enum: DISCONNECTED, CONNECTING, AUTHENTICATING, AUTHENTICATED, CONFIGURING, ERROR
  - Create `DeviceSessionState` class that holds current state and handles transitions
  - Implement `transition(new_state)` that validates allowed transitions:
    - DISCONNECTED → CONNECTING
    - CONNECTING → AUTHENTICATING | ERROR
    - AUTHENTICATING → AUTHENTICATED | ERROR
    - AUTHENTICATED → CONFIGURING | ERROR
    - CONFIGURING → AUTHENTICATED | ERROR
    - Any → ERROR
    - ERROR → DISCONNECTED
  - Store detected prompt patterns and last output in state
  - Store credentials in state (they come from `set_credentials` tool)

  **Must NOT do**:
  - Don't handle serial communication - that's connection module
  - Don't implement device detection - that's for later

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple state machine with enum and transitions
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: Wave 1
  - **Blocks**: session manager, parser, interactive tools
  - **Blocked By**: Task 1 (package structure)

  **Acceptance Criteria**:
  - [ ] `DeviceState` enum with all required states
  - [ ] `DeviceSessionState` class with transition validation
  - [ ] Valid transitions allowed, invalid transitions rejected
  - [ ] Stores credentials, prompt patterns, last output

  **QA Scenarios**:
  ```
  Scenario: Valid state transitions work correctly
    Tool: Bash (Python)
    Preconditions: Module created
    Steps:
      1. Run: python -c "from core.state_machine import DeviceState, DeviceSessionState; s = DeviceSessionState('test', DeviceState.DISCONNECTED); success = s.transition(DeviceState.CONNECTING); print(f'Transition DISCONNECTED→CONNECTING: {success}'); print(f'Current state: {s.device_state}')"
      2. Verify: success = True, state = CONNECTING
      3. Run: python -c "from core.state_machine import DeviceState, DeviceSessionState; s = DeviceSessionState('test', DeviceState.CONNECTING); success = s.transition(DeviceState.AUTHENTICATED); print(f'Transition CONNECTING→AUTHENTICATED: {success}')"
      4. Verify: success = False (must go through AUTHENTICATING)
    Expected Result: Invalid transitions rejected, valid transitions allowed
    Failure Indicators: Allows invalid transitions
    Evidence: .sisyphus/evidence/task-03-state-transitions.txt
  ```

  **Commit**: YES
  - Message: `feat(core): implement device state machine`
  - Files: `core/state_machine.py`

- [x] 4. Implement core/guardrails.py - 2-tier command safety validation

  **What to do**:
  - Implement `CommandRiskLevel` enum: SAFE, CONFIRMATION_REQUIRED, BLOCKED
  - Define the two lists:
    - BLOCKED: reload, reboot, format, format flash:, erase startup-config, write erase, delete flash:, erase flash:, factory-reset, reset saved-configuration
    - CONFIRMATION_REQUIRED: interface *, shutdown, no shutdown, ip address, vlan *, route *, ip route, access-list, firewall *, nat *, security-policy
  - Implement `Guardrails.check_command(command)` that returns:
    - (is_allowed, risk_level, message) where:
      - BLOCKED → is_allowed=False, message explains why
      - CONFIRMATION_REQUIRED → is_allowed=False but with message asking for confirmation
      - SAFE → is_allowed=True
  - Store confirmation status: when user confirms a risky command, mark it as allowed for that execution
  - Implement `is_credential_needed()` that checks if current prompt looks like username/password

  **Must NOT do**:
  - Don't handle command execution - just validation and risk assessment

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Pure validation logic, no I/O
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: Wave 1
  - **Blocks**: execute tool, which uses this
  - **Blocked By**: Task 1 (package structure)

  **Acceptance Criteria**:
  - [ ] All blocked commands correctly identified
  - [ ] All confirmation-required commands correctly identified
  - [ ] Returns correct is_allowed status and message
  - [ ] Detects credential prompts (username:/Password:/password:)

  **QA Scenarios**:
  ```
  Scenario: Blocked commands are rejected
    Tool: Bash (Python)
    Preconditions: Module created
    Steps:
      1. Run: python -c "from core.guardrails import Guardrails; g = Guardrails(); allowed, _, msg = g.check_command('reload'); print(f'Allowed: {allowed}, msg: {msg}')"
      2. Verify: allowed = False
      3. Run: python -c "from core.guardrails import Guardrails; g = Guardrails(); allowed, _, msg = g.check_command('show version'); print(f'Allowed: {allowed}')"
      4. Verify: allowed = True
    Expected Result: Blocked commands blocked, safe commands allowed
    Evidence: .sisyphus/evidence/task-04-blocked-cmds.txt

  Scenario: Confirmation-required commands require confirmation
    Tool: Bash (Python)
    Preconditions: Module created
    Steps:
      1. Run: python -c "from core.guardrails import Guardrails; g = Guardrails(); allowed, level, _ = g.check_command('interface GigabitEthernet0/0'); print(f'Allowed: {allowed}, level: {level}')"
      2. Verify: allowed = False, level = CONFIRMATION_REQUIRED
    Expected Result: Requires confirmation
    Evidence: .sisyphus/evidence/task-04-confirmation-needed.txt

  Scenario: Detects credential prompts correctly
    Tool: Bash (Python)
    Preconditions: Module created
    Steps:
      1. Test: "Username:" → should detect as credential needed
      2. Test: "Password:" → should detect as credential needed
      3. Test: "Device#" → should NOT detect
    Expected Result: Correct detection
    Evidence: .sisyphus/evidence/task-04-credential-detect.txt
  ```

  **Commit**: YES
  - Message: `feat(core): implement 2-tier command safety guardrails`
  - Files: `core/guardrails.py`

- [x] 5. Add test infrastructure

  **What to do**:
  - Create `tests/conftest.py` with pytest configuration
  - Create `tests/test_state_machine.py` with basic tests for state transitions
  - Create `tests/test_guardrails.py` with basic tests for command checking
  - Add `pytest.ini` or `pyproject.toml` with basic pytest config

  **Must NOT do**:
  - Don't require 100% coverage - just infrastructure and basic tests
  - Don't test modules that don't exist yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Just test configuration and basic tests
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: Wave 1
  - **Blocks**: None - infrastructure only
  - **Blocked By**: Task 1 (needs tests directory)

  **Acceptance Criteria**:
  - [ ] pytest configuration exists
  - [ ] Basic tests for state machine and guardrails created
  - [ ] `pytest tests/` can run without crashing

  **QA Scenarios**:
  ```
  Scenario: pytest can run
    Tool: Bash
    Preconditions: Test infrastructure created
    Steps:
      1. Run: pytest tests/ -v
      2. Verify: Tests run (even if some don't pass yet due to missing implementation)
    Expected Result: pytest runs successfully (doesn't crash)
    Failure Indicators: pytest fails with "no config" or import errors
    Evidence: .sisyphus/evidence/task-05-pytest-run.txt
  ```

  **Commit**: YES
  - Message: `test: add test infrastructure with basic tests`
  - Files: `tests/conftest.py`, `tests/test_state_machine.py`, `tests/test_guardrails.py`, `pytest.ini`

- [x] 6. Create vendor resource framework (extensible)

  **What to do**:
  - Create `resources/vendor/` directory structure
  - Create base class/interface for vendor command tables
  - Create function that registers vendor resources with MCP
  - Create empty structure that allows adding vendor command tables later
  - Don't populate actual vendor data yet - just framework

  **Must NOT do**:
  - Don't add actual vendor command tables (user requested just framework)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Just framework structure and registration
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: Wave 1
  - **Blocks**: Server registration (needs this when registering resources)
  - **Blocked By**: Task 1 (package structure)

  **Acceptance Criteria**:
  - [ ] Framework structure exists
  - [ `register_vendor_resources(mcp)` function that can be called from server.py
  - [ ] Extensible for adding vendors later

  **QA Scenarios**:
  ```
  Scenario: Framework imports correctly
    Tool: Bash (Python)
    Preconditions: Framework created
    Steps:
      1. Run: python -c "from resources.vendor.base import register_vendor_resources; print('OK')"
      2. Verify: No import errors
    Expected Result: Imports successfully
    Failure Indicators: Import error due to missing files/wrong structure
    Evidence: .sisyphus/evidence/task-06-vendor-framework.txt
  ```

  **Commit**: YES
  - Message: `feat(resources): add vendor command table framework`
  - Files: `resources/__init__.py`, `resources/vendor/__init__.py`, `resources/vendor/base.py`

- [x] 7. Implement session/connection.py - persistent serial connection with auto-reconnect

  **What to do**:
  - Create `SerialConnection` class that manages persistent serial connection (doesn't open/close for every command)
  - Implement `open()`, `close()`, `send_command()` methods
  - Implement `read_until_prompt()` that reads until expected stop/prompt pattern
  - Add auto-reconnect logic: if connection drops, attempt 3 reconnects with backoff
  - Handle timeouts correctly for slow devices
  - Use configuration from `config.py` for port/baud rate

  **Must NOT do**:
  - Don't manage multiple sessions - that's session manager
  - Don't handle state machine transitions - just connection I/O

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Serial communication needs careful error handling and timeouts
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Parallel Group**: Wave 2
  - **Blocks**: Session manager, which depends on this
  - **Blocked By**: Task 2 (configuration), Task 1 (package scaffolding)

  **Acceptance Criteria**:
  - [ ] `SerialConnection` class with open/close/send_command/read_until
  - [ ] Auto-reconnect: 3 attempts before marking as failed
  - [ ] Uses configuration from config module

  **QA Scenarios**:
  ```
  Scenario: Connection lifecycle works
    Tool: Bash (Python) - mock serial for testing
    Preconditions: Module created
    Steps:
      1. Create instance with test parameters, call open()
      2. Verify: Connection opens successfully (if port available)
      3. Send command and read response
      4. Call close()
      5. Verify: Connection closed
    Expected Result: All operations work without exceptions
    Failure Indicators: Exceptions during open/send/close
    Evidence: .sisyphus/evidence/task-07-connection-lifecycle.txt

  Scenario: Auto-reconnect attempts on failure
    Tool: Bash (Python) - simulated failure
    Preconditions: Module created
    Steps:
      1. Create connection that will fail
      2. Attempt to send command
      3. Verify: 3 reconnect attempts made before giving up
      4. Verify: Returns appropriate error
    Expected Result: 3 attempts then error
    Evidence: .sisyphus/evidence/task-07-auto-reconnect.txt
  ```

  **Commit**: YES
  - Message: `feat(session): implement persistent serial connection with auto-reconnect`
  - Files: `session/connection.py`

- [x] 8. Implement session/parser.py - prompt detection and output parsing

  **What to do**:
  - Implement `PromptDetector` class that detects common prompts:
    - Username: /Username:/Login:
    - Password: /Password:/password:
    - CLI prompts: ending with `#` or `>`
  - Implement `detect_prompt(output)` that returns what type of prompt detected (if any)
  - Implement `strip_echo(command, output)` that removes command echo from output
  - Store detected prompt patterns per session

  **Must NOT do**:
  - Don't handle automatic credential sending - that's done by state machine/session manager

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Pattern matching and parsing, no complex I/O
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Parallel Group**: Wave 2
  - **Blocks**: Session manager
  - **Blocked By**: Task 1 (package scaffolding), Task 3 (state machine)

  **Acceptance Criteria**:
  - [ ] Detects username prompts correctly
  - [ ] Detects password prompts correctly
  - [ ] Detects CLI prompts correctly
  - [ ] Strips command echo from output

  **QA Scenarios**:
  ```
  Scenario: Correctly detects credential prompts
    Tool: Bash (Python)
    Preconditions: Module created
    Steps:
      1. Test with output containing "Password:"
      2. Verify: returns PASSWORD prompt type
      3. Test with output containing "Username:"
      4. Verify: returns USERNAME prompt type
      5. Test with output containing "device#"
      6. Verify: returns CLI prompt type
    Expected Result: All prompt types detected correctly
    Failure Indicators: False negatives or false positives
    Evidence: .sisyphus/evidence/task-08-prompt-detection.txt

  Scenario: Strips command echo correctly
    Tool: Bash (Python)
    Preconditions: Module created
    Steps:
      1. Command = "show version", output = "show version\nCisco IOS Software..."
      2. Call strip_echo(command, output)
      3. Verify: Echo removed, output starts with "Cisco IOS Software..."
    Expected Result: Echo removed correctly
    Evidence: .sisyphus/evidence/task-08-strip-echo.txt
  ```

  **Commit**: YES
  - Message: `feat(session): implement prompt detection and output parsing`
  - Files: `session/parser.py`

- [x] 9. Implement session/manager.py - thread-safe session lifecycle (one per client)

  **What to do**:
  - Create `SessionManager` class that's thread-safe
  - One session per client (client ID identifies session)
  - Each session contains: `SerialConnection`, `DeviceSessionState`, credentials, parser
  - Implement: `create_session(client_id)`, `get_session(client_id)`, `close_session(client_id)`
  - Uses per-session locking for concurrent command queuing (all commands for same session executed sequentially)
  - Automatically queues concurrent commands for same session and executes them in order
  - Integrates with logging: every command and response gets logged

  **Must NOT do**:
  - Don't implement connection itself - uses `session/connection.py`
  - Don't expose MCP tools directly - just business logic

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Thread safety and concurrent queuing requires careful design
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Parallel Group**: Wave 2
  - **Blocks**: All tool implementations
  - **Blocked By**: Task 3 (state machine), Task 7 (connection), Task 8 (parser), Task 10 (logging)

  **Acceptance Criteria**:
  - [ ] Multiple concurrent sessions supported (one per client)
  - [ ] Concurrent commands for same session are queued and executed sequentially
  - [ ] Thread-safe - no race conditions when creating/accessing sessions
  - [ ] Session creation/getting/closure works correctly

  **QA Scenarios**:
  ```
  Scenario: Multiple sessions can coexist
    Tool: Bash (Python)
    Preconditions: Module created
    Steps:
      1. Run: python -c "from session.manager import SessionManager; sm = SessionManager; s1 = sm.create_session('client1'); s2 = sm.create_session('client2'); assert s1 is not None; assert s2 is not None; assert s1 != s2; print('OK')"
      2. Verify: No exceptions, output "OK"
    Expected Result: Multiple sessions created successfully
    Failure Indicators: Exception or wrong session returned
    Evidence: .sisyphus/evidence/task-09-multiple-sessions.txt

  Scenario: Concurrent commands queued sequentially
    Tool: Bash (Python) with threading
    Preconditions: Module created
    Steps:
      1. Create 10 threads that all queue a command to same session
      2. Verify: All commands executed in order, no output interleaving
    Expected Result: All executed sequentially, correct output order
    Failure Indicators: Output interleaving or exceptions
    Evidence: .sisyphus/evidence/task-09-concurrent-queue.txt
  ```

  **Commit**: YES
  - Message: `feat(session): implement thread-safe session manager with queuing`
  - Files: `session/manager.py`

 - [x] 10. Implement session logging - one file per session with credential redaction

  **What to do**:
  - Create `SessionLogger` class that manages logging for a session
  - Creates log file in `logs/` directory with naming pattern: `{client_id}_{timestamp}_{session_id}.log` for identification
  - Implements `log_command(command)` and `log_response(response)`
  - Redacts credentials from logs: when command/response contains username/password values, replaces with `***`
  - Flush after each write so log is always up-to-date for debugging

  **Must NOT do**:
  - Don't log credentials in plaintext - must redact

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple file logging with redaction
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Parallel Group**: Wave 2
  - **Blocks**: Session manager
  - **Blocked By**: Task 1 (package scaffolding)

  **Acceptance Criteria**:
  - [ ] Creates separate log file per session
  - [ ] File name contains identifiable info (client_id, timestamp, session_id)
  - [ ] Credentials are redacted in logs
  - [ ] Flush after each write

  **QA Scenarios**:
  ```
  Scenario: Log file created with correct name
    Tool: Bash
    Preconditions: Logger created for session "client1" with id "session-abc123"
    Steps:
      1. After opening logger, check logs/ directory
      2. Verify: File exists containing "client1" and "abc123" in name
    Expected Result: File created with correct naming
    Failure Indicators: File missing or wrong name
    Evidence: .sisyphus/evidence/task-10-log-file-creation.txt

  Scenario: Credentials redacted correctly
    Tool: Bash (grep)
    Preconditions: Logged a command with password "mysecret"
    Steps:
      1. Check log file: grep -q "mysecret" logs/*.log
      2. Verify: grep returns 1 (not found)
      3. Check that *** appears where password should be
    Expected Result: Credential redacted
    Failure Indicators: Plaintext credential found in log
    Evidence: .sisyphus/evidence/task-10-credential-redaction.txt
  ```

  **Commit**: YES
  - Message: `feat(session): implement session logging with credential redaction`
  - Files: `session/logger.py`

- [x] 11. Implement tools/credentials.py - set_credentials MCP tool

  **What to do**:
  - Implement `register_tools(mcp)` that registers `set_credentials` tool
  - Tool accepts `username` and `password` (and optional session_id if multi-session)
  - Stores credentials in the session state (in-memory only)
  - Returns JSON response indicating success
  - This is just the interface - actual automatic use when prompts detected is handled by session manager

  **Must NOT do**:
  - Don't store credentials anywhere except in-memory per-session state
  - Don't implement business logic here - just interface to store credentials in session

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple tool interface that delegates to session manager
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Parallel Group**: Wave 2
  - **Blocks**: Server registration
  - **Blocked By**: Task 9 (session manager), Task 1 (package scaffolding)

  **Acceptance Criteria**:
  - [ ] `set_credentials` tool registered
  - [ ] Stores username/password in session state
  - [ ] Returns JSON response

  **QA Scenarios**:
  ```
  Scenario: Credentials stored successfully
    Tool: Bash (Python)
    Preconditions: Session created
    Steps:
      1. Call set_credentials with username "admin", password "secret123"
      2. Retrieve session state
      3. Verify: credentials stored correctly
    Expected Result: Credentials stored in session state
    Failure Indicators: Credentials not stored
    Evidence: .sisyphus/evidence/task-11-credentials-stored.txt
  ```

  **Commit**: YES
  - Message: `feat(tools): add set_credentials MCP tool`
  - Files: `tools/credentials.py`

- [x] 12. Implement tools/execute.py - execute_command with session-awareness and guardrails

  **What to do**:
  - Implement `register_tools(mcp)` that registers `execute_command` tool
  - Tool accepts command (and optional confirmation flag for risky commands)
  - Get the session from session manager
  - Check command with guardrails:
    - If BLOCKED → return JSON error
    - If CONFIRMATION_REQUIRED and no confirmation flag → return JSON asking for confirmation
    - If allowed → execute via session connection
  - If guardrails pass and allowed, execute command through session
  - If prompt detected (credentials), automatically send credentials from session state
  - Log command and response via session logger
  - Return JSON structured response: {success: bool, output: str, message: str}

  **Must NOT do**:
  - Don't implement guardrails logic here - just use `core.guardrails`
  - Don't implement session management here - just use `session.manager`

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Integrates multiple modules needs correct wiring
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 3)
  - **Parallel Group**: Wave 3
  - **Blocks**: Server final refactoring
  - **Blocked By**: Task 4 (guardrails), Task 9 (session manager), Task 10 (logging)

  **Acceptance Criteria**:
  - [ ] `execute_command` tool registered
  - [ ] Integrates with guardrails for checking
  - [ ] Asks confirmation when needed
  - [ ] Auto-sends credentials when prompt detected
  - [ ] Logs command/response
  - [ ] Returns JSON structured response

  **QA Scenarios**:
  ```
  Scenario: Blocked command returns error and doesn't execute
    Tool: Python via Bash
    Preconditions: Module created, session created
    Steps:
      1. Call execute_command with "reload"
      2. Get response, check JSON result
      3. Verify: success = False, message indicates blocked
    Expected Result: Blocked, error returned, not executed
    Failure Indicators: Command executes successfully when it shouldn't
    Evidence: .sisyphus/evidence/task-12-blocked-cmd.txt

  Scenario: Safe command executes successfully
    Tool: Python via Bash
    Preconditions: Module created, session created
    Steps:
      1. Call execute_command with "show version"
      2. Verify: success = True, output contains device response
    Expected Result: Executes, returns output
    Failure Indicators: Execution fails when it should work
    Evidence: .sisyphus/evidence/task-12-safe-cmd-exec.txt

  Scenario: Confirmation-required without confirmation asks for confirmation
    Tool: Python via Bash
    Preconditions: Module created, session created
    Steps:
      1. Call execute_command with "interface GigabitEthernet0/0" without confirmation
      2. Verify: success = False, message asks for confirmation
    Expected Result: Asks confirmation, doesn't execute
    Failure Indicators: Executes without confirmation
    Evidence: .sisyphus/evidence/task-12-confirmation-needed.txt
  ```

  **Commit**: YES
  - Message: `feat(tools): implement execute_command with session and guardrails`
  - Files: `tools/execute.py`

- [x] 13. Implement tools/interactive.py - interactive_session management

  **What to do**:
  - Implement `register_tools(mcp)` that registers:
    - `start_interactive_session` - starts an interactive session for client
    - `stop_interactive_session` - stops and closes the interactive session
  - `start_interactive_session` creates new session in session manager with client ID
  - Returns JSON with session status
  - Storing stop pattern (expected prompt/stop sequence) that user configures
  - This is the top-level tool for interactive AI usage

  **Must NOT do**:
  - Don't implement session management - delegate to session manager

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Just tool interface, delegates all logic to session manager
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 3)
  - **Parallel Group**: Wave 3
  - **Blocks**: Server final refactoring
  - **Blocked By**: Task 9 (session manager)

  **Acceptance Criteria**:
  - [ ] Two tools registered: start and stop
  - [ ] Creates session on start, closes on stop
  - [ ] Accepts custom stop pattern
  - [ ] Returns JSON response

  **QA Scenarios**:
  ```
  Scenario: Start interactive session works
    Tool: Python via Bash
    Preconditions: Module created
    Steps:
      1. Call start_interactive_session with client_id "test-client"
      2. Verify: success = True, session exists in manager
    Expected Result: Session created successfully
    Failure Indicators: Session not created or error
    Evidence: .sisyphus/evidence/task-13-start-interactive.txt

  Scenario: Stop interactive session works
    Tool: Python via Bash
    Preconditions: Session started
    Steps:
      1. Call stop_interactive_session
      2. Verify: session closed and removed from manager
    Expected Result: Session closed successfully
    Failure Indicators: Session still exists after stop
    Evidence: .sisyphus/evidence/task-13-stop-interactive.txt
  ```

  **Commit**: YES
  - Message: `feat(tools): add interactive_session start/stop tools`
  - Files: `tools/interactive.py`

- [x] 14. Implement tools/device.py - check_connection + get_device_info

  **What to do**:
  - Implement `register_tools(mcp)` that registers:
    - `check_connection` - checks if serial port is accessible (migrated from original)
    - `get_device_info` - executes "show version" or "display version" and returns parsed device info
  - `check_connection` just checks serial port accessibility
  - `get_device_info` executes appropriate command based on detected prompt/vendor and returns version info
  - Returns JSON structured response

  **Must NOT do**:
  - Don't implement connection check logic inline - delegate to connection module

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Two simple tool implementations, delegates to existing modules
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 3)
  - **Parallel Group**: Wave 3
  - **Blocks**: Server final refactoring
  - **Blocked By**: Task 7 (connection), Task 9 (session manager)

  **Acceptance Criteria**:
  - [ ] Both tools registered
  - [ ] check_connection correctly reports port accessibility with proper error messages (permission denied, not found)
  - [ ] get_device_info executes version command and returns output
  - [ ] All responses JSON structured

  **QA Scenarios**:
  ```
  Scenario: check_connection returns correct status
    Tool: Python via Bash
    Preconditions: Module created
    Steps:
      1. Call check_connection with configured port
      2. Verify response indicates if connected/error with correct message
    Expected Result: Correct status returned
    Failure Indicators: Wrong error message for known error
    Evidence: .sisyphus/evidence/task-14-check-connection.txt

  Scenario: get_device_info executes command and returns info
    Tool: Python via Bash
    Preconditions: Session started, connected to device
    Steps:
      1. Call get_device_info
      2. Verify: success = True, output contains version information
    Expected Result: Version info returned successfully
    Failure Indicators: Error or empty output when should work
    Evidence: .sisyphus/evidence/task-14-get-device-info.txt
  ```

  **Commit**: YES
  - Message: `feat(tools): add check_connection and get_device_info tools`
  - Files: `tools/device.py`

- [x] 15. Refactor server.py - extract all logic, only register tools/resources

  **What to do**:
  - Remove all serial communication and business logic from `server.py`
  - Import and register all tools from:
    - `tools/execute`
    - `tools/interactive`
    - `tools/device`
    - `tools/credentials`
  - Import and register all vendor resources
  - Load configuration from `config.py`
  - Initialize MCP server, register everything, run
  - After refactoring: server.py should NOT contain any serial logic, just registration

  **Must NOT do**:
  - Don't keep any business logic in server.py - ONLY registration and startup

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Just refactoring/registration, wiring existing modules together
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on all tools created)
  - **Parallel Group**: Last in Wave 3
  - **Blocks**: Final verification
  - **Blocked By**: Tasks 12, 13, 14, 11 (all tools)

  **Acceptance Criteria**:
  - [ ] Server runs and all tools are registered
  - [ ] No serial communication logic directly in server.py
  - [ ] Uses configuration from config module

  **QA Scenarios**:
  ```
  Scenario: server.py imports all tools and can start without errors
    Tool: Bash
    Preconditions: Refactoring complete
    Steps:
      1. Run: python -c "import server; print('OK')"
      2. Verify: No import errors, outputs "OK"
      3. Check for serial logic: grep -n -E "(serial|read|write|open)" server.py | grep -v "import"
      4. Verify: Only imports, no serial logic in function bodies
    Expected Result: No import errors, no serial logic in server.py body
    Failure Indicators: Import error or serial logic found in server.py
    Evidence: .sisyphus/evidence/task-15-server-check.txt
  ```

  **Commit**: YES
  - Message: `refactor: extract business logic from server.py, only register tools`
  - Files: `server.py`

- [x] 16. Add JSON response wrapping for all tools

  **What to do**:
  - Create `tools/utils.py` with `format_response()` helper that formats all responses as JSON:
    - `success: bool` - whether operation succeeded
    - `output: Optional[str]` - output/result data if succeeded
    - `message: Optional[str]` - error/information message if failed or needs confirmation
  - All tools use this wrapper to ensure consistent JSON responses
  - Update all existing tool implementations to use this wrapper

  **Must NOT do**:
  - Don't allow plain text responses from any tool - everything must be JSON

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple wrapper utility, update all tools to use it
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (last step before final verification)
  - **Parallel Group**: Wave 3
  - **Blocks**: Final verification
  - **Blocked By**: Task 15 (server refactoring), all other tool tasks

  **Acceptance Criteria**:
  - [ ] Utility created
  - [ ] All tools use JSON wrapping
  - [ ] All responses have consistent structure

  **QA Scenarios**:
  ```
  Scenario: All tool responses are valid JSON
    Tool: Python via Bash
    Preconditions: All tools updated
    Steps:
      1. Call each tool with minimal parameters
      2. Parse response as JSON
      3. Verify: JSON has success field, correct types
    Expected Result: All responses valid JSON with correct schema
    Failure Indicators: Invalid JSON or missing fields
    Evidence: .sisyphus/evidence/task-16-json-response.txt
  ```

  **Commit**: YES
  - Message: `refactor(tools): add JSON response wrapper and standardize all outputs`
  - Files: `tools/utils.py` + updates to all tool files

---

## Final Verification Wave (after all implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
> Never mark F1-F4 as checked before getting user's okay. Rejection or feedback -> fix -> re-run -> present again -> wait for okay.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (import works, file created, functions exist). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `python -m py_compile server.py` and on all modules. Review all changed files for: `except Exception:` (too broad), empty catches, `print` in production (should use logging), commented-out code, unused imports. Check for common Python issues.
  Output: `Compile [PASS/FAIL] | Errors Found [N] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (features working together, not isolation). Test edge cases: concurrent commands, credential detection, dangerous command blocking. Save all evidence to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

Wave 1 (foundation):
1. `chore: add package scaffolding and dependencies`
2. `feat: add environment-based configuration`
3. `feat(core): implement device state machine`
4. `feat(core): implement 2-tier command safety guardrails`
5. `test: add test infrastructure with basic tests`
6. `feat(resources): add vendor command table framework`

Wave 2 (session core):
7. `feat(session): implement persistent serial connection with auto-reconnect`
8. `feat(session): implement prompt detection and output parsing`
9. `feat(session): implement thread-safe session manager with queuing`
10. `feat(session): implement session logging with credential redaction`
11. `feat(tools): add set_credentials MCP tool`

Wave 3 (tools + refactor):
12. `feat(tools): implement execute_command with session and guardrails`
13. `feat(tools): add interactive_session start/stop tools`
14. `feat(tools): add check_connection and get_device_info tools`
15. `refactor: extract business logic from server.py, only register tools`
16. `refactor(tools): add JSON response wrapper and standardize all outputs`

---

## Success Criteria

### Verification Commands
```bash
# Architecture check - no serial logic in server.py
grep -n -E "(serial|read|write|open)" server.py | grep -v "import"
# Should return zero lines (only imports)

# Check that all packages have __init__.py
ls -la core/__init__.py session/__init__.py tools/__init__.py
# All three should exist

# Check that configuration loads from environment
python -c "from config import config; assert config.port is not None"
# Should exit 0, no errors

# Run Python syntax check on all files
find . -name "*.py" -exec python -m py_compile {} +
# Should exit 0, no errors
```

### Final Checklist
- [x] All "Must Have" present
- [x] All "Must NOT Have" absent
- [x] All tasks complete
- [x] All QA scenarios pass
- [x] All tests run (even if not all pass)
- [x] All acceptance criteria met
