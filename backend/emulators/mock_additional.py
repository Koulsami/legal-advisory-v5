"""
Mock Tree Framework and Analysis Engine for Testing
Implements ITreeFramework and IAnalysisEngine interfaces
"""
from typing import List, Dict, Any, Tuple
from backend.interfaces.tree import ITreeFramework
from backend.interfaces.analysis import IAnalysisEngine
from backend.interfaces.data_structures import LogicTreeNode
from backend.interfaces.legal_module import ILegalModule


class MockTreeFramework(ITreeFramework):
    """
    Mock implementation of ITreeFramework for testing.
    Manages trees in memory for testing purposes.
    """
    
    def __init__(self):
        self._trees: Dict[str, List[LogicTreeNode]] = {}
    
    # ============================================
    # TREE MANAGEMENT
    # ============================================
    
    def build_tree(
        self,
        module_id: str,
        nodes: List[LogicTreeNode]
    ) -> None:
        """
        Register/build tree for a module.
        
        Args:
            module_id: Module identifier
            nodes: Tree nodes
        """
        # Validate tree before storing
        is_valid, errors = self._validate_tree_structure(nodes)
        if not is_valid:
            raise ValueError(f"Invalid tree for {module_id}: {errors}")
        
        self._trees[module_id] = nodes
    
    def query_tree(
        self,
        module_id: str,
        filters: Dict[str, Any] = None
    ) -> List[LogicTreeNode]:
        """
        Query tree nodes by module ID and optional filters.
        
        Args:
            module_id: Module identifier
            filters: Optional filters to apply
            
        Returns:
            List of matching nodes
        """
        if module_id not in self._trees:
            raise KeyError(f"Module {module_id} not registered")
        
        nodes = self._trees[module_id]
        
        # Apply filters if provided
        if filters:
            filtered_nodes = []
            for node in nodes:
                if self._matches_filters(node, filters):
                    filtered_nodes.append(node)
            return filtered_nodes
        
        return nodes
    
    def _validate_tree_structure(
        self,
        nodes: List[LogicTreeNode]
    ) -> Tuple[bool, List[str]]:
        """
        Validate tree structure.
        """
        errors = []
        
        if not nodes:
            errors.append("Tree must have at least one node")
        
        # Check for unique node IDs
        node_ids = [node.node_id for node in nodes]
        if len(node_ids) != len(set(node_ids)):
            errors.append("Duplicate node IDs found")
        
        # Check each node has required fields
        for node in nodes:
            if not node.node_id:
                errors.append("Node missing node_id")
            if not node.citation:
                errors.append(f"Node {node.node_id} missing citation")
            if not node.module_id:
                errors.append(f"Node {node.node_id} missing module_id")
        
        return (len(errors) == 0, errors)
    
    def _matches_filters(
        self,
        node: LogicTreeNode,
        filters: Dict[str, Any]
    ) -> bool:
        """
        Check if node matches filters.
        """
        for key, value in filters.items():
            if key == "node_id" and node.node_id != value:
                return False
            if key == "citation" and node.citation != value:
                return False
            if key == "source_type" and node.source_type != value:
                return False
        return True
    
    # ============================================
    # UTILITY
    # ============================================
    
    async def health_check(self) -> bool:
        """Check if tree framework is functioning"""
        try:
            # Test with minimal tree
            test_node = LogicTreeNode(
                node_id="TEST",
                citation="Test",
                module_id="TEST"
            )
            self.build_tree("TEST_MODULE", [test_node])
            result = self.query_tree("TEST_MODULE")
            # Clean up
            del self._trees["TEST_MODULE"]
            return len(result) == 1
        except Exception:
            return False
    
    def get_registered_modules(self) -> List[str]:
        """Get list of registered module IDs"""
        return list(self._trees.keys())
    
    def clear_tree(self, module_id: str) -> None:
        """Remove a tree from the framework"""
        if module_id in self._trees:
            del self._trees[module_id]


class MockAnalysisEngine(IAnalysisEngine):
    """
    Mock implementation of IAnalysisEngine for testing.
    Orchestrates analysis with predictable results.
    """
    
    def __init__(self):
        self._analysis_count = 0
    
    # ============================================
    # ANALYSIS
    # ============================================
    
    async def analyze(
        self,
        module: ILegalModule,
        filled_fields: Dict[str, Any],
        enhance_with_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Orchestrate complete analysis.
        
        Process:
        1. Get tree nodes from module
        2. Validate completeness
        3. Perform specialized calculation
        4. Get arguments and recommendations
        5. AI enhancement (if enabled)
        6. Return comprehensive result
        """
        self._analysis_count += 1
        
        # Get tree nodes
        tree_nodes = module.get_tree_nodes()
        
        # Check completeness
        completeness = module.check_completeness(filled_fields)
        
        # Validate fields
        is_valid, validation_errors = module.validate_fields(filled_fields)
        
        if not is_valid:
            return {
                "success": False,
                "error": "Validation failed",
                "validation_errors": validation_errors,
                "completeness": completeness
            }
        
        # Perform calculation (mock matching)
        calculation_result = await module.calculate(
            matched_nodes=tree_nodes[:2],  # Use first 2 nodes
            filled_fields=filled_fields
        )
        
        # Get arguments and recommendations
        arguments = module.get_arguments(calculation_result)
        recommendations = module.get_recommendations(filled_fields, calculation_result)
        
        # Build comprehensive result
        result = {
            "success": True,
            "completeness": completeness,
            "calculation": calculation_result,
            "arguments": arguments,
            "recommendations": recommendations,
            "module_id": module.metadata.module_id,
            "module_version": module.get_tree_version(),
            "enhanced_with_ai": enhance_with_ai
        }
        
        # Add AI enhancement if requested
        if enhance_with_ai:
            result["ai_insights"] = self._generate_mock_ai_insights(filled_fields, calculation_result)
        
        return result
    
    def _generate_mock_ai_insights(
        self,
        filled_fields: Dict[str, Any],
        calculation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mock AI insights.
        """
        return {
            "summary": "This is a mock AI-enhanced summary of the legal analysis.",
            "key_points": [
                "The calculation is based on established legal precedents",
                "Consider the cost-benefit ratio",
                "Early settlement may be advisable"
            ],
            "risk_assessment": "Medium risk based on the case parameters",
            "confidence": 0.85
        }
    
    # ============================================
    # HEALTH CHECK
    # ============================================
    
    async def health_check(self) -> bool:
        """Check if analysis engine is functioning"""
        try:
            # Would need a real module to test properly
            # For now, just return True
            return True
        except Exception:
            return False
    
    # ============================================
    # UTILITY
    # ============================================
    
    def get_analysis_count(self) -> int:
        """Get number of analyze() calls made"""
        return self._analysis_count
    
    def reset_analysis_count(self) -> None:
        """Reset analysis counter"""
        self._analysis_count = 0
