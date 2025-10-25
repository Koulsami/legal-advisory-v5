"""
Common Services Layer - Shared services for all legal modules.

This layer provides universal services that all legal modules use:
- Logic Tree Framework: Pre-built tree management and validation
- Matching Engine: Multi-dimensional matching for user queries
- Analysis Engine: Orchestrates analysis across modules
- Module Registry: Centralized module management

CRITICAL PRINCIPLE: These services work with PRE-BUILT trees and rules,
NEVER constructing logic dynamically during conversation.
"""

from .logic_tree_framework import LogicTreeFramework

__all__ = [
    "LogicTreeFramework",
]
