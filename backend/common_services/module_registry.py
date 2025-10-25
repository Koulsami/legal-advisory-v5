"""
Module Registry - Central registry for all legal modules.

This registry manages the lifecycle of legal modules (Order 21, Order 5, etc.),
providing registration, discovery, and health checking capabilities.

CRITICAL PRINCIPLE: Modules are registered at system startup with PRE-BUILT trees.
The registry NEVER constructs modules dynamically.
"""

from typing import Dict, List, Optional, Set
import logging
from datetime import datetime
from dataclasses import dataclass

from backend.interfaces.legal_module import ILegalModule
from backend.interfaces.data_structures import ModuleMetadata, ModuleStatus
from backend.common_services.logic_tree_framework import LogicTreeFramework

logger = logging.getLogger(__name__)


@dataclass
class ModuleRegistration:
    """Registration record for a legal module"""
    module: ILegalModule
    metadata: ModuleMetadata
    registered_at: datetime
    tree_node_count: int
    health_status: str = "unknown"
    last_health_check: Optional[datetime] = None


class ModuleRegistry:
    """
    Central registry for all legal modules.

    Manages the lifecycle of legal modules including registration,
    discovery, health checking, and integration with the Logic Tree Framework.

    Key Features:
    - Module registration and validation
    - Module discovery and lookup
    - Lifecycle management (REGISTERED, ACTIVE, DISABLED, DEPRECATED)
    - Automatic tree registration with LogicTreeFramework
    - Health checking for all modules
    - Statistics and monitoring

    Example:
        >>> registry = ModuleRegistry(tree_framework)
        >>> registry.register_module(order21_module)
        >>> module = registry.get_module("ORDER_21")
        >>> all_modules = registry.list_modules(status=ModuleStatus.ACTIVE)
    """

    def __init__(self, tree_framework: LogicTreeFramework):
        """
        Initialize the Module Registry.

        Args:
            tree_framework: LogicTreeFramework instance for tree management

        Raises:
            TypeError: If tree_framework is not a LogicTreeFramework instance
        """
        if not isinstance(tree_framework, LogicTreeFramework):
            raise TypeError(
                f"tree_framework must be LogicTreeFramework, got {type(tree_framework)}"
            )

        self.tree_framework = tree_framework

        # Registry storage: {module_id: ModuleRegistration}
        self._modules: Dict[str, ModuleRegistration] = {}

        # Module indices for fast lookup
        self._modules_by_status: Dict[ModuleStatus, Set[str]] = {
            ModuleStatus.REGISTERED: set(),
            ModuleStatus.ACTIVE: set(),
            ModuleStatus.DISABLED: set(),
            ModuleStatus.DEPRECATED: set()
        }

        self._modules_by_tag: Dict[str, Set[str]] = {}

        # Statistics
        self._registration_count = 0
        self._total_tree_nodes = 0

        logger.info("ModuleRegistry initialized")

    def register_module(
        self,
        module: ILegalModule,
        auto_activate: bool = True
    ) -> None:
        """
        Register a legal module with the registry.

        This method:
        1. Validates the module implements ILegalModule
        2. Extracts and validates metadata
        3. Registers the module's tree with LogicTreeFramework
        4. Adds module to registry
        5. Optionally activates the module

        Args:
            module: ILegalModule instance to register
            auto_activate: Automatically set status to ACTIVE (default: True)

        Raises:
            TypeError: If module doesn't implement ILegalModule
            ValueError: If module_id already registered
            RuntimeError: If tree registration fails

        Example:
            >>> order21 = Order21Module()
            >>> registry.register_module(order21)
            >>> assert registry.is_registered("ORDER_21")
        """
        # Validate module type
        if not isinstance(module, ILegalModule):
            raise TypeError(
                f"module must implement ILegalModule, got {type(module)}"
            )

        # Get and validate metadata
        metadata = module.metadata
        module_id = metadata.module_id

        if not module_id or not module_id.strip():
            raise ValueError("module_id cannot be empty")

        # Check if already registered
        if module_id in self._modules:
            raise ValueError(
                f"Module '{module_id}' is already registered"
            )

        # Get tree nodes from module
        try:
            tree_nodes = module.get_tree_nodes()
        except Exception as e:
            raise RuntimeError(
                f"Failed to get tree nodes from module '{module_id}': {e}"
            )

        if not tree_nodes:
            logger.warning(
                f"Module '{module_id}' has no tree nodes (empty tree)"
            )

        # Register tree with LogicTreeFramework
        try:
            self.tree_framework.register_module_tree(module_id, tree_nodes)
            logger.info(
                f"Registered {len(tree_nodes)} tree nodes for module '{module_id}'"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to register tree for module '{module_id}': {e}"
            )

        # Create registration record
        registration = ModuleRegistration(
            module=module,
            metadata=metadata,
            registered_at=datetime.now(),
            tree_node_count=len(tree_nodes)
        )

        # Store module
        self._modules[module_id] = registration
        self._registration_count += 1
        self._total_tree_nodes += len(tree_nodes)

        # Update indices
        self._add_to_status_index(module_id, metadata.status)
        self._add_to_tag_indices(module_id, metadata.tags)

        logger.info(
            f"Module '{module_id}' registered successfully "
            f"(status: {metadata.status.value}, nodes: {len(tree_nodes)})"
        )

        # Auto-activate if requested
        if auto_activate and metadata.status == ModuleStatus.REGISTERED:
            self.set_module_status(module_id, ModuleStatus.ACTIVE)

    def get_module(self, module_id: str) -> Optional[ILegalModule]:
        """
        Get a registered module by ID.

        Args:
            module_id: Unique module identifier

        Returns:
            ILegalModule instance if found, None otherwise

        Example:
            >>> module = registry.get_module("ORDER_21")
            >>> if module:
            ...     print(module.metadata.module_name)
        """
        registration = self._modules.get(module_id)
        return registration.module if registration else None

    def get_module_metadata(self, module_id: str) -> Optional[ModuleMetadata]:
        """
        Get metadata for a registered module.

        Args:
            module_id: Unique module identifier

        Returns:
            ModuleMetadata if found, None otherwise
        """
        registration = self._modules.get(module_id)
        return registration.metadata if registration else None

    def is_registered(self, module_id: str) -> bool:
        """
        Check if a module is registered.

        Args:
            module_id: Unique module identifier

        Returns:
            True if module is registered, False otherwise
        """
        return module_id in self._modules

    def list_modules(
        self,
        status: Optional[ModuleStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[str]:
        """
        List registered module IDs with optional filtering.

        Args:
            status: Filter by module status (optional)
            tags: Filter by tags - returns modules with ANY of these tags (optional)

        Returns:
            List of module IDs matching the criteria

        Example:
            >>> # All active modules
            >>> active = registry.list_modules(status=ModuleStatus.ACTIVE)
            >>> # All modules tagged with 'costs'
            >>> costs_modules = registry.list_modules(tags=["costs"])
        """
        module_ids = set(self._modules.keys())

        # Filter by status if specified
        if status is not None:
            module_ids &= self._modules_by_status.get(status, set())

        # Filter by tags if specified
        if tags:
            tag_matches = set()
            for tag in tags:
                tag_matches |= self._modules_by_tag.get(tag, set())
            module_ids &= tag_matches

        return sorted(list(module_ids))

    def list_all_modules(self) -> List[ModuleMetadata]:
        """
        Get metadata for all registered modules.

        Returns:
            List of ModuleMetadata objects for all registered modules

        Example:
            >>> for meta in registry.list_all_modules():
            ...     print(f"{meta.module_id}: {meta.module_name}")
        """
        return [
            reg.metadata
            for reg in self._modules.values()
        ]

    def set_module_status(
        self,
        module_id: str,
        new_status: ModuleStatus
    ) -> None:
        """
        Update the status of a registered module.

        Args:
            module_id: Module to update
            new_status: New status to set

        Raises:
            KeyError: If module_id not registered
            ValueError: If status transition is invalid

        Example:
            >>> registry.set_module_status("ORDER_21", ModuleStatus.ACTIVE)
            >>> registry.set_module_status("ORDER_5", ModuleStatus.DISABLED)
        """
        if module_id not in self._modules:
            raise KeyError(f"Module '{module_id}' is not registered")

        registration = self._modules[module_id]
        old_status = registration.metadata.status

        # Validate status transition
        if not self._is_valid_status_transition(old_status, new_status):
            raise ValueError(
                f"Invalid status transition for '{module_id}': "
                f"{old_status.value} -> {new_status.value}"
            )

        # Update status in metadata
        registration.metadata.status = new_status

        # Update indices
        self._remove_from_status_index(module_id, old_status)
        self._add_to_status_index(module_id, new_status)

        logger.info(
            f"Module '{module_id}' status changed: "
            f"{old_status.value} -> {new_status.value}"
        )

    def unregister_module(self, module_id: str) -> None:
        """
        Unregister a module from the registry.

        This removes the module from the registry but does NOT
        remove its tree from the LogicTreeFramework.

        Args:
            module_id: Module to unregister

        Raises:
            KeyError: If module_id not registered

        Example:
            >>> registry.unregister_module("OLD_MODULE")
        """
        if module_id not in self._modules:
            raise KeyError(f"Module '{module_id}' is not registered")

        registration = self._modules[module_id]

        # Remove from indices
        self._remove_from_status_index(module_id, registration.metadata.status)
        self._remove_from_tag_indices(module_id, registration.metadata.tags)

        # Remove from registry
        del self._modules[module_id]

        logger.info(f"Module '{module_id}' unregistered")

    async def health_check_module(self, module_id: str) -> bool:
        """
        Perform health check on a specific module.

        Args:
            module_id: Module to check

        Returns:
            True if module is healthy, False otherwise

        Raises:
            KeyError: If module_id not registered
        """
        if module_id not in self._modules:
            raise KeyError(f"Module '{module_id}' is not registered")

        registration = self._modules[module_id]
        module = registration.module

        try:
            # Call module's health_check method
            is_healthy = await module.health_check()

            # Update registration record
            registration.health_status = "healthy" if is_healthy else "unhealthy"
            registration.last_health_check = datetime.now()

            return is_healthy

        except Exception as e:
            logger.error(f"Health check failed for '{module_id}': {e}")
            registration.health_status = "error"
            registration.last_health_check = datetime.now()
            return False

    async def health_check_all(self) -> Dict[str, bool]:
        """
        Perform health check on all registered modules.

        Returns:
            Dictionary mapping module_id to health status (True/False)

        Example:
            >>> results = await registry.health_check_all()
            >>> for module_id, is_healthy in results.items():
            ...     print(f"{module_id}: {'✓' if is_healthy else '✗'}")
        """
        results = {}

        for module_id in self._modules.keys():
            try:
                is_healthy = await self.health_check_module(module_id)
                results[module_id] = is_healthy
            except Exception as e:
                logger.error(f"Health check failed for '{module_id}': {e}")
                results[module_id] = False

        healthy_count = sum(1 for h in results.values() if h)
        total_count = len(results)

        logger.info(
            f"Health check complete: {healthy_count}/{total_count} modules healthy"
        )

        return results

    def get_statistics(self) -> Dict[str, any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with statistics about registered modules

        Example:
            >>> stats = registry.get_statistics()
            >>> print(f"Total modules: {stats['total_modules']}")
            >>> print(f"Active modules: {stats['active_modules']}")
        """
        return {
            "total_modules": len(self._modules),
            "total_registrations": self._registration_count,
            "total_tree_nodes": self._total_tree_nodes,
            "modules_by_status": {
                status.value: len(module_ids)
                for status, module_ids in self._modules_by_status.items()
            },
            "active_modules": len(self._modules_by_status[ModuleStatus.ACTIVE]),
            "disabled_modules": len(self._modules_by_status[ModuleStatus.DISABLED]),
            "unique_tags": len(self._modules_by_tag),
            "tree_framework_modules": len(self.tree_framework.get_registered_modules())
        }

    def get_module_registration_info(
        self,
        module_id: str
    ) -> Optional[Dict[str, any]]:
        """
        Get detailed registration information for a module.

        Args:
            module_id: Module to get info for

        Returns:
            Dictionary with registration details, or None if not found
        """
        if module_id not in self._modules:
            return None

        registration = self._modules[module_id]

        return {
            "module_id": module_id,
            "module_name": registration.metadata.module_name,
            "version": registration.metadata.version,
            "status": registration.metadata.status.value,
            "registered_at": registration.registered_at.isoformat(),
            "tree_node_count": registration.tree_node_count,
            "health_status": registration.health_status,
            "last_health_check": (
                registration.last_health_check.isoformat()
                if registration.last_health_check
                else None
            ),
            "tags": registration.metadata.tags,
            "dependencies": registration.metadata.dependencies
        }

    # ========================================
    # PRIVATE HELPER METHODS
    # ========================================

    def _is_valid_status_transition(
        self,
        old_status: ModuleStatus,
        new_status: ModuleStatus
    ) -> bool:
        """
        Validate if a status transition is allowed.

        Allowed transitions:
        - REGISTERED -> ACTIVE
        - ACTIVE -> DISABLED
        - DISABLED -> ACTIVE
        - Any -> DEPRECATED (one-way)
        """
        # Can always transition to same status (no-op)
        if old_status == new_status:
            return True

        # Can always deprecate
        if new_status == ModuleStatus.DEPRECATED:
            return True

        # Cannot un-deprecate
        if old_status == ModuleStatus.DEPRECATED:
            return False

        # Define allowed transitions
        allowed = {
            ModuleStatus.REGISTERED: {ModuleStatus.ACTIVE},
            ModuleStatus.ACTIVE: {ModuleStatus.DISABLED},
            ModuleStatus.DISABLED: {ModuleStatus.ACTIVE}
        }

        return new_status in allowed.get(old_status, set())

    def _add_to_status_index(self, module_id: str, status: ModuleStatus):
        """Add module to status index"""
        self._modules_by_status[status].add(module_id)

    def _remove_from_status_index(self, module_id: str, status: ModuleStatus):
        """Remove module from status index"""
        self._modules_by_status[status].discard(module_id)

    def _add_to_tag_indices(self, module_id: str, tags: List[str]):
        """Add module to tag indices"""
        for tag in tags:
            if tag not in self._modules_by_tag:
                self._modules_by_tag[tag] = set()
            self._modules_by_tag[tag].add(module_id)

    def _remove_from_tag_indices(self, module_id: str, tags: List[str]):
        """Remove module from tag indices"""
        for tag in tags:
            if tag in self._modules_by_tag:
                self._modules_by_tag[tag].discard(module_id)
                # Clean up empty tag sets
                if not self._modules_by_tag[tag]:
                    del self._modules_by_tag[tag]
