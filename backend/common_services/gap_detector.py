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
        Validate filled fields against the module's logic tree.

        This is called AFTER AI extracts information from user message.
        It checks if we have enough to make a calculation.

        Args:
            module_id: Module identifier (e.g., "ORDER_21")
            filled_fields: Dictionary of fields filled so far

        Returns:
            ValidationResult with gaps if incomplete
        """
        # Get the decision tree for this module
        root_node = self.tree_framework.get_tree_root(module_id)

        if not root_node:
            return ValidationResult(
                complete=False,
                completeness_score=0.0,
                gaps=[],
                current_path=[],
                next_decision_point=None,
                can_calculate=False,
            )

        # Traverse tree and find gaps
        gaps = []
        path = []
        current_node = root_node

        while current_node:
            path.append(current_node.node_id)

            # Check if this is a calculation node (leaf)
            if current_node.node_type == "CALCULATION":
                # We've reached a calculation node - we're complete!
                return ValidationResult(
                    complete=True,
                    completeness_score=1.0,
                    gaps=[],
                    current_path=path,
                    next_decision_point=None,
                    can_calculate=True,
                )

            # Check if this is a decision node
            if current_node.node_type == "DECISION":
                # What field does this decision require?
                decision_field = self._get_decision_field(current_node)

                if not decision_field:
                    # No clear decision field - move to first child
                    if current_node.children:
                        current_node = current_node.children[0]
                    else:
                        break
                    continue

                # Do we have this field?
                if decision_field not in filled_fields:
                    # GAP FOUND!
                    gap = Gap(
                        field_name=decision_field,
                        field_type=self._infer_field_type(decision_field),
                        description=current_node.question_text or f"Need {decision_field}",
                        legal_basis=current_node.legal_reference or "Order 21",
                        priority="required",
                        context={
                            "node_id": current_node.node_id,
                            "already_filled": list(filled_fields.keys()),
                        },
                    )
                    gaps.append(gap)

                    # Calculate completeness score
                    completeness = len(filled_fields) / (len(filled_fields) + len(gaps))

                    return ValidationResult(
                        complete=False,
                        completeness_score=completeness,
                        gaps=gaps,
                        current_path=path,
                        next_decision_point=decision_field,
                        can_calculate=False,
                    )

                # We have the field - navigate to appropriate child
                field_value = filled_fields[decision_field]
                next_node = self._find_matching_child(current_node, field_value)

                if not next_node:
                    # No matching child - might be an unexpected value
                    gap = Gap(
                        field_name=decision_field,
                        field_type=self._infer_field_type(decision_field),
                        description=f"Value '{field_value}' not recognized for {decision_field}",
                        legal_basis=current_node.legal_reference or "Order 21",
                        priority="required",
                        context={
                            "node_id": current_node.node_id,
                            "provided_value": field_value,
                            "expected_values": [
                                child.condition for child in current_node.children
                            ],
                        },
                    )
                    gaps.append(gap)

                    return ValidationResult(
                        complete=False,
                        completeness_score=0.5,
                        gaps=gaps,
                        current_path=path,
                        next_decision_point=decision_field,
                        can_calculate=False,
                    )

                # Move to next node
                current_node = next_node

            else:
                # Other node type - move to first child if exists
                if current_node.children:
                    current_node = current_node.children[0]
                else:
                    break

        # Reached end without finding calculation node
        return ValidationResult(
            complete=False,
            completeness_score=len(filled_fields) / (len(filled_fields) + 1),
            gaps=gaps or [
                Gap(
                    field_name="unknown",
                    field_type="unknown",
                    description="Unable to determine next step",
                    legal_basis="Order 21",
                    priority="required",
                )
            ],
            current_path=path,
            next_decision_point=None,
            can_calculate=False,
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
        root_node = self.tree_framework.get_tree_root(module_id)
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
