"""
Mock Legal Module for Testing
Implements ILegalModule interface with test data
"""

from typing import Any, Dict, List, Tuple

from backend.interfaces.data_structures import (
    FieldRequirement,
    LogicTreeNode,
    ModuleMetadata,
    ModuleStatus,
    QuestionTemplate,
)
from backend.interfaces.legal_module import ILegalModule


class MockLegalModule(ILegalModule):
    """
    Mock implementation of ILegalModule for testing.
    Returns predictable test data.
    """

    def __init__(self):
        self._metadata = ModuleMetadata(
            module_id="MOCK_MODULE",
            module_name="Mock Legal Module for Testing",
            version="1.0.0",
            status=ModuleStatus.ACTIVE,
            author="Test Suite",
            description="Mock module for testing purposes",
            effective_date="2024-01-01",
            last_updated="2024-01-01",
            dependencies=[],
            tags=["test", "mock"],
        )

        self._tree_nodes = [
            LogicTreeNode(
                node_id="MOCK_1",
                citation="Mock Rule 1",
                module_id="MOCK_MODULE",
                what=[{"fact": "test_fact", "value": "test_value"}],
                which=[{"scope": "test", "applies_to": "all"}],
                if_then=[{"condition": "test", "result": "pass"}],
                modality=[{"type": "MUST", "action": "test"}],
                given=[{"assumption": "test_assumption"}],
                why=[{"reason": "test_reason", "policy": "test_policy"}],
            ),
            LogicTreeNode(
                node_id="MOCK_2",
                citation="Mock Rule 2",
                module_id="MOCK_MODULE",
                what=[{"fact": "another_fact", "value": "another_value"}],
                which=[{"scope": "limited", "applies_to": "specific"}],
                if_then=[{"condition": "complex", "result": "conditional"}],
                modality=[{"type": "MAY", "action": "optional"}],
                given=[{"assumption": "complex_assumption"}],
                why=[{"reason": "legal_precedent", "policy": "fairness"}],
            ),
        ]

        self._field_requirements = [
            FieldRequirement(
                field_name="case_type",
                field_type="enum",
                description="Type of legal case",
                required=True,
                validation_rules={"min_length": 1},
                enum_values=["civil", "criminal", "family"],
                example="civil",
            ),
            FieldRequirement(
                field_name="amount_claimed",
                field_type="number",
                description="Amount claimed in dollars",
                required=True,
                validation_rules={"min": 0, "max": 1000000},
                example="50000",
            ),
            FieldRequirement(
                field_name="court_level",
                field_type="enum",
                description="Level of court",
                required=True,
                validation_rules={},
                enum_values=["district", "high", "appeal"],
                example="district",
            ),
        ]

        self._question_templates = [
            QuestionTemplate(
                field_name="case_type",
                template="What type of case is this? (civil, criminal, or family)",
                priority=1,
                context_required=[],
                validation_pattern="^(civil|criminal|family)$",
            ),
            QuestionTemplate(
                field_name="amount_claimed",
                template="What is the amount claimed in this case?",
                priority=2,
                context_required=["case_type"],
                validation_pattern=r"^\d+(\.\d{2})?$",
            ),
            QuestionTemplate(
                field_name="court_level",
                template="Which court level will hear this case?",
                priority=3,
                context_required=["case_type", "amount_claimed"],
                validation_pattern="^(district|high|appeal)$",
            ),
        ]

    @property
    def metadata(self) -> ModuleMetadata:
        """Return module metadata"""
        return self._metadata

    def get_tree_nodes(self) -> List[LogicTreeNode]:
        """Return pre-built logic tree nodes"""
        return self._tree_nodes

    def get_tree_version(self) -> str:
        """Return tree version"""
        return "1.0.0"

    def get_field_requirements(self) -> List[FieldRequirement]:
        """Return field requirements"""
        return self._field_requirements

    def get_question_templates(self) -> List[QuestionTemplate]:
        """Return question templates"""
        return self._question_templates

    def validate_fields(self, filled_fields: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate filled fields against requirements"""
        errors = []

        for req in self._field_requirements:
            if req.required and req.field_name not in filled_fields:
                errors.append(f"Required field missing: {req.field_name}")

        for req in self._field_requirements:
            if req.field_name in filled_fields and req.enum_values:
                value = filled_fields[req.field_name]
                if value not in req.enum_values:
                    errors.append(
                        f"Invalid value for {req.field_name}: {value}. "
                        f"Must be one of {req.enum_values}"
                    )

        if "amount_claimed" in filled_fields:
            amount = filled_fields["amount_claimed"]
            if not isinstance(amount, (int, float)):
                errors.append("amount_claimed must be a number")
            elif amount < 0:
                errors.append("amount_claimed must be non-negative")

        return (len(errors) == 0, errors)

    def check_completeness(self, filled_fields: Dict[str, Any]) -> float:
        """Calculate information completeness (0.0 to 1.0)"""
        required_fields = [req.field_name for req in self._field_requirements if req.required]
        if not required_fields:
            return 1.0

        filled_required = sum(1 for field in required_fields if field in filled_fields)
        return filled_required / len(required_fields)

    async def calculate(
        self, matched_nodes: List[Any], filled_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform mock calculation"""
        amount = filled_fields.get("amount_claimed", 10000)
        base_cost = amount * 0.1

        return {
            "total_costs": base_cost,
            "breakdown": {
                "filing_fee": base_cost * 0.3,
                "hearing_fee": base_cost * 0.4,
                "miscellaneous": base_cost * 0.3,
            },
            "currency": "SGD",
            "calculation_method": "mock_fixed_percentage",
            "applicable_rules": (
                [node.citation for node in matched_nodes] if matched_nodes else ["MOCK_1"]
            ),
            "notes": "This is a mock calculation for testing purposes",
        }

    async def get_arguments(self, calculation_result: Dict[str, Any]) -> List[str]:
        """Generate court-ready legal arguments"""
        return [
            "Pursuant to Mock Rule 1, the costs are calculated as follows:",
            f"- Total costs amount to ${calculation_result.get('total_costs', 0):.2f}",
            "- This calculation is based on the standardized mock formula",
            "- All fees are in accordance with the mock schedule",
            "The calculation is deterministic and verifiable.",
        ]

    async def get_recommendations(
        self, filled_fields: Dict[str, Any], calculation_result: Dict[str, Any]
    ) -> List[str]:
        """Provide strategic recommendations"""
        amount = filled_fields.get("amount_claimed", 0)
        recommendations = [
            "Consider the cost-benefit analysis of proceeding",
            "Ensure all documentation is properly filed",
        ]

        if amount > 50000:
            recommendations.append("Given the high claim amount, consider engaging senior counsel")

        if filled_fields.get("court_level") == "appeal":
            recommendations.append("Prepare comprehensive grounds of appeal")

        return recommendations

    async def health_check(self) -> bool:
        """Check if module is functioning correctly"""
        try:
            assert len(self._tree_nodes) > 0
            assert len(self._field_requirements) > 0
            assert len(self._question_templates) > 0
            assert self._metadata.module_id == "MOCK_MODULE"
            return True
        except Exception:
            return False
