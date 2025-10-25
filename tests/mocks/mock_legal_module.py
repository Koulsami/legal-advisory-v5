"""
Mock Legal Module for Testing
"""

from typing import Any, Dict, List, Tuple

from backend.interfaces import (
    FieldRequirement,
    ILegalModule,
    LogicTreeNode,
    MatchResult,
    ModuleMetadata,
    ModuleStatus,
    QuestionTemplate,
)


class MockLegalModule(ILegalModule):
    """Mock implementation of ILegalModule for testing"""

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            module_id="MOCK_MODULE",
            module_name="Mock Legal Module",
            version="1.0.0",
            status=ModuleStatus.ACTIVE,
            author="Test Suite",
            description="Mock module for testing",
            effective_date="2024-01-01",
            last_updated="2024-10-25",
            dependencies=[],
            tags=["test", "mock"],
        )

    def get_tree_nodes(self) -> List[LogicTreeNode]:
        return [
            LogicTreeNode(
                node_id="mock_1",
                citation="Mock Rule 1",
                module_id="MOCK_MODULE",
                what=[{"definition": "Test definition"}],
            ),
            LogicTreeNode(
                node_id="mock_2",
                citation="Mock Rule 2",
                module_id="MOCK_MODULE",
                if_then=[{"condition": "test", "result": "pass"}],
            ),
        ]

    def get_tree_version(self) -> str:
        return "1.0.0"

    def get_field_requirements(self) -> List[FieldRequirement]:
        return [
            FieldRequirement(
                field_name="test_field",
                field_type="string",
                description="Test field",
                required=True,
                validation_rules={"min_length": 1},
            )
        ]

    def get_question_templates(self) -> List[QuestionTemplate]:
        return [
            QuestionTemplate(
                field_name="test_field", template="What is your test value?", priority=1
            )
        ]

    def validate_fields(self, filled_fields: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        if "test_field" not in filled_fields:
            errors.append("test_field is required")
        return len(errors) == 0, errors

    def check_completeness(self, filled_fields: Dict[str, Any]) -> Tuple[float, List[str]]:
        required = ["test_field"]
        filled = sum(1 for f in required if f in filled_fields)
        missing = [f for f in required if f not in filled_fields]
        return filled / len(required), missing

    def calculate(self, filled_fields: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": "mock_calculation", "value": 100.0}

    def get_arguments(
        self, calculation_result: Dict[str, Any], filled_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"arguments": ["Mock argument 1", "Mock argument 2"]}

    def get_recommendations(self, calculation_result: Dict[str, Any]) -> List[str]:
        return ["Mock recommendation 1", "Mock recommendation 2"]
