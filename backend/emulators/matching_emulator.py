"""
Matching Engine Emulator for testing.

Provides deterministic matching results without complex NLP.
"""

from typing import List, Dict, Any
from backend.interfaces.matching import IMatchingEngine, MatchResult
from backend.interfaces.data_structures import LogicTreeNode


class MatchingEmulator(IMatchingEngine):
    """
    Simple matching emulator that uses keyword matching.
    
    Returns deterministic results for testing.
    """
    
    def __init__(self, threshold: float = 0.6):
        """Initialize matching emulator"""
        self._threshold = threshold
        self._match_count = 0
    
    async def match(
        self,
        tree_nodes: List[LogicTreeNode],
        filled_fields: Dict[str, Any],
        threshold: float = 0.6
    ) -> List[MatchResult]:
        """
        Match filled fields to tree nodes (IMatchingEngine interface method).
        
        Args:
            tree_nodes: All available tree nodes
            filled_fields: User's filled information
            threshold: Minimum match score (0.0-1.0)
            
        Returns:
            List of MatchResult objects, sorted by match_score descending
        """
        self._match_count += 1
        results = []
        
        # Convert filled_fields to searchable text
        search_text = " ".join(str(v).lower() for v in filled_fields.values())
        search_words = set(search_text.split())
        
        for node in tree_nodes:
            # Extract searchable content from node's 6 dimensions
            node_content = []
            
            # Extract from WHAT dimension
            for item in node.what:
                if isinstance(item, dict):
                    node_content.extend([str(v) for v in item.values()])
            
            # Extract from WHICH dimension
            for item in node.which:
                if isinstance(item, dict):
                    node_content.extend([str(v) for v in item.values()])
            
            # Extract from other dimensions
            for dimension in [node.if_then, node.modality, node.given, node.why]:
                for item in dimension:
                    if isinstance(item, dict):
                        node_content.extend([str(v) for v in item.values()])
            
            # Calculate match score
            node_text = " ".join(node_content).lower()
            node_words = set(node_text.split())
            
            overlap = len(search_words & node_words)
            total = len(search_words | node_words)
            match_score = overlap / total if total > 0 else 0.0
            
            if match_score >= threshold:
                results.append(MatchResult(
                    node_id=node.node_id,
                    node=node,
                    match_score=match_score,
                    matched_fields=filled_fields,
                    missing_fields=[],
                    confidence=match_score,
                    reasoning=f"Keyword overlap: {overlap} words matched"
                ))
        
        # Sort by match_score descending
        results.sort(key=lambda x: x.match_score, reverse=True)
        return results
    
    async def find_matches(
        self,
        user_input: str,
        candidates: List[LogicTreeNode],
        top_k: int = 5
    ) -> List[MatchResult]:
        """
        Find matching nodes using simple keyword matching.
        
        Returns deterministic results based on keyword overlap.
        """
        # Convert user_input to filled_fields format for match() method
        filled_fields = {"user_query": user_input}
        
        # Use the match() method
        results = await self.match(candidates, filled_fields, self._threshold)
        
        # Return top_k results
        return results[:top_k]
    
    async def health_check(self) -> bool:
        """Check emulator health"""
        return True
    
    def get_match_count(self) -> int:
        """Get number of match operations performed"""
        return self._match_count
    
    def reset(self):
        """Reset emulator state"""
        self._match_count = 0
