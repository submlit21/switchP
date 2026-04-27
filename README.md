# switchP - Network Device Console Management MCP Server

A Model Context Protocol (MCP) server for managing network device consoles via serial port connections. Provides thread-safe multi-session management, command safety guardrails, automatic credential handling, and vendor command extensibility.

## Features

- **Thread-Safe Multi-Session Management**: Supports multiple concurrent client sessions with two-level locking
- **Command Safety Guardrails**: 2-tier risk assessment (SAFE, CONFIRMATION_REQUIRED, BLOCKED) for network device commands
- **Automatic Credential Redaction**: Secure logging with automatic redaction of usernames and passwords
- **Vendor Plugin Architecture**: Extensible system for adding vendor-specific command documentation
- **Persistent Serial Connections**: Maintains connections between commands for performance
- **Interactive Session Support**: Start/stop interactive sessions with custom stop patterns
- **Device Information Detection**: Auto-detects vendor, model, version, and serial numbers
- **Prompt Detection Learning**: Learns device-specific prompt patterns for better automation

## Architecture

The project follows a modular architecture with strict separation of concerns:

```
switchP/
├── core/          # Core business logic: guardrails, state machine
├── session/       # Session management: connection, manager, logger, parser
├── tools/         # MCP tool implementations: execute, device, credentials, interactive
├── resources/     # Vendor command resource system with plugin architecture
├── tests/         # pytest test suite with comprehensive coverage
├── logs/          # Session logging directory (credentials automatically redacted)
├── config.py      # Pydantic Settings configuration
├── server.py      # Main MCP server entry point
└── requirements.txt # Python dependencies
```

## Installation

### Prerequisites

- Python 3.8+
- Serial port access (USB-to-serial adapter or built-in serial port)
- Network device with console port

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd switchP
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (copy `.env.example` to `.env`):
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` file with your serial port settings:
   ```bash
   # Linux: /dev/ttyUSB0 or /dev/ttyACM0
   # macOS: /dev/cu.usbserial-*
   PORT=/dev/ttyUSB0
   
   # Common baud rates: 9600, 19200, 38400, 57600, 115200
   BAUD_RATE=9600
   ```

## Usage

### Starting the MCP Server

Run the server with stdio transport (for MCP client integration):

```bash
python server.py
```

Or run directly for testing:

```bash
python -c "from server import mcp; mcp.run(transport='stdio')"
```

### Available MCP Tools

The server exposes the following MCP tools:

#### 1. `execute_command` - Execute commands with safety guardrails
```json
{
  "command": "show version",
  "client_id": "default",
  "confirm": false
}
```

**Parameters:**
- `command`: Command string to execute (e.g., "show version", "display interface brief")
- `client_id`: Optional client identifier for multi-session management (default: "default")
- `confirm`: Optional confirmation flag for commands that require approval (default: false)

**Response:**
```json
{
  "success": true,
  "message": "Command executed successfully",
  "output": "Cisco IOS Software, C2960 Software...",
  "action": "none"
}
```

#### 2. `get_device_info` - Get device information
```json
{
  "client_id": "default",
  "command": null
}
```

**Parameters:**
- `client_id`: Optional client identifier (default: "default")
- `command`: Optional custom version command (auto-detects if null)

**Response:**
```json
{
  "success": true,
  "message": "Device information retrieved",
  "output": {
    "vendor": "Cisco",
    "model": "C2960",
    "version": "15.2(7)E",
    "serial": "FOC1234ABCD"
  }
}
```

#### 3. `check_connection` - Verify serial port connectivity
```json
{
  "port": null,
  "baud_rate": null
}
```

**Parameters:**
- `port`: Optional serial port path (defaults to configured port)
- `baud_rate`: Optional baud rate (defaults to configured baud rate)

#### 4. `set_credentials` - Store authentication credentials
```json
{
  "username": "admin",
  "password": "password123",
  "client_id": "default"
}
```

**Parameters:**
- `username`: Device login username
- `password`: Device login password
- `client_id`: Client identifier for multi-session support

#### 5. `start_interactive_session` - Start persistent session
```json
{
  "client_id": "default",
  "stop_pattern": null
}
```

**Parameters:**
- `client_id`: Unique client identifier (default: "default")
- `stop_pattern`: Optional custom regex pattern to detect end of command output

#### 6. `stop_interactive_session` - Stop and cleanup session
```json
{
  "client_id": "default"
}
```

### Available MCP Resources

The server provides vendor command documentation via MCP resources:

- `vendor://list` - List all registered vendors
- `vendor://{vendor_name}/info` - Get vendor information
- `vendor://{vendor_name}/commands` - List all commands for a vendor
- `vendor://{vendor_name}/commands/{command_name}` - Get help for specific command
- `vendor://{vendor_name}/table` - Get complete command table

## Command Safety Guardrails

The system implements a 2-tier safety validation system:

### Risk Levels
1. **SAFE**: Read-only commands (e.g., `show version`, `display interface`)
2. **CONFIRMATION_REQUIRED**: Configuration changes (e.g., `configure terminal`, `interface`)
3. **BLOCKED**: Dangerous operations (e.g., `reload`, `write erase`, `delete flash:`)

