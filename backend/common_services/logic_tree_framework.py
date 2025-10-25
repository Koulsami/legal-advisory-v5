"""
Logic Tree Framework - Universal tree management system.

This framework manages pre-built logic trees from all legal modules,
providing registration, validation, and completeness calculation.

CRITICAL PRINCIPLE: Trees are PRE-BUILT during module initialization,
NEVER constructed dynamically during conversation.
"""

from typing import List, Dict, Any, Tuple, Optional
import logging

from backend.interfaces.data_structures import LogicTreeNode

logger = logging.getLogger(__name__)


class LogicTreeFramework:
    """
    Universal Logic Tree Framework.
    
    Manages pre-built logic trees from all legal modules in a consistent way.
    Provides validation, indexing, and completeness calculation.
    
    Key Responsibilities:
    1. Register pre-built trees from legal modules
    2. Validate tree structure and relationships
    3. Provide fast node lookups via indexing
    4. Calculate information completeness for routing
    """
    
    def __init__(self):
        """Initialize the Logic Tree Framework."""
        # Storage for registered trees
        self._trees: Dict[str, List[LogicTreeNode]] = {}
        
        # Node index for O(1) lookups: {module_id: {node_id: node}}
        self._node_index: Dict[str, Dict[str, LogicTreeNode]] = {}
        
        logger.info("LogicTreeFramework initialized")
    
    def register_module_tree(
        self,
        module_id: str,
        nodes: List[LogicTreeNode]
    ) -> None:
        """
        Register pre-built tree from a legal module.
        
        CRITICAL: Tree must be PRE-BUILT by the module.
        Trees are NEVER constructed dynamically during conversation.
        
        Args:
            module_id: Unique module identifier (e.g., "ORDER_21", "ORDER_5")
            nodes: List of pre-built LogicTreeNode objects
            
        Raises:
            ValueError: If tree validation fails
            TypeError: If nodes are not LogicTreeNode objects
            
        Example:
            >>> framework = LogicTreeFramework()
            >>> nodes = [LogicTreeNode(...), LogicTreeNode(...)]
            >>> framework.register_module_tree("ORDER_21", nodes)
        """
        # Validate input types
        if not isinstance(module_id, str) or not module_id.strip():
            raise ValueError("module_id must be a non-empty string")
        
        if not isinstance(nodes, list):
            raise TypeError("nodes must be a list of LogicTreeNode objects")
        
        if len(nodes) == 0:
            raise ValueError("Cannot register empty tree - nodes list is empty")
        
        # Validate all nodes are LogicTreeNode objects
        for i, node in enumerate(nodes):
            if not isinstance(node, LogicTreeNode):
                raise TypeError(
                    f"Node at index {i} is not a LogicTreeNode object. "
                    f"Got type: {type(node).__name__}"
                )
        
        # Validate tree structure
        is_valid, errors = self.validate_tree(nodes)
        if not is_valid:
            error_msg = f"Tree validation failed for module '{module_id}':\n"
            error_msg += "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)
        
        # Check if module already registered (warn but allow override)
        if module_id in self._trees:
            logger.warning(
                f"Module '{module_id}' already registered. "
                f"Overwriting with new tree."
            )
        
        # Build node index for fast lookups
        node_index = {}
        for node in nodes:
            node_index[node.node_id] = node
        
        # Store the tree and index
        self._trees[module_id] = nodes
        self._node_index[module_id] = node_index
        
        logger.info(
            f"Registered tree for module '{module_id}': "
            f"{len(nodes)} nodes indexed"
        )
    
    def get_module_tree(
        self,
        module_id: str
    ) -> List[LogicTreeNode]:
        """
        Get registered tree for a module.
        
        Args:
            module_id: Module identifier
            
        Returns:
            List of LogicTreeNode objects for the module
            
        Raises:
            KeyError: If module_id not registered
            
        Example:
            >>> framework = LogicTreeFramework()
            >>> # After registration...
            >>> tree = framework.get_module_tree("ORDER_21")
            >>> print(f"Tree has {len(tree)} nodes")
        """
        if module_id not in self._trees:
            registered = list(self._trees.keys())
            raise KeyError(
                f"Module '{module_id}' not registered. "
                f"Registered modules: {registered}"
            )
        
        return self._trees[module_id]
    
    def validate_tree(
        self,
        nodes: List[LogicTreeNode]
    ) -> Tuple[bool, List[str]]:
        """
        Validate tree structure and relationships.
        
        Validates:
        1. All nodes are LogicTreeNode objects
        2. Node IDs are unique within the tree
        3. All 6 dimensions are present (what, which, if_then, modality, given, why)
        4. Parent/child/related node references exist in tree
        5. No circular relationships
        
        Args:
            nodes: List of tree nodes to validate
            
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
            - is_valid: True if tree is valid, False otherwise
            - errors: List of validation error messages (empty if valid)
            
        Example:
            >>> framework = LogicTreeFramework()
            >>> is_valid, errors = framework.validate_tree(nodes)
            >>> if not is_valid:
            ...     print(f"Validation errors: {errors}")
        """
        errors = []
        
        # Quick check: empty list
        if not nodes:
            errors.append("Cannot validate empty node list")
            return False, errors
        
        # Validation 1: All nodes are LogicTreeNode objects
        for i, node in enumerate(nodes):
            if not isinstance(node, LogicTreeNode):
                errors.append(
                    f"Node at index {i} is not a LogicTreeNode object "
                    f"(got {type(node).__name__})"
                )
        
        # If type validation failed, return early
        if errors:
            return False, errors
        
        # Build node ID set for validation
        node_ids = set()
        duplicate_ids = []
        
        # Validation 2: Node IDs are unique
        for node in nodes:
            if node.node_id in node_ids:
                duplicate_ids.append(node.node_id)
            node_ids.add(node.node_id)
        
        if duplicate_ids:
            errors.append(
                f"Duplicate node IDs found: {duplicate_ids}"
            )
        
        # Validation 3: All 6 dimensions present (check structure)
        for node in nodes:
            missing_dimensions = []
            
            # Check each dimension exists as an attribute
            if not hasattr(node, 'what'):
                missing_dimensions.append('what')
            if not hasattr(node, 'which'):
                missing_dimensions.append('which')
            if not hasattr(node, 'if_then'):
                missing_dimensions.append('if_then')
            if not hasattr(node, 'modality'):
                missing_dimensions.append('modality')
            if not hasattr(node, 'given'):
                missing_dimensions.append('given')
            if not hasattr(node, 'why'):
                missing_dimensions.append('why')
            
            if missing_dimensions:
                errors.append(
                    f"Node '{node.node_id}' missing dimensions: "
                    f"{missing_dimensions}"
                )
            
            # Check dimensions are lists
            for dim in ['what', 'which', 'if_then', 'modality', 'given', 'why']:
                if hasattr(node, dim):
                    value = getattr(node, dim)
                    if not isinstance(value, list):
                        errors.append(
                            f"Node '{node.node_id}' dimension '{dim}' "
                            f"must be a list (got {type(value).__name__})"
                        )
        
        # Validation 4: Parent/child/related node references exist
        for node in nodes:
            # Check parent nodes
            if hasattr(node, 'parent_nodes'):
                for parent_id in node.parent_nodes:
                    if parent_id not in node_ids:
                        errors.append(
                            f"Node '{node.node_id}' references non-existent "
                            f"parent '{parent_id}'"
                        )
            
            # Check child nodes
            if hasattr(node, 'child_nodes'):
                for child_id in node.child_nodes:
                    if child_id not in node_ids:
                        errors.append(
                            f"Node '{node.node_id}' references non-existent "
                            f"child '{child_id}'"
                        )
            
            # Check related nodes
            if hasattr(node, 'related_nodes'):
                for related_id in node.related_nodes:
                    if related_id not in node_ids:
                        errors.append(
                            f"Node '{node.node_id}' references non-existent "
                            f"related node '{related_id}'"
                        )
        
        # Validation 5: Check for circular relationships (basic check)
        # We check if any node is its own ancestor
        def has_circular_reference(node_id: str, visited: set) -> bool:
            """Check if node has circular parent relationship."""
            if node_id in visited:
                return True
            
            # Find the node
            node = None
            for n in nodes:
                if n.node_id == node_id:
                    node = n
                    break
            
            if not node:
                return False
            
            visited.add(node_id)
            
            # Check all parents
            for parent_id in node.parent_nodes:
                if has_circular_reference(parent_id, visited.copy()):
                    return True
            
            return False
        
        for node in nodes:
            if has_circular_reference(node.node_id, set()):
                errors.append(
                    f"Circular relationship detected involving node "
                    f"'{node.node_id}'"
                )
        
        # Return validation result
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def calculate_completeness(
        self,
        filled_fields: Dict[str, Any],
        required_fields: List[str]
    ) -> float:
        """
        Calculate information completeness ratio.
        
        Used by ALL modules to determine when enough information
        has been gathered to route to specialized analysis.
        
        Args:
            filled_fields: Dictionary of information gathered from user
            required_fields: List of field names required for analysis
            
        Returns:
            Float between 0.0 and 1.0 representing completeness
            - 0.0 = No fields filled
            - 1.0 = All required fields filled
            - 0.7 = 70% of required fields filled
            
        Example:
            >>> framework = LogicTreeFramework()
            >>> filled = {"court_level": "High Court", "party_type": "Plaintiff"}
            >>> required = ["court_level", "party_type", "case_type"]
            >>> completeness = framework.calculate_completeness(filled, required)
            >>> print(f"Completeness: {completeness:.0%}")
            Completeness: 67%
        """
        # Handle edge cases
        if not required_fields:
            return 1.0  # No fields required = 100% complete
        
        if not filled_fields:
            return 0.0  # No fields filled = 0% complete
        
        # Count how many required fields are filled
        # A field is considered "filled" if:
        # 1. It exists in filled_fields
        # 2. Its value is not None
        # 3. Its value is not an empty string
        # 4. If it's a list/dict, it's not empty
        filled_count = 0
        for field in required_fields:
            if field in filled_fields:
                value = filled_fields[field]
                
                # Check if value is "truthy" (not None, not empty)
                if value is not None:
                    # Handle different types
                    if isinstance(value, str):
                        if value.strip():  # Non-empty string
                            filled_count += 1
                    elif isinstance(value, (list, dict)):
                        if len(value) > 0:  # Non-empty collection
                            filled_count += 1
                    else:
                        # For other types (bool, int, float, etc.)
                        filled_count += 1
        
        # Calculate ratio
        completeness = filled_count / len(required_fields)
        
        return completeness
    
    def get_node(
        self,
        module_id: str,
        node_id: str
    ) -> Optional[LogicTreeNode]:
        """
        Get a specific node by ID (O(1) lookup).
        
        Args:
            module_id: Module identifier
            node_id: Node identifier
            
        Returns:
            LogicTreeNode if found, None otherwise
            
        Example:
            >>> framework = LogicTreeFramework()
            >>> node = framework.get_node("ORDER_21", "R3-2")
            >>> if node:
            ...     print(f"Found: {node.citation}")
        """
        # Check if module is registered
        if module_id not in self._node_index:
            logger.warning(f"Module '{module_id}' not registered")
            return None
        
        # Get node from index
        return self._node_index[module_id].get(node_id)
    
    def get_registered_modules(self) -> List[str]:
        """
        Get list of all registered module IDs.
        
        Returns:
            List of module IDs
            
        Example:
            >>> framework = LogicTreeFramework()
            >>> modules = framework.get_registered_modules()
            >>> print(f"Registered: {modules}")
            Registered: ['ORDER_21', 'ORDER_5', 'ORDER_19']
        """
        return list(self._trees.keys())
    
    def get_tree_stats(self, module_id: str) -> Dict[str, Any]:
        """
        Get statistics about a registered tree.
        
        Args:
            module_id: Module identifier
            
        Returns:
            Dictionary with tree statistics:
            - node_count: Total number of nodes
            - avg_children: Average children per node
            - max_depth: Maximum tree depth
            - dimension_usage: Count of nodes using each dimension
            
        Raises:
            KeyError: If module_id not registered
        """
        if module_id not in self._trees:
            raise KeyError(f"Module '{module_id}' not registered")
        
        nodes = self._trees[module_id]
        
        # Calculate basic stats
        node_count = len(nodes)
        
        # Calculate average children per node
        total_children = sum(len(node.child_nodes) for node in nodes)
        avg_children = total_children / node_count if node_count > 0 else 0
        
        # Calculate dimension usage
        dimension_usage = {
            'what': 0,
            'which': 0,
            'if_then': 0,
            'modality': 0,
            'given': 0,
            'why': 0
        }
        
        for node in nodes:
            if len(node.what) > 0:
                dimension_usage['what'] += 1
            if len(node.which) > 0:
                dimension_usage['which'] += 1
            if len(node.if_then) > 0:
                dimension_usage['if_then'] += 1
            if len(node.modality) > 0:
                dimension_usage['modality'] += 1
            if len(node.given) > 0:
                dimension_usage['given'] += 1
            if len(node.why) > 0:
                dimension_usage['why'] += 1
        
        # Calculate max depth (simple BFS approach)
        max_depth = self._calculate_max_depth(nodes)
        
        return {
            'node_count': node_count,
            'avg_children': round(avg_children, 2),
            'max_depth': max_depth,
            'dimension_usage': dimension_usage
        }
    
    def _calculate_max_depth(self, nodes: List[LogicTreeNode]) -> int:
        """
        Calculate maximum tree depth using BFS.
        
        Args:
            nodes: List of tree nodes
            
        Returns:
            Maximum depth (root nodes have depth 0)
        """
        if not nodes:
            return 0
        
        # Build adjacency map
        children_map = {}
        for node in nodes:
            children_map[node.node_id] = node.child_nodes
        
        # Find root nodes (nodes with no parents)
        all_node_ids = {node.node_id for node in nodes}
        has_parent = set()
        for node in nodes:
            for child_id in node.child_nodes:
                has_parent.add(child_id)
        
        root_ids = all_node_ids - has_parent
        
        if not root_ids:
            # No clear roots, tree might be circular or all nodes are connected
            # Return 0 as we can't determine depth
            return 0
        
        # BFS to find max depth
        max_depth = 0
        visited = set()
        queue = [(root_id, 0) for root_id in root_ids]
        
        while queue:
            node_id, depth = queue.pop(0)
            
            if node_id in visited:
                continue
            
            visited.add(node_id)
            max_depth = max(max_depth, depth)
            
            # Add children to queue
            if node_id in children_map:
                for child_id in children_map[node_id]:
                    if child_id not in visited:
                        queue.append((child_id, depth + 1))
        
        return max_depth
