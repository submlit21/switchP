import importlib
import pkgutil
from typing import Any

from .vendor.base import VendorCommandTable


__all__ = [
    "VendorCommandTable",
    "register_vendor",
    "register_vendor_resources",
    "get_vendor_registry",
]

# Registry of vendor command tables discovered at runtime
_vendor_registry: list[VendorCommandTable] = []


def register_vendor(vendor: VendorCommandTable) -> None:
    """Register a new vendor command table.

    This is called by vendor modules when they are loaded to add their
    command table to the registry.

    Args:
        vendor: The vendor command table instance to register.
    """
    _vendor_registry.append(vendor)


def get_vendor_registry() -> list[VendorCommandTable]:
    """Get the current vendor registry.

    Returns:
        List of all registered vendor command tables.
    """
    return _vendor_registry.copy()


def _discover_vendors() -> None:
    """Discover and auto-register vendor modules in the resources.vendor package."""
    from . import vendor

    for _, module_name, _ in pkgutil.iter_modules(vendor.__path__):
        if module_name != "base":
            try:
                module = importlib.import_module(
                    f".{module_name}", package=vendor.__package__
                )
                if hasattr(module, "register"):
                    module.register()
            except Exception as e:
                # Skip problematic modules but don't fail everything
                continue


def register_vendor_resources(mcp: Any) -> None:
    """Register all vendor command tables as MCP resources.

    This function should be called from the main server.py to:
    1. Auto-discover all vendor modules
    2. Register each vendor's command table as an MCP resource
    3. Register the vendor list resource

    Args:
        mcp: The MCP server instance to register resources with.
    """
    # Auto-discover and load vendor modules
    _discover_vendors()

    # Get all registered vendors
    vendors = get_vendor_registry()

    # Register vendor list resource
    @mcp.resource("vendor://list")
    def list_vendors() -> str:
        """List all registered vendors with their metadata."""
        output = []
        for vendor in vendors:
            info = vendor.get_vendor_info()
            output.append(
                f"- {info['display_name']} ({info['name']}): {info['command_count']} commands"
            )
        return "\n".join(output)

    # Register individual vendor resources
    for vendor in vendors:
        vendor_name = vendor.vendor_name

        # Register vendor info resource
        @mcp.resource(f"vendor://{vendor_name}/info")
        def get_vendor_info(vendor=vendor) -> str:
            """Get information about a specific vendor."""
            info = vendor.get_vendor_info()
            return "\n".join([f"{key}: {value}" for key, value in info.items()])

        # Register command list resource
        @mcp.resource(f"vendor://{vendor_name}/commands")
        def list_vendor_commands(vendor=vendor) -> str:
            """List all commands available for a specific vendor."""
            commands = vendor.list_commands()
            return "\n".join(commands)

        # Register individual command help resource
        @mcp.resource(f"vendor://{vendor_name}/commands/{{command_name}}")
        def get_command_help(command_name: str, vendor=vendor) -> str:
            """Get help documentation for a specific command."""
            help_text = vendor.get_command_help(command_name)
            if help_text is None:
                return f"Command '{command_name}' not found for vendor '{vendor_name}'"
            return help_text

        # Register full command table resource
        @mcp.resource(f"vendor://{vendor_name}/table")
        def get_full_table(vendor=vendor) -> str:
            """Get the complete command table for a vendor."""
            table = vendor.get_command_table()
            output = []
            for cmd, help in sorted(table.items()):
                output.append(f"## {cmd}")
                output.append(help)
                output.append("")
            return "\n".join(output)
