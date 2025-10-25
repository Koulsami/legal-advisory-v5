"""
Mock Calculator for Testing
Implements ICalculator interface
"""

from typing import Any, Dict, List

from backend.interfaces.calculator import ICalculator


class MockCalculator(ICalculator):
    """
    Mock implementation of ICalculator for testing.
    Performs simple mock calculations.
    """

    def __init__(self):
        self._calculation_count = 0

    async def calculate(
        self, matched_nodes: List[Any], filled_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform mock calculation.
        """
        self._calculation_count += 1

        # Simple mock calculation
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
            "calculation_method": "mock_calculator",
            "applicable_rules": (
                [node.citation for node in matched_nodes] if matched_nodes else ["MOCK_RULE"]
            ),
            "notes": "Mock calculation for testing",
        }

    async def health_check(self) -> bool:
        """Check if calculator is functioning"""
        try:
            result = await self.calculate([], {"amount_claimed": 1000})
            return "total_costs" in result
        except Exception:
            return False

    def get_calculation_count(self) -> int:
        """Get number of calculations performed"""
        return self._calculation_count

    def reset_calculation_count(self) -> None:
        """Reset calculation counter"""
        self._calculation_count = 0