### Blocked Commands
- `reload`
- `reboot`
- `format`
- `format flash:`
- `erase startup-config`
- `write erase`
- `delete flash:`
- `erase flash:`
- `factory-reset`
- `reset saved-configuration`

### Confirmation-Required Commands
- `interface`
- `shutdown`
- `no shutdown`
- `ip address`
- `vlan`
- `route`
- `ip route`
- `access-list`
- `firewall`
- `nat`
- `security-policy`

## Session Management

### Thread Safety
- **Global Lock**: RLock for session dictionary access
- **Per-Session Lock**: RLock for command serialization within a session
- **Tested**: Stress-tested with 10 concurrent threads

### Session Components
Each session includes:
- `SerialConnection`: Persistent serial port connection
- `DeviceSessionState`: State machine for device conversation flow
- `SessionLogger`: File-based logging with credential redaction
- `PromptDetector`: Prompt pattern detection with learning
- Credentials: Optional username/password storage

### Logging
- Log files: `logs/{client_id}_{timestamp}_{session_id}.log`
- Automatic credential redaction: `***` replaces usernames and passwords
- Flush-after-write for immediate debugging

## Vendor Plugin System

### Adding New Vendors
1. Create a new Python module in `resources/vendor/` (e.g., `cisco.py`)
2. Implement the `VendorCommandTable` abstract base class
3. Expose a `register()` function that calls `resources.register_vendor()`

### Example Vendor Module
```python
from resources.vendor.base import VendorCommandTable

class CiscoCommandTable(VendorCommandTable):
    @property
    def vendor_name(self) -> str:
        return "cisco"
    
    @property
    def vendor_display_name(self) -> str:
        return "Cisco Systems"
    
    def list_commands(self) -> List[str]:
        return ["show version", "show interfaces", "configure terminal"]
    
    def get_command_help(self, command_name: str) -> Optional[str]:
        help_texts = {
            "show version": "Display system hardware and software status",
            "show interfaces": "Display interface status and configuration",
            "configure terminal": "Enter global configuration mode"
        }
        return help_texts.get(command_name)

def register():
    from resources import register_vendor
    register_vendor(CiscoCommandTable())
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_guardrails.py

# Run with verbose output
pytest -v
```

### Test Coverage
- `test_guardrails.py`: Command safety validation tests
- `test_state_machine.py`: Device state transition tests
- `test_session_manager.py`: Thread-safe session management tests

## Development

### Code Conventions
- 4-space indentation (no tabs)
- Type hints on all public methods
- Snake_case for functions/variables, PascalCase for classes/enums
- Explicit `__all__` in `__init__.py` for public API
- All MCP tools return structured JSON with `success`, `message`, `output`, `action` fields

### Project Structure Guidelines
- **Business logic**: `core/` directory only
- **Session management**: `session/` directory only
- **MCP interface**: `tools/` directory only (delegate to core/session)
- **Vendor extensions**: `resources/vendor/` directory
- **Configuration**: `config.py` with Pydantic Settings
- **Entry point**: `server.py` (only initialization and registration)

### Anti-Patterns to Avoid
- Business logic in `server.py` - only initialization allowed
- Missing `__init__.py` in package directories
- Hardcoded configuration values - use environment variables
- Plaintext credential logging - always redact with `***`
- Reconnecting for every command - use persistent connections
- Multiple concurrent commands per session - use per-session locking
- Business logic in tool modules - delegate to core/session

## Troubleshooting

### Common Issues

1. **Serial port not found**
   - Check `PORT` environment variable
   - Verify device is connected: `ls /dev/tty*`
   - Check permissions: `sudo chmod 666 /dev/ttyUSB0`

2. **Connection timeout**
   - Verify baud rate matches device configuration
   - Check cable connection
   - Try different baud rates: 9600, 19200, 38400, 57600, 115200

3. **Permission denied**
   - Add user to dialout group: `sudo usermod -a -G dialout $USER`
   - Log out and back in for group changes to take effect

4. **Command blocked**
   - Check if command is in blocked list
   - Use `confirm=true` for confirmation-required commands
   - Review guardrails configuration in `core/guardrails.py`

### Debug Mode
Enable verbose logging by modifying `session/logger.py`:
```python
# Change log level to DEBUG
logging.basicConfig(level=logging.DEBUG, ...)
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-vendor`
3. Make changes following code conventions
4. Add tests for new functionality
5. Run test suite: `pytest`
6. Submit pull request

### Adding New Features
- **New vendor support**: Add module to `resources/vendor/`
- **New MCP tools**: Add to `tools/` directory
- **Core functionality**: Add to `core/` directory
- **Session management**: Add to `session/` directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenCode](https://github.com/oh-my-opencode/opencode) — the AI orchestration framework that built this project
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for the protocol specification
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) for the Python SDK
- [pyserial](https://github.com/pyserial/pyserial) for serial communication
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management

## Support

For issues, questions, or feature requests:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing tests for usage examples
3. Open an issue on the repository

---

**Note**: This project is designed for network device management in controlled environments. Always follow security best practices and never expose the MCP server to untrusted networks.