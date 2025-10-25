"""
Legal Module Emulator for testing.

Provides a minimal logic tree for testing without full module implementation.
"""

from typing import Dict, List, Any, Optional, Tuple
from backend.interfaces.legal_module import ILegalModule
from backend.interfaces.data_structures import (
    ModuleMetadata, 
    ModuleStatus,
    LogicTreeNode, 
    FieldRequirement,
    QuestionTemplate,
    MatchResult
)


class ModuleEmulator(ILegalModule):
    """
    Simple legal module emulator with minimal logic tree.
    
    Useful for testing without full Order 21 implementation.
    """
    
    def __init__(self, module_name: str = "EmulatorModule"):
        """Initialize module emulator"""
        self._module_name = module_name
        self._tree_nodes = self._create_minimal_tree()
        self._query_count = 0
    
    def _create_minimal_tree(self) -> List[LogicTreeNode]:
        """Create a minimal 3-node logic tree for testing"""
        nodes = [
            LogicTreeNode(
                node_id="node_1",
                citation="TEST-1",
                module_id="TEST_MODULE",
                what=[{
                    "proposition": "case_type_identification",
                    "text": "Identify the type of case"
                }]
            ),
            LogicTreeNode(
                node_id="node_2",
                citation="TEST-2",
                module_id="TEST_MODULE",
                what=[{
                    "proposition": "amount_calculation",
                    "text": "Calculate the amount in dispute"
                }]
            ),
            LogicTreeNode(
                node_id="node_3",
                citation="TEST-3",
                module_id="TEST_MODULE",
                which=[{
                    "entity": "party_count",
                    "text": "Count the number of parties involved"
                }]
            )
        ]
        return nodes
    
    # ============================================
    # METADATA
    # ============================================
    
    @property
    def metadata(self) -> ModuleMetadata:
        """Return module metadata"""
        return ModuleMetadata(
            module_id="TEST_MODULE",
            module_name=self._module_name,
            version="1.0.0-emulator",
            status=ModuleStatus.ACTIVE,
            author="Test System",
            description="Emulator module for testing",
            effective_date="2024-01-01",
            last_updated="2024-10-25",
            dependencies=[],
            tags=["testing", "emulator"]
        )
    
    # ============================================
    # TREE MANAGEMENT
    # ============================================
    
    def get_tree_nodes(self) -> List[LogicTreeNode]:
        """Return PRE-BUILT logic tree nodes for this module"""
        return self._tree_nodes
    
    def get_tree_version(self) -> str:
        """Return version of the logic tree"""
        return "1.0.0"
    
    # ============================================
    # FIELD REQUIREMENTS
    # ============================================
    
    def get_field_requirements(self) -> List[FieldRequirement]:
        """Return list of all fields required by this module"""
        return [
            FieldRequirement(
                field_name="case_type",
                field_type="string",
                description="Type of case (civil/criminal)",
                required=True,
                validation_rules={"min_length": 1},
                enum_values=["civil", "criminal"],
                example="civil"
            ),
            FieldRequirement(
                field_name="amount",
                field_type="number",
                description="Amount in dispute",
                required=True,
                validation_rules={"min": 0},
                example="10000"
            ),
            FieldRequirement(
                field_name="party_count",
                field_type="integer",
                description="Number of parties",
                required=False,
                validation_rules={"min": 1},
                example="2"
            )
        ]
    
    def get_question_templates(self) -> List[QuestionTemplate]:
        """Return template questions for information gathering"""
        return [
            QuestionTemplate(
                field_name="case_type",
                template="What type of case is this?",
                priority=1,
                context_required=[],
                validation_pattern=None
            ),
            QuestionTemplate(
                field_name="amount",
                template="What is the amount in dispute?",
                priority=2,
                context_required=["case_type"],
                validation_pattern=r"^\d+(\.\d{2})?$"
            ),
            QuestionTemplate(
                field_name="party_count",
                template="How many parties are involved?",
                priority=3,
                context_required=[],
                validation_pattern=r"^\d+$"
            )
        ]
    
    # ============================================
    # VALIDATION
    # ============================================
    
    def validate_fields(self, filled_fields: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate filled fields meet module requirements"""
        errors = []
        
        # Check required fields
        if "case_type" not in filled_fields:
            errors.append("case_type is required")
        elif filled_fields["case_type"] not in ["civil", "criminal"]:
            errors.append("case_type must be 'civil' or 'criminal'")
        
        if "amount" not in filled_fields:
            errors.append("amount is required")
        elif not isinstance(filled_fields["amount"], (int, float)) or filled_fields["amount"] < 0:
            errors.append("amount must be a positive number")
        
        # Validate optional fields
        if "party_count" in filled_fields:
            if not isinstance(filled_fields["party_count"], int) or filled_fields["party_count"] < 1:
                errors.append("party_count must be at least 1")
        
        is_valid = len(errors) == 0
        return (is_valid, errors)
    
    def check_completeness(self, filled_fields: Dict[str, Any]) -> float:
        """Calculate information completeness (0.0 to 1.0)"""
        required_fields = ["case_type", "amount"]
        optional_fields = ["party_count"]
        
        required_filled = sum(1 for f in required_fields if f in filled_fields)
        optional_filled = sum(1 for f in optional_fields if f in filled_fields)
        
        # Required fields worth 80%, optional fields worth 20%
        required_score = (required_filled / len(required_fields)) * 0.8
        optional_score = (optional_filled / len(optional_fields)) * 0.2
        
        return required_score + optional_score
    
    # ============================================
    # SPECIALIZED LOGIC
    # ============================================
    
    async def calculate(
        self, 
        matched_nodes: List[MatchResult], 
        filled_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform module-specific specialized calculation"""
        self._query_count += 1
        
        amount = filled_fields.get("amount", 0)
        party_count = filled_fields.get("party_count", 1)
        case_type = filled_fields.get("case_type", "unknown")
        
        # Simple mock calculation
        base_fee = amount * 0.1  # 10% of amount
        party_multiplier = 1 + ((party_count - 1) * 0.2)  # 20% extra per additional party
        total = base_fee * party_multiplier
        
        result = {
            "base_amount": amount,
            "case_type": case_type,
            "party_count": party_count,
            "base_fee": base_fee,
            "party_multiplier": party_multiplier,
            "total_cost": total,
            "calculation_method": "emulator_mock",
            "matched_nodes_count": len(matched_nodes)
        }
        
        return result
    
    async def get_arguments(
        self, 
        calculation_result: Dict[str, Any], 
        filled_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate legal arguments based on calculation"""
        return {
            "primary_argument": f"Based on emulator calculation for {filled_fields.get('case_type', 'unknown')} case",
            "supporting_points": [
                f"Amount in dispute: ${calculation_result.get('base_amount', 0):,.2f}",
                f"Party count: {calculation_result.get('party_count', 1)}",
                f"Calculated total cost: ${calculation_result.get('total_cost', 0):,.2f}"
            ],
            "citations": ["TEST-1", "TEST-2", "TEST-3"],
            "precedents": []
        }
    
    async def get_recommendations(
        self, 
        calculation_result: Dict[str, Any], 
        filled_fields: Dict[str, Any]
    ) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = [
            "This is an emulator-generated recommendation",
            f"Consider the total estimated cost of ${calculation_result.get('total_cost', 0):,.2f}",
            "Review the calculation with actual legal module for accurate results"
        ]
        
        if calculation_result.get("party_count", 1) > 2:
            recommendations.append("Multiple parties may increase complexity and costs")
        
        return recommendations
    
    # ============================================
    # EMULATOR-SPECIFIC METHODS
    # ============================================
    
    async def health_check(self) -> bool:
        """Check emulator health"""
        return True
    
    def get_query_count(self) -> int:
        """Get number of queries made"""
        return self._query_count
    
    def reset(self):
        """Reset emulator state"""
        self._query_count = 0
