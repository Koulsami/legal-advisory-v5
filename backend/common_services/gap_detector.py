"""
Gap Detector for Logic Tree
Legal Advisory System v5.0

Identifies missing information required by the logic tree to make decisions.
Part of the Hybrid AI + Logic Tree architecture.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from backend.interfaces.data_structures import LogicTreeNode


@dataclass
class Gap:
    """Represents a missing piece of information."""

    field_name: str
    field_type: str
    description: str
    legal_basis: str
    priority: str  # "required", "recommended", "optional"
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "field_name": self.field_name,
            "field_type": self.field_type,
            "description": self.description,
            "legal_basis": self.legal_basis,
            "priority": self.priority,
            "context": self.context or {},
        }


@dataclass
class ValidationResult:
    """Result of validating filled fields against logic tree."""

    complete: bool
    completeness_score: float  # 0.0 to 1.0
    gaps: List[Gap]
    current_path: List[str]  # Node IDs traversed
    next_decision_point: Optional[str] = None
    can_calculate: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "complete": self.complete,
            "completeness_score": self.completeness_score,
            "gaps": [g.to_dict() for g in self.gaps],
            "current_path": self.current_path,
            "next_decision_point": self.next_decision_point,
            "can_calculate": self.can_calculate,
        }


class GapDetector:
    """
    Detects gaps in information by traversing the logic tree.

    This is the ACCURACY component of the hybrid architecture:
    - AI extracts information naturally
    - GapDetector validates completeness
    - If gaps found, AI asks about them naturally
    """

    def __init__(self, logic_tree_framework):
        """
        Initialize gap detector.

        Args:
            logic_tree_framework: LogicTreeFramework instance
        """
        self.tree_framework = logic_tree_framework

    def validate_against_tree(
        self, module_id: str, filled_fields: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate filled fields against the module's requirements.

        This is called AFTER AI extracts information from user message.
        It checks if we have enough to make a calculation.

        Args:
            module_id: Module identifier (e.g., "ORDER_21")
            filled_fields: Dictionary of fields filled so far

        Returns:
            ValidationResult with gaps if incomplete
        """
        # Import here to avoid circular dependency
        from backend.common_services.module_registry import get_global_registry

        registry = get_global_registry()
        if not registry:
            # No registry available - can't validate
            return ValidationResult(
                complete=False,
                completeness_score=0.0,
                gaps=[],
                current_path=[],
                next_decision_point=None,
                can_calculate=False,
            )

        # Get the module
        module = registry.get_module(module_id)
        if not module:
            return ValidationResult(
                complete=False,
                completeness_score=0.0,
                gaps=[],
                current_path=[],
                next_decision_point=None,
                can_calculate=False,
            )

        # Get field requirements
        field_requirements = module.get_field_requirements()

        # Find gaps - missing required fields
        gaps = []
        required_fields = [fr for fr in field_requirements if fr.required]

        for field_req in required_fields:
            field_name = field_req.field_name

            # Check if field is filled
            if field_name not in filled_fields or filled_fields[field_name] is None:
                gap = Gap(
                    field_name=field_name,
                    field_type=field_req.field_type,
                    description=field_req.description,
                    legal_basis="Order 21",  # TODO: Get from module metadata
                    priority="required",
                    context={
                        "already_filled": list(filled_fields.keys()),
                    },
                )
                gaps.append(gap)

        # Calculate completeness
        total_required = len(required_fields)
        filled_required = total_required - len(gaps)
        completeness_score = filled_required / total_required if total_required > 0 else 0.0

        # Determine if we can calculate
        complete = len(gaps) == 0
        can_calculate = complete

        # Next decision point is first gap
        next_decision_point = gaps[0].field_name if gaps else None

        return ValidationResult(
            complete=complete,
            completeness_score=completeness_score,
            gaps=gaps,
            current_path=[module_id],  # Simple path for now
            next_decision_point=next_decision_point,
            can_calculate=can_calculate,
        )

    def _get_decision_field(self, node: LogicTreeNode) -> Optional[str]:
        """
        Extract the decision field from a node.

        Examples:
        - "IF court_level = High Court" → "court_level"
        - "WHAT is the claim amount?" → "claim_amount"
        """
        # Check node metadata
        if hasattr(node, "decision_field") and node.decision_field:
            return node.decision_field

        # Try to infer from question text
        if node.question_text:
            # Simple heuristic: look for common patterns
            text = node.question_text.lower()

            if "court level" in text or "which court" in text:
                return "court_level"
            if "claim amount" in text or "how much" in text:
                return "claim_amount"
            if "trial days" in text or "how many days" in text:
                return "trial_days"
            if "case type" in text or "judgment type" in text:
                return "case_type"
            if "liquidated" in text or "claim nature" in text:
                return "claim_nature"

        # Check children conditions to infer field
        if node.children:
            for child in node.children:
                if hasattr(child, "condition") and child.condition:
                    # Try to extract field from condition
                    # e.g., "court_level=High Court" → "court_level"
                    if "=" in child.condition:
                        field = child.condition.split("=")[0].strip()
                        return field

        return None

    def _infer_field_type(self, field_name: str) -> str:
        """Infer the type of a field from its name."""
        type_mapping = {
            "court_level": "choice",
            "case_type": "choice",
            "claim_nature": "choice",
            "claim_amount": "number",
            "trial_days": "number",
            "represented_status": "choice",
            "defendant_count": "number",
        }
        return type_mapping.get(field_name, "text")

    def _find_matching_child(self, node: LogicTreeNode, value: Any) -> Optional[LogicTreeNode]:
        """
        Find child node that matches the given value.

        Args:
            node: Parent node
            value: Field value to match

        Returns:
            Matching child node or None
        """
        if not node.children:
            return None

        # Try exact match first
        for child in node.children:
            if not hasattr(child, "condition"):
                continue

            condition = child.condition

            # Handle different condition formats
            if "=" in condition:
                # Format: "field=value"
                _, expected_value = condition.split("=", 1)
                expected_value = expected_value.strip()

                if str(value).lower() == expected_value.lower():
                    return child

            elif str(value).lower() in condition.lower():
                # Value mentioned in condition
                return child

        # If no exact match, return first child (default path)
        return node.children[0] if node.children else None

    def get_required_fields(self, module_id: str) -> List[str]:
        """
        Get all fields that might be required for this module.

        Useful for AI to know what to look for.

        Args:
            module_id: Module identifier

        Returns:
            List of field names that may be required
        """
        try:
            tree_nodes = self.tree_framework.get_module_tree(module_id)
            root_node = tree_nodes[0] if tree_nodes else None
        except (KeyError, IndexError):
            root_node = None

        if not root_node:
            return []

        required_fields = set()

        def traverse(node: LogicTreeNode):
            if not node:
                return

            # Extract decision field if this is a decision node
            if node.node_type == "DECISION":
                field = self._get_decision_field(node)
                if field:
                    required_fields.add(field)

            # Traverse children
            if node.children:
                for child in node.children:
                    traverse(child)

        traverse(root_node)
        return list(required_fields)
