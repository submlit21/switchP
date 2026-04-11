from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class VendorCommandTable(ABC):
    """Base abstract class for vendor-specific command tables.

    Each vendor should implement this interface to provide their command
    reference information as MCP resources.
    """

    @property
    @abstractmethod
    def vendor_name(self) -> str:
        """Return the vendor name (e.g., 'cisco', 'huawei', 'hpe')."""
        pass

    @property
    @abstractmethod
    def vendor_display_name(self) -> str:
        """Return the human-readable display name for the vendor."""
        pass

    @abstractmethod
    def list_commands(self) -> List[str]:
        """List all available command names for this vendor."""
        pass

    @abstractmethod
    def get_command_help(self, command_name: str) -> Optional[str]:
        """Get the help documentation for a specific command.

        Args:
            command_name: The name of the command to get help for.

        Returns:
            The help text as a string, or None if the command is not found.
        """
        pass

    @abstractmethod
    def get_command_table(self) -> Dict[str, str]:
        """Get the complete command table mapping command names to help text."""
        pass

    def get_vendor_info(self) -> Dict[str, str]:
        """Get general information about this vendor."""
        return {
            "name": self.vendor_name,
            "display_name": self.vendor_display_name,
            "command_count": str(len(self.list_commands())),
        }
