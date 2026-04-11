# PROJECT KNOWLEDGE BASE

**Generated:** 2026-04-11
**Commit:** n/a (not a git repo)
**Branch:** n/a

## OVERVIEW
Vendor command resource system implementing plugin architecture for network device command documentation via MCP resources.

## STRUCTURE
```
resources/
├── __init__.py          # Vendor registry and auto-discovery system
└── vendor/              # Vendor plugin system
    ├── __init__.py      # Public API export
    └── base.py          # Abstract base class for vendor implementations
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add new vendor plugin | `vendor/` | Create new Python module implementing `VendorCommandTable` |
| Vendor base class | `vendor/base.py` | Abstract base class defining vendor plugin interface |
| Auto-discovery system | `__init__.py` | Runtime scanning and registration of vendor modules |
| MCP resource registration | `__init__.py:57` | `register_vendor_resources()` for server integration |
| Vendor registry access | `__init__.py:31` | `get_vendor_registry()` returns all registered vendors |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `VendorCommandTable` | ABC | `vendor/base.py:5` | Abstract base class for vendor plugin implementations |
| `register_vendor` | function | `__init__.py:19` | Manual vendor registration (called by vendor modules) |
| `_discover_vendors` | function | `__init__.py:40` | Auto-discovery of vendor modules via package scanning |

## CONVENTIONS
- Vendor modules must be placed in `vendor/` directory
- Each vendor must implement `VendorCommandTable` and expose `register()` function
- Vendor names should be lowercase (e.g., 'cisco', 'huawei', 'hpe')
- All vendor modules except `base.py` are auto-discovered at runtime

## ANTI-PATTERNS (THIS DIRECTORY)
- Business logic in vendor modules - only command documentation allowed
- Hardcoded vendor lists - use auto-discovery via `_discover_vendors()`
- Direct MCP registration in vendor modules - use `register_vendor_resources()` instead
- Missing `register()` function - required for auto-discovery
- Complex state in vendor implementations - should be stateless command tables only

## UNIQUE STYLES
- Plugin architecture: auto-discovery via `pkgutil.iter_modules()`
- Runtime registration: vendors self-register via `register()` function
- MCP resource generation: dynamic creation of `vendor://*` resources
- Loose coupling: vendors don't need to know about each other
- Error tolerance: problematic vendor modules are skipped, not fatal

## NOTES
- The system automatically discovers all Python modules in `vendor/` (except `base.py`)
- MCP resources are created dynamically for each vendor at `vendor://{vendor_name}/...`
- Designed for extensibility: adding new vendors requires only a new module, no other code changes
