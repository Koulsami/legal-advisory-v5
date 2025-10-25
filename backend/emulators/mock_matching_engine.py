"""
Mock Matching Engine for Testing
Implements IMatchingEngine interface with predictable matching logic
"""

from typing import Any, Dict, List

from backend.interfaces.data_structures import LogicTreeNode, MatchResult
from backend.interfaces.matching import IMatchingEngine


class MockMatchingEngine(IMatchingEngine):
    """
    Mock implementation of IMatchingEngine for testing.
    Returns predictable match results.
    """

    def __init__(self):
        self._match_count = 0

    async def match(
        self, filled_fields: Dict[str, Any], tree_nodes: List[LogicTreeNode], threshold: float = 0.6
    ) -> List[MatchResult]:
        """Perform mock matching of fields to tree nodes"""
        self._match_count += 1
        matches = []

        for node in tree_nodes:
            score = self._calculate_mock_score(filled_fields, node)

            if score >= threshold:
                matches.append(
                    MatchResult(
                        node_id=node.node_id,
                        node=node,
                        match_score=score,
                        matched_fields=filled_fields.copy(),
                        missing_fields=self._identify_missing_fields(filled_fields, node),
                        confidence=score,
                        reasoning=f"Mock match with confidence {score:.2f}",
                    )
                )

        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches

    def _calculate_mock_score(self, filled_fields: Dict[str, Any], node: LogicTreeNode) -> float:
        """Calculate a mock confidence score"""
        score = 0.5
        field_count = len(filled_fields)
        if field_count >= 1:
            score += 0.1
        if field_count >= 2:
            score += 0.15
        if field_count >= 3:
            score += 0.2
        return min(score, 0.95)

    def _identify_missing_fields(
        self, filled_fields: Dict[str, Any], node: LogicTreeNode
    ) -> List[str]:
        """Identify fields that could improve the match"""
        all_possible_fields = ["case_type", "amount_claimed", "court_level", "trial_duration"]
        missing = [field for field in all_possible_fields if field not in filled_fields]
        return missing[:3]

    async def health_check(self) -> bool:
        """Check if matching engine is functioning"""
        try:
            test_fields = {"test": "value"}
            test_node = LogicTreeNode(node_id="TEST", citation="Test", module_id="TEST")
            result = await self.match(
                filled_fields=test_fields, tree_nodes=[test_node], threshold=0.0
            )
            return isinstance(result, list) and len(result) > 0
        except Exception:
            return False

    def get_match_count(self) -> int:
        """Get number of match() calls made"""
        return self._match_count

    def reset_match_count(self) -> None:
        """Reset match counter"""
        self._match_count = 0
