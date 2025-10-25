"""
IMatchingEngine Interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .data_structures import LogicTreeNode, MatchResult


class IMatchingEngine(ABC):
    """Matching engine for finding relevant tree nodes"""
    
    @abstractmethod
    async def match(
        self,
        tree_nodes: List[LogicTreeNode],
        filled_fields: Dict[str, Any],
        threshold: float = 0.6
    ) -> List[MatchResult]:
        """
        Match filled fields to tree nodes.
        
        Args:
            tree_nodes: All available tree nodes
            filled_fields: User's filled information
            threshold: Minimum match score (0.0-1.0)
            
        Returns:
            List of MatchResult objects, sorted by match_score descending
        """
        pass
