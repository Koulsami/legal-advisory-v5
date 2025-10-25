"""
ILegalModule Interface
Legal Advisory System v5.0

All legal modules (Order 21, Order 5, etc.) must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from .data_structures import (
    FieldRequirement,
    LogicTreeNode,
    MatchResult,
    ModuleMetadata,
    QuestionTemplate,
)


class ILegalModule(ABC):
    """
    Abstract base class that ALL legal modules must implement.

    This is the core contract for pluggable legal modules.
    Each module (Order 21, Order 5, Order 19, etc.) implements this interface.
    """

    # ============================================
    # METADATA
    # ============================================

    @property
    @abstractmethod
    def metadata(self) -> ModuleMetadata:
        """
        Return module metadata.

        Returns:
            ModuleMetadata with module info

        Example:
            ModuleMetadata(
                module_id="ORDER_21",
                module_name="Rules of Court 2021 - Order 21: Costs",
                version="1.0.0",
                status=ModuleStatus.ACTIVE,
                author="Legal Advisory System",
                description="Cost calculation for Singapore legal matters",
                effective_date="2021-04-01",
                last_updated="2024-10-25",
                dependencies=[],
                tags=["costs", "singapore", "civil"]
            )
        """
        pass

    # ============================================
    # TREE MANAGEMENT
    # ============================================

    @abstractmethod
    def get_tree_nodes(self) -> List[LogicTreeNode]:
        """
        Return PRE-BUILT logic tree nodes for this module.

        CRITICAL: Tree must be PRE-BUILT during module initialization.
        Trees are NEVER constructed dynamically during conversation.

        Returns:
            List of LogicTreeNode objects

        Example for Order 21:
            - 29 rules from Order 21
            - 9 scenarios from Appendix 1
            - Total: 38 pre-built nodes
        """
        pass

    @abstractmethod
    def get_tree_version(self) -> str:
        """
        Return version of the logic tree.

        Returns:
            Semantic version string (e.g., "1.2.0")
        """
        pass

    # ============================================
    # FIELD REQUIREMENTS
    # ============================================

    @abstractmethod
    def get_field_requirements(self) -> List[FieldRequirement]:
        """
        Return list of all fields required by this module.

        Returns:
            List of FieldRequirement objects

        Example:
            [
                FieldRequirement(
                    field_name="court_level",
                    field_type="enum",
                    description="Level of court",
                    required=True,
                    validation_rules={"min_length": 1},
                    enum_values=["High Court", "District Court", "Magistrates"]
                )
            ]
        """
        pass

    @abstractmethod
    def get_question_templates(self) -> List[QuestionTemplate]:
        """
        Return template questions for information gathering.

        Returns:
            List of QuestionTemplate objects
        """
        pass

    # ============================================
    # VALIDATION
    # ============================================

    @abstractmethod
    def validate_fields(self, filled_fields: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate filled fields meet module requirements.

        Args:
            filled_fields: Dictionary of field_name -> value

        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        pass

    @abstractmethod
    def check_completeness(self, filled_fields: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Calculate information completeness and identify missing fields.

        Args:
            filled_fields: Currently filled fields

        Returns:
            Tuple of (completeness_score, missing_fields)
            - completeness_score: Float between 0.0 (no info) and 1.0 (complete)
            - missing_fields: List of field names that are missing or incomplete

        Example:
            >>> score, missing = module.check_completeness({"court": "High Court"})
            >>> # (0.3, ["party_type", "case_type", "amount"])
        """
        pass

    # ============================================
    # SPECIALIZED LOGIC (100% Accurate)
    # ============================================

    @abstractmethod
    def calculate(self, filled_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform module-specific specialized calculation.

        THIS IS WHERE 100% ACCURACY HAPPENS.

        Note: This is a synchronous method. The calculation logic is deterministic
        and does not require async operations.

        Args:
            filled_fields: All information gathered from user

        Returns:
            Dictionary containing calculation results

        Example:
            >>> result = module.calculate({
            ...     "court_level": "High Court",
            ...     "case_type": "default_judgment",
            ...     "amount": 10000
            ... })
            >>> # {"total_costs": 1500, "breakdown": {...}}
        """
        pass

    @abstractmethod
    def get_arguments(
        self, calculation_result: Dict[str, Any], filled_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate legal arguments based on calculation.

        Note: This is a synchronous method. Arguments are generated from
        pre-built templates and calculation results.

        Args:
            calculation_result: Results from calculate()
            filled_fields: Original user information

        Returns:
            Dictionary with arguments and supporting citations

        Example:
            >>> args = module.get_arguments(calc_result, filled_fields)
            >>> # {"main_argument": "...", "supporting_citations": [...]}
        """
        pass

    @abstractmethod
    def get_recommendations(self, calculation_result: Dict[str, Any]) -> List[str]:
        """
        Generate strategic recommendations based on calculation.

        Note: This is a synchronous method. Recommendations are generated from
        pre-built rules and calculation results.

        Args:
            calculation_result: Results from calculate()

        Returns:
            List of recommendation strings

        Example:
            >>> recs = module.get_recommendations(calc_result)
            >>> # ["File within 14 days", "Include all supporting documents"]
        """
        pass
