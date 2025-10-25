"""
Universal Matching Engine - Multi-dimensional scoring for legal logic trees.

This engine matches user-provided information (filled_fields) against LogicTreeNode objects
using a sophisticated 6-dimension scoring system:

1. WHAT: Facts, propositions, conclusions
2. WHICH: Scope, entities, classifications
3. IF-THEN: Conditional logic, implications
4. MODALITY: Obligations (MUST, MAY, CAN, CANNOT)
5. GIVEN: Assumptions, premises, context
6. WHY: Reasoning, rationale, policy

CRITICAL PRINCIPLE: This engine works with PRE-BUILT trees.
It NEVER constructs logic dynamically.
"""

from typing import List, Dict, Any, Tuple, Set
import logging
from dataclasses import dataclass

from backend.interfaces.matching import IMatchingEngine
from backend.interfaces.data_structures import LogicTreeNode, MatchResult

logger = logging.getLogger(__name__)


@dataclass
class DimensionScore:
    """Score for a single dimension"""
    dimension_name: str
    score: float  # 0.0 to 1.0
    matched_items: List[str]
    total_items: int
    reasoning: str


class UniversalMatchingEngine(IMatchingEngine):
    """
    Universal Matching Engine for legal logic trees.

    Uses weighted multi-dimensional scoring across the 6 universal dimensions.
    Works with ANY legal module (Order 21, Order 5, etc.).

    Key Features:
    - Multi-dimensional scoring (6 dimensions)
    - Configurable dimension weights
    - Threshold filtering
    - Detailed match explanations
    - Confidence calculation based on data quality

    Example:
        >>> engine = UniversalMatchingEngine()
        >>> filled = {"court_level": "High Court", "party_type": "Plaintiff"}
        >>> results = await engine.match(tree_nodes, filled, threshold=0.6)
        >>> for result in results:
        ...     print(f"{result.node_id}: {result.match_score:.2f}")
    """

    # Default dimension weights (sum to 1.0)
    DEFAULT_WEIGHTS = {
        "WHAT": 0.25,    # Facts and propositions
        "WHICH": 0.20,   # Classifications and scope
        "IF_THEN": 0.20, # Conditional logic
        "MODALITY": 0.15,# Requirements
        "GIVEN": 0.10,   # Context and assumptions
        "WHY": 0.10      # Rationale and policy
    }

    def __init__(
        self,
        dimension_weights: Dict[str, float] = None,
        use_fuzzy_matching: bool = False,
        case_sensitive: bool = False
    ):
        """
        Initialize the Universal Matching Engine.

        Args:
            dimension_weights: Custom weights for dimensions (must sum to 1.0)
            use_fuzzy_matching: Enable fuzzy string matching (default: False)
            case_sensitive: Enable case-sensitive matching (default: False)

        Raises:
            ValueError: If dimension_weights don't sum to 1.0
        """
        self.weights = dimension_weights or self.DEFAULT_WEIGHTS.copy()
        self.use_fuzzy_matching = use_fuzzy_matching
        self.case_sensitive = case_sensitive

        # Validate weights
        if abs(sum(self.weights.values()) - 1.0) > 0.001:
            raise ValueError(
                f"Dimension weights must sum to 1.0, got {sum(self.weights.values())}"
            )

        # Statistics
        self._match_count = 0
        self._total_nodes_evaluated = 0

        logger.info(f"UniversalMatchingEngine initialized with weights: {self.weights}")

    async def match(
        self,
        tree_nodes: List[LogicTreeNode],
        filled_fields: Dict[str, Any],
        threshold: float = 0.6
    ) -> List[MatchResult]:
        """
        Match filled fields to tree nodes using 6-dimension scoring.

        This is the main entry point for the matching engine.
        Scores each node across all 6 dimensions, combines with weights,
        filters by threshold, and returns sorted results.

        Args:
            tree_nodes: List of LogicTreeNode objects to match against
            filled_fields: Dictionary of user-provided information
            threshold: Minimum match score to include (0.0-1.0)

        Returns:
            List of MatchResult objects, sorted by match_score descending

        Example:
            >>> filled = {
            ...     "court_level": "High Court",
            ...     "party_type": "Plaintiff",
            ...     "case_type": "Contract dispute"
            ... }
            >>> results = await engine.match(nodes, filled, threshold=0.7)
            >>> print(f"Found {len(results)} matches above 0.7")
        """
        self._match_count += 1
        self._total_nodes_evaluated += len(tree_nodes)

        if not tree_nodes:
            logger.warning("match() called with empty tree_nodes list")
            return []

        if not filled_fields:
            logger.warning("match() called with empty filled_fields dict")
            return []

        # Validate threshold
        if not (0.0 <= threshold <= 1.0):
            raise ValueError(f"threshold must be between 0.0 and 1.0, got {threshold}")

        results = []

        for node in tree_nodes:
            # Score node across all dimensions
            dimension_scores = self._score_node(node, filled_fields)

            # Calculate weighted overall score
            overall_score = self._calculate_overall_score(dimension_scores)

            # Filter by threshold
            if overall_score >= threshold:
                # Calculate confidence and missing fields
                confidence = self._calculate_confidence(dimension_scores, filled_fields)
                missing_fields = self._identify_missing_fields(node, filled_fields)

                # Generate explanation
                reasoning = self._generate_reasoning(dimension_scores, overall_score)

                # Create MatchResult
                result = MatchResult(
                    node_id=node.node_id,
                    node=node,
                    match_score=overall_score,
                    matched_fields=filled_fields.copy(),
                    missing_fields=missing_fields,
                    confidence=confidence,
                    reasoning=reasoning
                )
                results.append(result)

        # Sort by match_score descending
        results.sort(key=lambda x: x.match_score, reverse=True)

        logger.debug(
            f"Matched {len(results)}/{len(tree_nodes)} nodes above threshold {threshold}"
        )

        return results

    def _score_node(
        self,
        node: LogicTreeNode,
        filled_fields: Dict[str, Any]
    ) -> List[DimensionScore]:
        """
        Score a node across all 6 dimensions.

        Returns list of DimensionScore objects, one per dimension.
        """
        return [
            self._score_what_dimension(node, filled_fields),
            self._score_which_dimension(node, filled_fields),
            self._score_if_then_dimension(node, filled_fields),
            self._score_modality_dimension(node, filled_fields),
            self._score_given_dimension(node, filled_fields),
            self._score_why_dimension(node, filled_fields)
        ]

    def _score_what_dimension(
        self,
        node: LogicTreeNode,
        filled_fields: Dict[str, Any]
    ) -> DimensionScore:
        """
        Score WHAT dimension: Facts, propositions, conclusions.

        Looks for matches between filled_fields values and content in node.what
        """
        matched_items = []
        total_items = len(node.what)

        if total_items == 0:
            # No WHAT content in this node
            return DimensionScore(
                dimension_name="WHAT",
                score=0.0,
                matched_items=[],
                total_items=0,
                reasoning="No WHAT content in node"
            )

        # Extract searchable terms from filled_fields
        search_terms = self._extract_search_terms(filled_fields)

        # Check each item in node.what for matches
        for item in node.what:
            if self._item_matches_terms(item, search_terms):
                matched_items.append(str(item))

        # Calculate score
        score = len(matched_items) / total_items if total_items > 0 else 0.0

        return DimensionScore(
            dimension_name="WHAT",
            score=score,
            matched_items=matched_items,
            total_items=total_items,
            reasoning=f"Matched {len(matched_items)}/{total_items} WHAT items"
        )

    def _score_which_dimension(
        self,
        node: LogicTreeNode,
        filled_fields: Dict[str, Any]
    ) -> DimensionScore:
        """
        Score WHICH dimension: Scope, entities, classifications.

        Looks for categorical matches (types, categories, classifications)
        """
        matched_items = []
        total_items = len(node.which)

        if total_items == 0:
            return DimensionScore(
                dimension_name="WHICH",
                score=0.0,
                matched_items=[],
                total_items=0,
                reasoning="No WHICH content in node"
            )

        search_terms = self._extract_search_terms(filled_fields)

        for item in node.which:
            if self._item_matches_terms(item, search_terms):
                matched_items.append(str(item))

        score = len(matched_items) / total_items if total_items > 0 else 0.0

        return DimensionScore(
            dimension_name="WHICH",
            score=score,
            matched_items=matched_items,
            total_items=total_items,
            reasoning=f"Matched {len(matched_items)}/{total_items} WHICH items"
        )

    def _score_if_then_dimension(
        self,
        node: LogicTreeNode,
        filled_fields: Dict[str, Any]
    ) -> DimensionScore:
        """
        Score IF-THEN dimension: Conditional logic, implications.

        Looks for conditional matches (if X then Y patterns)
        """
        matched_items = []
        total_items = len(node.if_then)

        if total_items == 0:
            return DimensionScore(
                dimension_name="IF_THEN",
                score=0.0,
                matched_items=[],
                total_items=0,
                reasoning="No IF-THEN content in node"
            )

        search_terms = self._extract_search_terms(filled_fields)

        for item in node.if_then:
            if self._item_matches_terms(item, search_terms):
                matched_items.append(str(item))

        score = len(matched_items) / total_items if total_items > 0 else 0.0

        return DimensionScore(
            dimension_name="IF_THEN",
            score=score,
            matched_items=matched_items,
            total_items=total_items,
            reasoning=f"Matched {len(matched_items)}/{total_items} IF-THEN items"
        )

    def _score_modality_dimension(
        self,
        node: LogicTreeNode,
        filled_fields: Dict[str, Any]
    ) -> DimensionScore:
        """
        Score MODALITY dimension: Obligations (MUST, MAY, CAN, CANNOT).

        Looks for requirement-related matches
        """
        matched_items = []
        total_items = len(node.modality)

        if total_items == 0:
            return DimensionScore(
                dimension_name="MODALITY",
                score=0.0,
                matched_items=[],
                total_items=0,
                reasoning="No MODALITY content in node"
            )

        search_terms = self._extract_search_terms(filled_fields)

        for item in node.modality:
            if self._item_matches_terms(item, search_terms):
                matched_items.append(str(item))

        score = len(matched_items) / total_items if total_items > 0 else 0.0

        return DimensionScore(
            dimension_name="MODALITY",
            score=score,
            matched_items=matched_items,
            total_items=total_items,
            reasoning=f"Matched {len(matched_items)}/{total_items} MODALITY items"
        )

    def _score_given_dimension(
        self,
        node: LogicTreeNode,
        filled_fields: Dict[str, Any]
    ) -> DimensionScore:
        """
        Score GIVEN dimension: Assumptions, premises, context.

        Looks for contextual matches
        """
        matched_items = []
        total_items = len(node.given)

        if total_items == 0:
            return DimensionScore(
                dimension_name="GIVEN",
                score=0.0,
                matched_items=[],
                total_items=0,
                reasoning="No GIVEN content in node"
            )

        search_terms = self._extract_search_terms(filled_fields)

        for item in node.given:
            if self._item_matches_terms(item, search_terms):
                matched_items.append(str(item))

        score = len(matched_items) / total_items if total_items > 0 else 0.0

        return DimensionScore(
            dimension_name="GIVEN",
            score=score,
            matched_items=matched_items,
            total_items=total_items,
            reasoning=f"Matched {len(matched_items)}/{total_items} GIVEN items"
        )

    def _score_why_dimension(
        self,
        node: LogicTreeNode,
        filled_fields: Dict[str, Any]
    ) -> DimensionScore:
        """
        Score WHY dimension: Reasoning, rationale, policy.

        Looks for policy/rationale matches
        """
        matched_items = []
        total_items = len(node.why)

        if total_items == 0:
            return DimensionScore(
                dimension_name="WHY",
                score=0.0,
                matched_items=[],
                total_items=0,
                reasoning="No WHY content in node"
            )

        search_terms = self._extract_search_terms(filled_fields)

        for item in node.why:
            if self._item_matches_terms(item, search_terms):
                matched_items.append(str(item))

        score = len(matched_items) / total_items if total_items > 0 else 0.0

        return DimensionScore(
            dimension_name="WHY",
            score=score,
            matched_items=matched_items,
            total_items=total_items,
            reasoning=f"Matched {len(matched_items)}/{total_items} WHY items"
        )

    def _extract_search_terms(self, filled_fields: Dict[str, Any]) -> Set[str]:
        """
        Extract search terms from filled_fields.

        Converts values to lowercase (unless case_sensitive),
        splits into words, returns set of terms.
        """
        terms = set()

        for key, value in filled_fields.items():
            # Convert value to string
            value_str = str(value)

            # Apply case sensitivity
            if not self.case_sensitive:
                value_str = value_str.lower()

            # Split into words and add to set
            words = value_str.split()
            terms.update(words)

        return terms

    def _item_matches_terms(
        self,
        item: Dict[str, Any],
        search_terms: Set[str]
    ) -> bool:
        """
        Check if an item (dict) contains any of the search terms.

        Searches all values in the item dict for term matches.
        """
        if not isinstance(item, dict):
            return False

        # Extract all text from item
        item_text = " ".join(str(v) for v in item.values())

        if not self.case_sensitive:
            item_text = item_text.lower()

        # Check if any search term appears in item text
        item_words = set(item_text.split())
        return len(search_terms & item_words) > 0

    def _calculate_overall_score(
        self,
        dimension_scores: List[DimensionScore]
    ) -> float:
        """
        Calculate weighted overall score from dimension scores.

        Applies dimension weights and returns final score (0.0-1.0).
        """
        total_score = 0.0

        for dim_score in dimension_scores:
            weight = self.weights.get(dim_score.dimension_name, 0.0)
            total_score += dim_score.score * weight

        return round(total_score, 4)

    def _calculate_confidence(
        self,
        dimension_scores: List[DimensionScore],
        filled_fields: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence based on:
        1. Number of dimensions with data
        2. Number of filled fields
        3. Match consistency across dimensions
        """
        # Count dimensions with content
        dimensions_with_content = sum(
            1 for ds in dimension_scores if ds.total_items > 0
        )

        # Base confidence on dimensions with content (max 6)
        dimension_confidence = dimensions_with_content / 6.0

        # Adjust based on number of filled fields (more fields = higher confidence)
        field_confidence = min(len(filled_fields) / 5.0, 1.0)  # Cap at 5 fields

        # Calculate match consistency (how consistent scores are across dimensions)
        non_zero_scores = [ds.score for ds in dimension_scores if ds.score > 0]
        if non_zero_scores:
            avg_score = sum(non_zero_scores) / len(non_zero_scores)
            consistency = 1.0 - (
                sum(abs(s - avg_score) for s in non_zero_scores) / len(non_zero_scores)
            )
        else:
            consistency = 0.0

        # Combine factors
        confidence = (
            0.5 * dimension_confidence +
            0.3 * field_confidence +
            0.2 * consistency
        )

        return round(min(confidence, 1.0), 4)

    def _identify_missing_fields(
        self,
        node: LogicTreeNode,
        filled_fields: Dict[str, Any]
    ) -> List[str]:
        """
        Identify fields that could improve match quality.

        Looks at node content to suggest additional fields user could provide.
        """
        # For now, return empty list
        # Future: analyze node content to suggest relevant fields
        return []

    def _generate_reasoning(
        self,
        dimension_scores: List[DimensionScore],
        overall_score: float
    ) -> str:
        """
        Generate human-readable explanation of match.

        Describes which dimensions matched and why.
        """
        # Find top contributing dimensions
        scored_dims = [(ds.dimension_name, ds.score, ds.reasoning)
                      for ds in dimension_scores if ds.score > 0]
        scored_dims.sort(key=lambda x: x[1], reverse=True)

        if not scored_dims:
            return f"Overall match: {overall_score:.2%} (no dimension matches)"

        # Build explanation
        parts = [f"Overall match: {overall_score:.2%}"]

        for dim_name, score, reasoning in scored_dims[:3]:  # Top 3
            parts.append(f"  - {dim_name}: {score:.2%} ({reasoning})")

        return "\n".join(parts)

    # Statistics methods
    def get_match_count(self) -> int:
        """Get total number of match operations performed"""
        return self._match_count

    def get_nodes_evaluated(self) -> int:
        """Get total number of nodes evaluated"""
        return self._total_nodes_evaluated

    def reset_statistics(self):
        """Reset statistics counters"""
        self._match_count = 0
        self._total_nodes_evaluated = 0
