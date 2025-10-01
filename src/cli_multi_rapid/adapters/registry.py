#!/usr/bin/env python3
"""
Registry alias for compatibility.

Provides AdapterRegistry import path expected by some modules/tests.
"""

from .adapter_registry import AdapterRegistry, registry  # re-export

__all__ = ["AdapterRegistry", "registry"]

