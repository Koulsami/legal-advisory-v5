"""
ICalculator Interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .data_structures import MatchResult


class ICalculator(ABC):
    """Module-specific calculator"""
    
    @abstractmethod
    async def calculate(
        self,
        matched_nodes: List[MatchResult],
        filled_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform specialized calculation.
        
        Must be 100% accurate and deterministic.
        """
        pass
