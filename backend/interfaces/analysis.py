"""
IAnalysisEngine Interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .data_structures import LogicTreeNode


class IAnalysisEngine(ABC):
    """Analysis engine orchestration"""
    
    @abstractmethod
    async def analyze(
        self,
        module: 'ILegalModule',
        filled_fields: Dict[str, Any],
        enhance_with_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Orchestrate complete analysis.
        
        Returns:
            Comprehensive analysis result
        """
        pass
